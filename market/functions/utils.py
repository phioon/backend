from django.utils import encoding
from operator import itemgetter
from datetime import datetime
import time
import pytz
import unicodedata
import re


# general
def remove_special_chars(string):
    string = str(string)
    string = unicodedata.normalize('NFKD', string)
    string = string.encode('ASCII', 'ignore')
    return encoding.force_str(string)


def get_asset_datetime(asset_symbol, datetime):
    asset_datetime = str(asset_symbol + '_' + re.sub("[^0-9]", "", datetime))
    return asset_datetime


# Time
def convert_epoch_to_timestamp(epoch):
    while len(str(epoch)) > 10:
        # It must be in seconds. In case it is miliseconds or nanoseconds, keep dividing
        epoch = epoch / 1000

    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(epoch))
    return timestamp


def convert_naive_to_utc(strDatetime, tz):
    local = pytz.timezone(tz)
    naive = datetime.strptime(strDatetime, '%Y-%m-%d %H:%M:%S')
    local_dt = local.localize(naive, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)

    return utc_dt


# data structures
def get_field_as_key(obj_list, key_field):
    dictionary = {}
    for obj in obj_list:
        if obj[key_field] not in dictionary:
            dictionary[obj[key_field]] = []
        dictionary[obj[key_field]].append(obj)

    return dictionary


def get_field_as_unique_key(obj_list, key_field):
    dictionary = {}
    for obj in obj_list:
        dictionary[obj[key_field]] = obj

    return dictionary


def has_empty_fields(obj):
    for value in obj.values():
        if not value:
            return True
    return False


def retrieve_obj_from_obj_list(obj_list, key_field, value):
    for obj in obj_list:
        if obj[key_field] == value:
            return obj


def order_by_asc(obj_list, field):
    obj_list = sorted(obj_list, key=itemgetter(field))
    return obj_list


def order_by_desc(obj_list, field):
    obj_list = sorted(obj_list, key=itemgetter(field), reverse=True)
    return obj_list


# technical analysis
def rate_of_change(v1, v2):
    delta = 0
    if v2 and v1:
        delta = v2 - v1

    return percentage(delta, v1)


def percentage(numerator, denominator, decimals=2, if_denominator_is_zero=0):
    if denominator and denominator > 0:
        return round(numerator / denominator * 100, decimals)
    else:
        return if_denominator_is_zero


def division(numerator, denominator, decimals=2, if_denominator_is_zero=0):
    if denominator > 0:
        return round(numerator / denominator, decimals)
    else:
        return if_denominator_is_zero


def multiplication(v1, v2, decimals):
    return round(v1 * v2, decimals)


def risk_reward(gain_percent, loss_percent):
    return division(gain_percent, loss_percent)


def gain_percent_buy(max_price, target):
    delta = target - max_price
    return percentage(delta, max_price)


def gain_percent_sell(max_price, target):
    delta = max_price - target
    return percentage(delta, max_price)


def stop_loss_buy(max_price, stop_loss):
    delta = max_price - stop_loss
    return percentage(delta, max_price)


def stop_loss_sell(max_price, stop_loss):
    delta = stop_loss - max_price
    return percentage(delta, max_price)


def fibonacci_projection(type, highList, lowList, projection_percentage,
                         min_periods_to_consider=17, inc_interval=4, max_periods_to_consider=72):
    # highList and lowList are ordered by ASCENDENT
    # So, the more recent data is in the last position

    p1 = p2 = p3 = None
    fibo_projection = {}

    lastIndex = len(highList) - 1
    periods = min_periods_to_consider

    keepLooking = True
    high_today = highList[lastIndex]
    low_today = lowList[lastIndex]
    ini_highest = max(highList[lastIndex - periods:])
    ini_lowest = min(lowList[lastIndex - periods:])

    while keepLooking:
        highest = max(highList[lastIndex - periods:])
        lowest = min(lowList[lastIndex - periods:])

        if type == 'buy':
            # BUY
            if p1 is None:
                # It's the first loop run
                p1 = lowest
                periods += inc_interval
                continue

            if (lowest < p1 or
                    lowest >= ini_lowest or
                    high_today >= ini_highest):
                # lowest < p1:                  A new low has been found
                # lowest >= ini_lowest:         Lowest value is still GTE to the first low found (17 periods)
                # high_today <= ini_highest:    Today's high value is still LTE to the first high found (17 periods)
                # LTE:                          Lesser Than or Equal
                # GTE:                          Greater Than or Equal

                p1 = lowest
                periods += inc_interval
            else:
                keepLooking = False

        else:
            # SELL
            if p1 is None:
                # It's the first loop run
                p1 = highest
                periods += inc_interval
                continue

            if (highest > p1 or
                    highest <= ini_highest or
                    low_today <= ini_lowest):
                # highest > p1:                 A new high has been found
                # highest <= ini_highest:       Highest value is still LTE to the first high found (17 periods)
                # low_today <= ini_lowest:      Today's low value is still GTE to the first low found (17 periods)
                # LTE:                          Lesser Than or Equal
                # GTE:                          Greater Than or Equal

                p1 = highest
                periods += inc_interval
            else:
                keepLooking = False

        if periods >= max_periods_to_consider:
            # Try to draw projection based on up to 72 periods (default).
            keepLooking = False

    # Considering only positions after p1 (From p1 to lastIndex)
    highList = highList[lastIndex - periods: lastIndex + 1]
    lowList = lowList[lastIndex - periods: lastIndex + 1]

    p2Index = None

    if type == 'buy':
        # BUY
        for x in range(len(highList)):
            if p2 is None or highList[x] >= p2:
                p2 = highList[x]
                p2Index = x

        p3 = min(lowList[p2Index:])

        wave_1 = p2 - p1
        retraction = p2 - p3
        projection = round(p3 + (wave_1 * projection_percentage), 2)
    else:
        # SELL
        for x in range(len(lowList)):
            if p2 is None or lowList[x] <= p2:
                p2 = lowList[x]
                p2Index = x

        p3 = max(highList[p2Index:])

        wave_1 = p1 - p2
        retraction = p3 - p2
        projection = p3 - (wave_1 * projection_percentage)

    fibo_projection['periods_needed'] = periods
    fibo_projection['p1'] = round(p1, 2)
    fibo_projection['p2'] = round(p2, 2)
    fibo_projection['p3'] = round(p3, 2)
    fibo_projection['wave_1'] = round(wave_1, 2)
    fibo_projection['retraction'] = round(retraction, 2)
    fibo_projection['pct_retraction'] = percentage(retraction, wave_1, decimals=1)
    fibo_projection['projection'] = round(projection, 2)

    fibo_projection = review_fibo_projection(fibo_projection)

    return fibo_projection


def review_fibo_projection(fibo_projection):
    if fibo_projection['projection'] <= 0:
        # Don't let projection be lesser than 0.
        fibo_projection['projection'] = 1.5

    return fibo_projection
