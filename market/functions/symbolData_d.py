from django_engine import settings
from market import managers
from market.functions import sma, ema, roc
from market.functions import utils as phioon_utils
import pandas as pd


def updateRaw(symbol, last_x_rows):
    from market.models import Asset, D_raw

    provider_manager = managers.ProviderManager()
    data = provider_manager.get_eod_data(asset_symbol=symbol, last_x_periods=last_x_rows)

    d_raw = D_raw()
    objs = []

    for obj in data:
        objs.append(D_raw(asset_datetime=phioon_utils.get_asset_datetime(symbol, obj['datetime']),
                    asset_symbol=Asset.objects.get(asset_symbol=symbol),
                    d_datetime=obj['datetime'],
                    d_open=obj['open'],
                    d_high=obj['high'],
                    d_low=obj['low'],
                    d_close=obj['close'],
                    d_volume=obj['volume']))

    if last_x_rows > 0:
        d_raw.updateOrCreateObjs(objs[:last_x_rows])  # First X Descending
    else:
        d_raw.bulk_create(objs)


def updatePvpc(symbol, lastXrows):  # For each Asset
    from market.models import D_raw, D_pvpc

    d_raw = D_raw.objects.only('asset_datetime')
    pvpc = D_pvpc()
    objs = []

    # Ordered by 'd_datetime' DESCENDENT
    adtList = list(D_raw.objects.filter(asset_symbol=symbol)
                   .exclude(d_close=0)
                   .values_list('asset_datetime', flat=True)
                   .order_by('-d_datetime'))
    highList = list(D_raw.objects.filter(asset_symbol=symbol)
                    .exclude(d_close=0)
                    .values_list('d_high', flat=True)
                    .order_by('-d_datetime'))
    lowList = list(D_raw.objects.filter(asset_symbol=symbol)
                   .exclude(d_close=0)
                   .values_list('d_low', flat=True)
                   .order_by('-d_datetime'))

    for x in range(len(adtList)):
        adt = adtList[x]
        pv72 = pv305 = pv610 = pv1292 = None
        pc72 = pc305 = pc610 = pc1292 = None

        if x + 1292 < len(adtList):
            high1292 = max(highList[x: x + 1292])
            low1292 = min(lowList[x: x + 1292])
            pv1292 = round(((high1292 - low1292) * .786) + low1292, 2)
            pc1292 = round(((high1292 - low1292) * .214) + low1292, 2)

        if x + 610 < len(adtList):
            high610 = max(highList[x: x + 610])
            low610 = min(lowList[x: x + 610])
            pv610 = round(((high610 - low610) * .786) + low610, 2)
            pc610 = round(((high610 - low610) * .214) + low610, 2)

        if x + 305 < len(adtList):
            high305 = max(highList[x: x + 305])
            low305 = min(lowList[x: x + 305])
            pv305 = round(((high305 - low305) * .786) + low305, 2)
            pc305 = round(((high305 - low305) * .214) + low305, 2)

        if x + 72 < len(adtList):
            high72 = max(highList[x: x + 72])
            low72 = min(lowList[x: x + 72])
            pv72 = round(((high72 - low72) * .786) + low72, 2)
            pc72 = round(((high72 - low72) * .214) + low72, 2)

        obj = D_pvpc(d_raw=d_raw.get(asset_datetime=adt),
                     asset_datetime=adt,
                     d_pv72=pv72,
                     d_pv305=pv305,
                     d_pv1292=pv1292,
                     d_pc72=pc72,
                     d_pc305=pc305,
                     d_pc1292=pc1292)
        objs.append(obj)

    if lastXrows > 0:
        pvpc.updateOrCreateObjs(objs[:lastXrows])  # First X Descending
    else:
        pvpc.bulk_create(objs)


