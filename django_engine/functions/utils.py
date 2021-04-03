from django.utils import encoding
from operator import itemgetter
from datetime import datetime
import numpy as np
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


# raw data manager
def get_ema_list(df, span):
    df = df.ewm(span=span, adjust=False).mean()
    df = df.fillna(0)
    df[0:span] = None
    df = df.round(2)

    df = df.where(df.notnull(), None)

    result = df.values.tolist()
    return result


def get_sma_list(df, span):
    df = df.rolling(span).mean()
    df = df.fillna(0)
    df[0:span] = None
    df = df.round(2)

    df = df.where(df.notnull(), None)

    result = df.values.tolist()
    return result


def get_roc_list(df, span):
    df = df.where(df.notnull(), np.nan)
    df = df.pct_change(periods=span)
    df[0:span*2] = None

    df = df.fillna(0)
    df = df.round(4)
    df = df.where(df.notnull(), None)

    result = df.values.tolist()
    return result


# technical analysis
def distance_percent(v1, v2):
    distance = v1 - v2
    distance = distance / v1

    return abs(distance)


def is_near(v1, v2, threshold):
    distance = distance_percent(v1, v2)

    return distance <= threshold


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


def get_projection_pct(context, retracement_pct):
    if context == 'long':
        if retracement_pct >= 90:
            return 1.5
        elif retracement_pct >= 55:
            return 0.98
        else:
            return 0.8
    elif context == 'short':
        if retracement_pct >= 90:
            return 0.98
        elif retracement_pct >= 55:
            return 0.8
        else:
            return 0.61


def fibonacci_projection(type, highs, lows, projection_percentage='auto',
                         min_periods_to_consider=17, inc_interval=4, max_periods_to_consider=72):
    # highList and lowList are ordered by ASCENDENT
    # So, the more recent data is in the last position

    p1 = p2 = p3 = None
    fibonacci_obj = {}

    last_index = len(highs) - 1
    periods = min_periods_to_consider

    keep_looking = True
    high_today = highs[last_index]
    low_today = lows[last_index]
    ini_highest = max(highs[last_index - periods:])
    ini_lowest = min(lows[last_index - periods:])

    while keep_looking:
        highest = max(highs[last_index - periods:])
        lowest = min(lows[last_index - periods:])

        if p1 is None:
            # It's the first loop run
            p1 = lowest
            periods += inc_interval
            continue

        if type == 'long':
            # LONG
            if (lowest < p1 or
                    lowest >= ini_lowest or
                    high_today >= ini_highest):
                # lowest < p1:                  A new low has been found
                # lowest >= ini_lowest:         Lowest value is still GTE to the first low found (17 periods)
                # high_today >= ini_highest:    Today's high is still GTE to the first high found (17 periods)

                p1 = lowest
                periods += inc_interval
            else:
                keep_looking = False

        else:
            # SHORT
            if (highest > p1 or
                    highest <= ini_highest or
                    low_today <= ini_lowest):
                # highest > p1:                 A new high has been found
                # highest <= ini_highest:       Highest value is still LTE to the first high found (17 periods)
                # low_today <= ini_lowest:      Today's low is still LTE to the first low found (17 periods)

                p1 = highest
                periods += inc_interval
            else:
                keep_looking = False

        if periods >= max_periods_to_consider:
            # Try to draw projection based on up to 72 periods (default).
            keep_looking = False

    # Considering only positions after p1
    highs = highs[last_index - periods:]
    lows = lows[last_index - periods:]

    p2Index = None

    if type == 'long':
        # BUY
        for x in range(len(highs)):
            if p2 is None or highs[x] >= p2:
                p2 = highs[x]
                p2Index = x

        p3 = min(lows[p2Index:])

        first_wave = p2 - p1
        retracement = p2 - p3
        retracement_pct = percentage(retracement, first_wave, decimals=1)

        if projection_percentage == 'auto':
            projection_percentage = get_projection_pct(context=type, retracement_pct=retracement_pct)
        projection = round(p3 + (first_wave * projection_percentage), 2)
    else:
        # SELL
        for x in range(len(lows)):
            if p2 is None or lows[x] <= p2:
                p2 = lows[x]
                p2Index = x

        p3 = max(highs[p2Index:])

        first_wave = p1 - p2
        retracement = p3 - p2
        retracement_pct = percentage(retracement, first_wave, decimals=1)

        if projection_percentage == 'auto':
            projection_percentage = get_projection_pct(context=type, retracement_pct=retracement_pct)
        projection = p3 - (first_wave * projection_percentage)

    fibonacci_obj['periods_needed'] = periods
    fibonacci_obj['p1'] = round(p1, 2)
    fibonacci_obj['p2'] = round(p2, 2)
    fibonacci_obj['p3'] = round(p3, 2)
    fibonacci_obj['first_wave'] = round(first_wave, 2)
    fibonacci_obj['retracement'] = round(retracement, 2)
    fibonacci_obj['retracement_pct'] = percentage(retracement, first_wave, decimals=1)
    fibonacci_obj['projection'] = round(projection, 2)

    return fibonacci_obj
