from django.utils import encoding
import unicodedata


def remove_special_chars(string):
    string = unicodedata.normalize('NFKD', string)
    string = string.encode('ASCII', 'ignore')
    return encoding.force_str(string)


def percentage(numerator, denominator, decimals=2, if_denominator_is_zero=0):
    if denominator > 0:
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


def fibonacciProjection(type, highList, lowList, projection_percentage, max_periods_to_consider=72):
    # highList and lowList are ordered by ASCENDENT
    # So, the more recent data is in the last position

    p1 = p2 = p3 = None
    fiboProjection = {}

    lastIndex = len(highList) - 1
    periods = 17
    inc_interval = 4

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
    highList = highList[lastIndex - periods: lastIndex - 1]
    lowList = lowList[lastIndex - periods: lastIndex - 1]

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

    fiboProjection['periods_needed'] = periods
    fiboProjection['p1'] = round(p1, 2)
    fiboProjection['p2'] = round(p2, 2)
    fiboProjection['p3'] = round(p3, 2)
    fiboProjection['wave_1'] = round(wave_1, 2)
    fiboProjection['retraction'] = round(retraction, 2)
    fiboProjection['pct_retraction'] = percentage(retraction, wave_1, decimals=1)
    fiboProjection['projection'] = round(projection, 2)

    # print(' .. ini_lowest: %s ' % ini_lowest)
    # print(' .. ini_highest: %s ' % ini_highest)
    # print(' .. periods: %s ' % periods)
    # print(' .. p1: %s ' % p1)
    # print(' .. p2: %s ' % p2)
    # print(' .. p3: %s ' % p3)

    return fiboProjection