def updateSma(symbol, lastXrows):
    from market.models import D_raw, D_sma

    d_raw = D_raw.objects.only('asset_datetime')
    dSma = D_sma()
    objs = []

    # Ordered by 'd_datetime' ASCENDENT
    adtList = list(D_raw.objects.filter(asset_symbol=symbol)
                   .exclude(d_close=0)
                   .values_list('asset_datetime', flat=True)
                   .order_by('d_datetime'))
    closeList = list(D_raw.objects.filter(asset_symbol=symbol)
                     .exclude(d_close=0)
                     .values_list('d_close', flat=True)
                     .order_by('d_datetime'))

    df = pd.DataFrame(closeList)[0]
    sma_close7 = sma.getSmaList(df, 7)
    sma_close10 = sma.getSmaList(df, 10)
    sma_close20 = sma.getSmaList(df, 20)
    sma_close21 = sma.getSmaList(df, 21)
    sma_close30 = sma.getSmaList(df, 30)
    sma_close50 = sma.getSmaList(df, 50)
    sma_close55 = sma.getSmaList(df, 55)
    sma_close100 = sma.getSmaList(df, 100)
    sma_close200 = sma.getSmaList(df, 200)

    for x in range(len(adtList)):
        adt = adtList[x]
        sma7 = sma_close7[x]
        sma10 = sma_close10[x]
        sma20 = sma_close20[x]
        sma21 = sma_close21[x]
        sma30 = sma_close30[x]
        sma50 = sma_close50[x]
        sma55 = sma_close55[x]
        sma100 = sma_close100[x]
        sma200 = sma_close200[x]

        obj = D_sma(d_raw=d_raw.get(asset_datetime=adt),
                    asset_datetime=adt,
                    d_sma_close7=sma7,
                    d_sma_close10=sma10,
                    d_sma_close20=sma20,
                    d_sma_close21=sma21,
                    d_sma_close30=sma30,
                    d_sma_close50=sma50,
                    d_sma_close55=sma55,
                    d_sma_close100=sma100,
                    d_sma_close200=sma200)
        objs.append(obj)

    if lastXrows > 0:
        dSma.updateOrCreateObjs(objs[-lastXrows:])  # First X Ascending
    else:
        dSma.bulk_create(objs)


def updateEma(symbol, lastXrows):
    from market.models import D_raw, D_ema

    d_raw = D_raw.objects.only('asset_datetime')
    dEma = D_ema()
    objs = []

    # Ordered by 'd_datetime' ASCENDENT
    adtList = list(D_raw.objects.filter(asset_symbol=symbol)
                   .exclude(d_close=0)
                   .values_list('asset_datetime', flat=True)
                   .order_by('d_datetime'))
    closeList = list(D_raw.objects.filter(asset_symbol=symbol)
                     .exclude(d_close=0)
                     .values_list('d_close', flat=True)
                     .order_by('d_datetime'))

    df = pd.DataFrame(closeList)[0]
    ema_close8 = ema.getEmaList(df, 8)
    ema_close9 = ema.getEmaList(df, 9)
    ema_close17 = ema.getEmaList(df, 17)
    ema_close34 = ema.getEmaList(df, 34)
    ema_close50 = ema.getEmaList(df, 50)
    ema_close72 = ema.getEmaList(df, 72)
    ema_close144 = ema.getEmaList(df, 144)
    ema_close200 = ema.getEmaList(df, 200)
    ema_close305 = ema.getEmaList(df, 305)
    ema_close610 = ema.getEmaList(df, 610)
    ema_close1292 = ema.getEmaList(df, 1292)
    ema_close2584 = ema.getEmaList(df, 2584)

    for x in range(len(adtList)):
        adt = adtList[x]
        ema8 = ema_close8[x]
        ema9 = ema_close9[x]
        ema17 = ema_close17[x]
        ema34 = ema_close34[x]
        ema50 = ema_close50[x]
        ema72 = ema_close72[x]
        ema144 = ema_close144[x]
        ema200 = ema_close200[x]
        ema305 = ema_close305[x]
        ema610 = ema_close610[x]
        ema1292 = ema_close1292[x]
        ema2584 = ema_close2584[x]

        obj = D_ema(d_raw=d_raw.get(asset_datetime=adt),
                    asset_datetime=adt,
                    d_ema_close8=ema8,
                    d_ema_close9=ema9,
                    d_ema_close17=ema17,
                    d_ema_close34=ema34,
                    d_ema_close50=ema50,
                    d_ema_close72=ema72,
                    d_ema_close144=ema144,
                    d_ema_close200=ema200,
                    d_ema_close305=ema305,
                    d_ema_close610=ema610,
                    d_ema_close1292=ema1292,
                    d_ema_close2584=ema2584)
        objs.append(obj)

    if lastXrows > 0:
        dEma.updateOrCreateObjs(objs[-lastXrows:])  # First X Ascending
    else:
        dEma.bulk_create(objs)


def updateRoc(symbol, lastXrows):
    from market.models import Logging, D_raw, D_roc, D_sma, D_ema

    l = Logging()
    d_raw = D_raw.objects.only('asset_datetime')
    dRoc = D_roc()
    objs = []

    # Ordered by 'd_datetime' ASCENDENT
    adtList = list(D_raw.objects.filter(asset_symbol=symbol)
                   .exclude(d_close=0)
                   .values_list('asset_datetime', flat=True)
                   .order_by('d_datetime'))
    closeSmaList = list(D_sma.objects.filter(d_raw_id__asset_symbol__exact=symbol)
                        .exclude(d_raw_id__d_close=0)
                        .values_list('d_sma_close7', 'd_sma_close10', 'd_sma_close20', 'd_sma_close21', 'd_sma_close30',
                                     'd_sma_close50', 'd_sma_close55', 'd_sma_close100', 'd_sma_close200')
                        .order_by('asset_datetime'))
    closeEmaList = list(D_ema.objects.filter(d_raw_id__asset_symbol__exact=symbol)
                        .exclude(d_raw_id__d_close=0)
                        .values_list('d_ema_close8', 'd_ema_close9', 'd_ema_close17', 'd_ema_close34', 'd_ema_close50',
                                     'd_ema_close72', 'd_ema_close144', 'd_ema_close200', 'd_ema_close305',
                                     'd_ema_close610', 'd_ema_close1292', 'd_ema_close2584')
                        .order_by('asset_datetime'))

    if len(adtList) != len(closeEmaList):
        l.log_into_db(level='error',
                      context='updateRoc',
                      message='[%s] Not ready: len[adtList] = %i and len(closeEmaList) = %i'
                            % (symbol, len(adtList), len(closeEmaList)))
        return

    # EMA
    df = pd.DataFrame(closeEmaList)[:]
    roc_emaClose8 = roc.getRocList(df[0], 8 - 1)  # Related to # periods behind
    roc_emaClose9 = roc.getRocList(df[1], 9 - 1)  # Related to # periods behind
    roc_emaClose17 = roc.getRocList(df[2], 17 - 1)  # Related to # periods behind
    roc_emaClose34 = roc.getRocList(df[3], 34 - 1)  # Related to # periods behind
    roc_emaClose50 = roc.getRocList(df[4], 50 - 1)  # Related to # periods behind
    roc_emaClose72 = roc.getRocList(df[5], 72 - 1)  # Related to # periods behind
    roc_emaClose144 = roc.getRocList(df[6], 144 - 1)  # Related to # periods behind
    roc_emaClose200 = roc.getRocList(df[7], 200 - 1)  # Related to # periods behind
    roc_emaClose305 = roc.getRocList(df[8], 305 - 1)  # Related to # periods behind
    roc_emaClose610 = roc.getRocList(df[9], 610 - 1)  # Related to # periods behind
    roc_emaClose1292 = roc.getRocList(df[10], 1292 - 1)  # Related to # periods behind
    roc_emaClose2584 = roc.getRocList(df[11], 2584 - 1)  # Related to # periods behind

    # SMA
    df = pd.DataFrame(closeSmaList)[:]
    roc_smaClose7 = roc.getRocList(df[0], 7 - 1)  # Related to # periods behind
    roc_smaClose10 = roc.getRocList(df[1], 10 - 1)  # Related to # periods behind
    roc_smaClose20 = roc.getRocList(df[2], 20 - 1)  # Related to # periods behind
    roc_smaClose21 = roc.getRocList(df[3], 21 - 1)  # Related to # periods behind
    roc_smaClose30 = roc.getRocList(df[4], 30 - 1)  # Related to # periods behind
    roc_smaClose50 = roc.getRocList(df[4], 50 - 1)  # Related to # periods behind
    roc_smaClose55 = roc.getRocList(df[4], 55 - 1)  # Related to # periods behind
    roc_smaClose100 = roc.getRocList(df[5], 100 - 1)  # Related to # periods behind
    roc_smaClose200 = roc.getRocList(df[7], 200 - 1)  # Related to # periods behind

    for x in range(len(adtList)):
        adt = adtList[x]

        rocEma8 = roc_emaClose8[x]
        rocEma9 = roc_emaClose9[x]
        rocEma17 = roc_emaClose17[x]
        rocEma34 = roc_emaClose34[x]
        rocEma50 = roc_emaClose50[x]
        rocEma72 = roc_emaClose72[x]
        rocEma144 = roc_emaClose144[x]
        rocEma200 = roc_emaClose200[x]
        rocEma305 = roc_emaClose305[x]
        rocEma610 = roc_emaClose610[x]
        rocEma1292 = roc_emaClose1292[x]
        rocEma2584 = roc_emaClose2584[x]

        rocSma7 = roc_smaClose7[x]
        rocSma10 = roc_smaClose10[x]
        rocSma20 = roc_smaClose20[x]
        rocSma21 = roc_smaClose21[x]
        rocSma30 = roc_smaClose30[x]
        rocSma50 = roc_smaClose50[x]
        rocSma55 = roc_smaClose55[x]
        rocSma100 = roc_smaClose100[x]
        rocSma200 = roc_smaClose200[x]

        obj = D_roc(d_raw=d_raw.get(asset_datetime=adt),
                    asset_datetime=adt,

                    d_roc_smaclose7=rocSma7,
                    d_roc_smaclose10=rocSma10,
                    d_roc_smaclose20=rocSma20,
                    d_roc_smaclose21=rocSma21,
                    d_roc_smaclose30=rocSma30,
                    d_roc_smaclose50=rocSma50,
                    d_roc_smaclose55=rocSma55,
                    d_roc_smaclose100=rocSma100,
                    d_roc_smaclose200=rocSma200,

                    d_roc_emaclose8=rocEma8,
                    d_roc_emaclose9=rocEma9,
                    d_roc_emaclose17=rocEma17,
                    d_roc_emaclose34=rocEma34,
                    d_roc_emaclose50=rocEma50,
                    d_roc_emaclose72=rocEma72,
                    d_roc_emaclose144=rocEma144,
                    d_roc_emaclose200=rocEma200,
                    d_roc_emaclose305=rocEma305,
                    d_roc_emaclose610=rocEma610,
                    d_roc_emaclose1292=rocEma1292,
                    d_roc_emaclose2584=rocEma2584)
        objs.append(obj)

    if lastXrows > 0:
        dRoc.updateOrCreateObjs(objs[-lastXrows:])  # Last X Ascending
    else:
        dRoc.bulk_create(objs)


def updateVar(symbol, lastXrows):
    from market.models import Logging, D_raw, D_var, D_ema

    l = Logging()
    d_raw = D_raw.objects.only('asset_datetime')
    dVar = D_var()
    objs = []

    # Ordered by 'd_datetime' ASCENDENT
    adtList = list(D_raw.objects.filter(asset_symbol=symbol)
                   .exclude(d_close=0)
                   .values_list('asset_datetime', flat=True)
                   .order_by('d_datetime'))
    closeEmaList = list(D_ema.objects.filter(d_raw_id__asset_symbol__exact=symbol)
                        .exclude(d_raw_id__d_close=0)
                        .values_list('d_ema_close17', 'd_ema_close34', 'd_ema_close72',
                                     'd_ema_close144', 'd_ema_close305', 'd_ema_close610')
                        .order_by('asset_datetime'))

    if len(adtList) != len(closeEmaList):
        l.log_into_db(level='error',
                      context='updateVar',
                      message='[%s] Not ready: len[adtList] = %i and len(closeEmaList) = %i'
                            % (symbol, len(adtList), len(closeEmaList)))
        return

    for x in range(len(adtList)):
        var_emaClose1734 = var_emaClose3472 = var_emaClose72144 = var_emaClose144305 = var_emaClose305610 = None

        emaClose17 = closeEmaList[x][0]
        emaClose34 = closeEmaList[x][1]
        emaClose72 = closeEmaList[x][2]
        emaClose144 = closeEmaList[x][3]
        emaClose305 = closeEmaList[x][4]
        emaClose610 = closeEmaList[x][5]

        if emaClose17 and emaClose34:
            var_emaClose1734 = phioon_utils.percentage((emaClose17 - emaClose34),
                                                       emaClose17,
                                                       decimals=3,
                                                       if_denominator_is_zero=0)
        if emaClose34 and emaClose72:
            var_emaClose3472 = phioon_utils.percentage((emaClose34 - emaClose72),
                                                       emaClose34,
                                                       decimals=3,
                                                       if_denominator_is_zero=0)
        if emaClose72 and emaClose144:
            var_emaClose72144 = phioon_utils.percentage((emaClose72 - emaClose144),
                                                        emaClose72,
                                                        decimals=3,
                                                        if_denominator_is_zero=0)
        if emaClose144 and emaClose305:
            var_emaClose144305 = phioon_utils.percentage((emaClose144 - emaClose305),
                                                         emaClose144,
                                                         decimals=3,
                                                         if_denominator_is_zero=0)
        if emaClose305 and emaClose610:
            var_emaClose305610 = phioon_utils.percentage((emaClose305 - emaClose610),
                                                         emaClose305,
                                                         decimals=3,
                                                         if_denominator_is_zero=0)

        adt = adtList[x]

        obj = D_var(d_raw=d_raw.get(asset_datetime=adt),
                    asset_datetime=adt,
                    d_var_emaclose1734=var_emaClose1734,
                    d_var_emaclose3472=var_emaClose3472,
                    d_var_emaclose72144=var_emaClose72144,
                    d_var_emaclose144305=var_emaClose144305,
                    d_var_emaclose305610=var_emaClose305610)
        objs.append(obj)

    if lastXrows > 0:
        dVar.updateOrCreateObjs(objs[-lastXrows:])  # Last X Ascending
    else:
        dVar.bulk_create(objs)


def updateTechnicalCondition(symbol, lastXrows):
    from market.models import Logging, TechnicalCondition, D_technicalCondition, D_raw, D_pvpc, D_ema, D_var

    l = Logging()
    d_tc = D_technicalCondition()
    d_raw = D_raw.objects.only('asset_datetime')
    objs = []

    # Ordered by 'd_datetime' ASCENDENT
    adtList = list(D_raw.objects.filter(asset_symbol=symbol)
                   .exclude(d_close=0)
                   .values_list('asset_datetime', flat=True)
                   .order_by('d_datetime'))
    closeList = list(D_raw.objects.filter(asset_symbol=symbol)
                     .exclude(d_close=0)
                     .values_list('d_close', flat=True)
                     .order_by('d_datetime'))
    lowList = list(D_raw.objects.filter(asset_symbol=symbol)
                   .exclude(d_close=0)
                   .values_list('d_low', flat=True)
                   .order_by('d_datetime'))
    highList = list(D_raw.objects.filter(asset_symbol=symbol)
                    .exclude(d_close=0)
                    .values_list('d_high', flat=True)
                    .order_by('d_datetime'))

    # Respect the order: [0]=pv72, [1]=pv305, [2]=pv1292...
    pvList = list(D_pvpc.objects.filter(d_raw_id__asset_symbol__exact=symbol)
                  .exclude(d_raw_id__d_close=0)
                  .values_list('d_pv72', 'd_pv305', 'd_pv1292')
                  .order_by('asset_datetime'))
    pcList = list(D_pvpc.objects.filter(d_raw_id__asset_symbol__exact=symbol)
                  .exclude(d_raw_id__d_close=0)
                  .values_list('d_pc72', 'd_pc305', 'd_pc1292')
                  .order_by('asset_datetime'))

    # Respect the order: [0]=d_ema_close34, [1]=d_ema_close144...
    closeEmaList = list(D_ema.objects.filter(d_raw_id__asset_symbol__exact=symbol)
                        .exclude(d_raw_id__d_close=0)
                        .values_list('d_ema_close34', 'd_ema_close144', 'd_ema_close610')
                        .order_by('asset_datetime'))

    # Respect the order: [0]=varEma34144, [1]=varEma144610
    varList = list(D_var.objects.filter(d_raw_id__asset_symbol__exact=symbol)
                   .exclude(d_raw_id__d_close=0)
                   .values_list('d_var_emaclose1734', 'd_var_emaclose3472', 'd_var_emaclose72144',
                                'd_var_emaclose144305', 'd_var_emaclose305610', )
                   .order_by('asset_datetime'))

    if len(adtList) != len(pvList):
        l.log_into_db(level='error',
                      context='updateTechnicalCondition',
                      message='[%s] Not ready: len[adtList] = %i and len(pvList) = %i'
                            % (symbol, len(adtList), len(pvList)))
        return

    for x in range(len(adtList)):
        phibo_test = ema_test = None

        adt = adtList[x]
        close = closeList[x]
        low = lowList[x]
        high = highList[x]

        # Last 4 values (Identifying pivots)
        high_4p = highList[x - 3:x + 1]
        low_4p = lowList[x - 3:x + 1]

        varEma1734 = varList[x][0]
        varEma3472 = varList[x][1]
        varEma72144 = varList[x][2]
        varEma144305 = varList[x][3]
        varEma305610 = varList[x][4]

        emaClose34 = closeEmaList[x][0]
        emaClose144 = closeEmaList[x][1]
        emaClose610 = closeEmaList[x][2]

        pivot = TechnicalCondition.pivot(high_4p, low_4p)
        low_ema_btl = TechnicalCondition.ema_btl(low, emaClose34, emaClose144, emaClose610)
        high_ema_btl = TechnicalCondition.ema_btl(high, emaClose34, emaClose144, emaClose610)
        ema_range = TechnicalCondition.ema_range(varEma1734, varEma3472, varEma72144, varEma144305, varEma305610)
        ema_trend = TechnicalCondition.ema_trend(varEma1734, varEma3472, varEma72144, varEma144305, varEma305610)
        phibo_alignment = TechnicalCondition.phibo_alignment(pvList[x], pcList[x])

        if x >= 305:
            phibo_test = TechnicalCondition.phibo_test(lowList[x - (17 - 1): x + 1],
                                                       highList[x - (17 - 1): x + 1],
                                                       closeList[x - (17 - 1): x + 1],
                                                       pvList[x - (17 - 1): x + 1],
                                                       pcList[x - (17 - 1): x + 1])
            ema_test = TechnicalCondition.ema_test(lowList[x - (17 - 1): x + 1],
                                                   highList[x - (17 - 1): x + 1],
                                                   closeList[x - (17 - 1): x + 1],
                                                   closeEmaList[x - (17 - 1): x + 1])

        obj = D_technicalCondition(d_raw=d_raw.get(asset_datetime=adt),
                                   asset_datetime=adt,

                                   pivot=pivot,
                                   low_ema_btl=low_ema_btl,
                                   high_ema_btl=high_ema_btl,
                                   ema_range=ema_range,
                                   ema_trend=ema_trend,
                                   ema_test=ema_test,
                                   phibo_alignment=phibo_alignment,
                                   phibo_test=phibo_test)
        objs.append(obj)

    if lastXrows > 0:
        d_tc.updateOrCreateObjs(objs[-lastXrows:])  # Last X Ascending
    else:
        d_tc.bulk_create(objs)


def updateSetup(symbol):
    from market.models import Logging, TechnicalCondition, D_raw, D_pvpc, D_ema, D_roc, D_setup, D_technicalCondition
    from market.classes.Setup import Setup

    l = Logging()
    d_setup = D_setup()
    d_raw = D_raw.objects.only('asset_datetime')
    tc = TechnicalCondition.objects.only('id')
    objs = []

    # Ordered by 'd_datetime' ASCENDENT
    adtList = list(D_raw.objects.filter(asset_symbol=symbol)
                   .exclude(d_close=0)
                   .values_list('asset_datetime', flat=True)
                   .order_by('d_datetime'))
    datetimes = list(D_raw.objects.filter(asset_symbol=symbol)
                     .exclude(d_close=0)
                     .values_list('d_datetime', flat=True)
                     .order_by('d_datetime'))
    lowList = list(D_raw.objects.filter(asset_symbol=symbol)
                   .exclude(d_close=0)
                   .values_list('d_low', flat=True)
                   .order_by('d_datetime'))
    highList = list(D_raw.objects.filter(asset_symbol=symbol)
                    .exclude(d_close=0)
                    .values_list('d_high', flat=True)
                    .order_by('d_datetime'))
    # EMA
    closeEmaList = list(D_ema.objects.filter(d_raw_id__asset_symbol__exact=symbol)
                        .exclude(d_raw__d_close=0)
                        .values_list('d_ema_close34', 'd_ema_close144', 'd_ema_close610')
                        .order_by('asset_datetime'))
    # PHIBO
    pvList = list(D_pvpc.objects.filter(d_raw_id__asset_symbol__exact=symbol)
                  .exclude(d_raw__d_close=0)
                  .values_list('d_pv72', 'd_pv305', 'd_pv1292')
                  .order_by('asset_datetime'))
    pcList = list(D_pvpc.objects.filter(d_raw_id__asset_symbol__exact=symbol)
                  .exclude(d_raw__d_close=0)
                  .values_list('d_pc72', 'd_pc305', 'd_pc1292')
                  .order_by('asset_datetime'))
    # ROCs
    rocList = list(D_roc.objects.filter(d_raw_id__asset_symbol__exact=symbol)
                   .exclude(d_raw__d_close=0)
                   .values_list('d_roc_emaclose17')
                   .order_by('asset_datetime'))
    # Technical Conditions
    pivotList = list(D_technicalCondition.objects.filter(d_raw__asset_symbol__exact=symbol)
                     .exclude(d_raw__d_close=0)
                     .values_list('pivot', flat=True)
                     .order_by('asset_datetime'))
    lowemabtlList = list(D_technicalCondition.objects.filter(d_raw__asset_symbol__exact=symbol)
                         .exclude(d_raw__d_close=0)
                         .values_list('low_ema_btl', flat=True)
                         .order_by('asset_datetime'))
    highemabtlList = list(D_technicalCondition.objects.filter(d_raw__asset_symbol__exact=symbol)
                          .exclude(d_raw__d_close=0)
                          .values_list('high_ema_btl', flat=True)
                          .order_by('asset_datetime'))
    emarangeList = list(D_technicalCondition.objects.filter(d_raw__asset_symbol__exact=symbol)
                        .exclude(d_raw__d_close=0)
                        .values_list('ema_range', flat=True)
                        .order_by('asset_datetime'))
    ematrendList = list(D_technicalCondition.objects.filter(d_raw__asset_symbol__exact=symbol)
                        .exclude(d_raw__d_close=0)
                        .values_list('ema_trend', flat=True)
                        .order_by('asset_datetime'))
    ematestList = list(D_technicalCondition.objects.filter(d_raw__asset_symbol__exact=symbol)
                       .exclude(d_raw__d_close=0)
                       .values_list('ema_test', flat=True)
                       .order_by('asset_datetime'))
    phibotestList = list(D_technicalCondition.objects.filter(d_raw__asset_symbol__exact=symbol)
                         .exclude(d_raw__d_close=0)
                         .values_list('phibo_test', flat=True)
                         .order_by('asset_datetime'))
    phiboalignList = list(D_technicalCondition.objects.filter(d_raw__asset_symbol__exact=symbol)
                          .exclude(d_raw__d_close=0)
                          .values_list('phibo_alignment', flat=True)
                          .order_by('asset_datetime'))

    if len(adtList) != len(pivotList):
        l.log_into_db(level='error',
                      context='updateSetup',
                      message='[%s] Not ready: len(adtList) = %i and len(pivotList) = %i'
                            % (symbol, len(adtList), len(pivotList)))
        return

    for x in range(610, len(adtList)):
        adt = adtList[x]
        roc_ema17 = rocList[x][0]

        pivot = pivotList[x]
        low_ema_btl_3p = lowemabtlList[x - 2:x + 1]
        high_ema_btl_3p = highemabtlList[x - 2:x + 1]
        ema_range_3p = emarangeList[x - 2:x + 1]
        ema_trend_3p = ematrendList[x - 2:x + 1]
        ema_test_3p = ematestList[x - 2:x + 1]
        phibo_alignment_3p = phiboalignList[x - 2:x + 1]
        phibo_test_3p = phibotestList[x - 2:x + 1]

        # PHIBO
        tcId_phibo = Setup.get_tcId_phibo(phibo_test_3p, phibo_alignment_3p,
                                          low_ema_btl_3p, high_ema_btl_3p,
                                          pivot, roc_ema17)

        if tcId_phibo:
            setup = Setup()
            setup.started_on = datetimes[x]
            setup.tc = tc.get(pk=tcId_phibo)

            setup.create_phibo_setup(datetimes, highList, lowList, pvList, pcList)

            asset_setup = str(symbol + '_' + setup.tc.id)

            obj = D_setup(d_raw=d_raw.get(asset_datetime=adt),
                          asset_setup=asset_setup,
                          asset_datetime=adt,
                          tc=setup.tc,

                          started_on=setup.started_on,
                          ended_on=setup.ended_on,
                          is_success=setup.is_success,
                          duration=setup.duration,

                          max_price=setup.max_price,
                          target=setup.target,
                          stop_loss=setup.stop_loss,
                          gain_percent=setup.gain_percent,
                          loss_percent=setup.loss_percent,
                          risk_reward=setup.risk_reward,

                          fibo_periods_needed=setup.fibo_periods_needed,
                          fibo_p1=setup.fibo_p1,
                          fibo_p2=setup.fibo_p2,
                          fibo_p3=setup.fibo_p3,
                          fibo_wave_1=setup.fibo_wave_1,
                          fibo_retraction=setup.fibo_retraction,
                          fibo_pct_retraction=setup.fibo_pct_retraction,
                          fibo_projection=setup.fibo_projection)
            objs.append(obj)
            continue

    d_setup.updateOrCreateObjs(objs)


def updateSetupSummary(symbol):
    from market.models import Asset, D_setup, D_setupSummary
    from datetime import datetime, timedelta

    d_ss = D_setupSummary()
    obj_asset = Asset.objects.get(pk=symbol)
    objs = []

    # Ordered by 'd_datetime' ASCENDENT
    # Considers only setups that happened from 4.23 years ago.
    dateFrom = str(datetime.today().date() - timedelta(days=955))
    d_setups = (D_setup.objects.filter(d_raw__asset_symbol__exact=symbol, d_raw__d_datetime__gte=dateFrom)
                .order_by('asset_datetime'))

    setups = {}

    for setup in d_setups:
        setup_id = setup.tc.id

        if setup_id not in setups:
            setups[setup_id] = {
                'tc': setup.tc,
                'has_position_open': False,
                'occurrencies': 0,
                'gain_count': 0,
                'loss_count': 0,
                'duration_gain_sum': 0,
                'duration_loss_sum': 0,
                'last_ended_occurrence': None,
                'last_ended_duration': None,
                'last_was_success': None
            }

        setups[setup_id]['occurrencies'] += 1
        has_position_open = setups[setup_id]['has_position_open']

        if setup.is_success:
            # GAIN
            setups[setup_id]['gain_count'] += 1
            setups[setup_id]['duration_gain_sum'] += setup.duration

            setups[setup_id]['last_ended_occurrence'] = setup.started_on
            setups[setup_id]['last_ended_duration'] = setup.duration
            setups[setup_id]['last_was_success'] = True

        elif setup.is_success is False:
            # LOSS
            setups[setup_id]['loss_count'] += 1
            setups[setup_id]['duration_loss_sum'] += setup.duration

            setups[setup_id]['last_ended_occurrence'] = setup.started_on
            setups[setup_id]['last_ended_duration'] = setup.duration
            setups[setup_id]['last_was_success'] = False

        else:
            setups[setup_id]['has_position_open'] = True

        gain_count = setups[setup_id]['gain_count']
        total_count = setups[setup_id]['gain_count'] + setups[setup_id]['loss_count']
        success_rate = phioon_utils.percentage(gain_count, total_count, decimals=1, if_denominator_is_zero=0)

        # Determine if setup will be visible at this point of time
        if setup.is_public is None:
            # is_public hasn't been touched yet

            if (success_rate >= settings.MARKET_MIN_SUCCESS_RATE and
                    setup.risk_reward >= settings.MARKET_MIN_REWARD_RISK):
                # Setup has good probability
                if total_count == 1:
                    # It's the first time this Setup happens for this asset
                    setup.is_public = True
                elif has_position_open:
                    setup.is_public = False
                else:
                    setup.is_public = True
                setup.save()

            else:
                # Setup hasn't good probablities...
                setup.is_public = False
                setup.save()

    for [setup_id, data] in setups.items():
        asset_setup = str(symbol + '_' + setup_id)
        obj_tc = data['tc']
        has_position_open = data['has_position_open']

        occurrencies = data['occurrencies']
        gain_count = data['gain_count']
        loss_count = data['loss_count']
        total_count = gain_count + loss_count
        duration_gain_sum = data['duration_gain_sum']
        duration_loss_sum = data['duration_loss_sum']

        success_rate = phioon_utils.percentage(gain_count, total_count, decimals=1, if_denominator_is_zero=0)

        avg_duration_gain = round(duration_gain_sum / gain_count, 0) if gain_count > 0 else None
        avg_duration_loss = round(duration_loss_sum / loss_count, 0) if loss_count > 0 else None

        obj = D_setupSummary(asset_setup=asset_setup,
                             asset_symbol=obj_asset,
                             tc=obj_tc,

                             has_position_open=has_position_open,

                             occurrencies=occurrencies,
                             gain_count=gain_count,
                             loss_count=loss_count,
                             success_rate=success_rate,
                             avg_duration_gain=avg_duration_gain,
                             avg_duration_loss=avg_duration_loss,

                             last_ended_occurrence=data['last_ended_occurrence'],
                             last_ended_duration=data['last_ended_duration'],
                             last_was_success=data['last_was_success'])
        objs.append(obj)

    d_ss.updateOrCreateObjs(objs)
