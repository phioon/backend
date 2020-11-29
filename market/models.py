from django_engine import settings
from market import managers
from .functions import symbolData_d
from datetime import datetime, timedelta
from django.db import models

from google.cloud import tasks_v2

__dateFrom_D__ = str(datetime.today().date() - timedelta(days=4380))
__dateFrom_m60__ = str(datetime.today().date() - timedelta(days=730))
__dateTo__ = str(datetime.today().date())


class Logging(models.Model):
    timestamp = models.DateTimeField(auto_now=True)
    level = models.CharField(max_length=8)
    context = models.CharField(max_length=64)
    message = models.TextField()
    created_by = models.CharField(max_length=32)

    def __str__(self):
        return self.level

    def log_into_db(self, level, context, message, created_by='SYSTEM'):
        log = Logging(level=level,
                      context=context,
                      message=message,
                      created_by=created_by)
        log.save()

    def run_aging(self):
        pass


class TechnicalCondition(models.Model):
    # TC class integrates directly with Analysis and Recommendation classes.
    # These classes must be checked out every time new rows are added here.

    id = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=64)
    type = models.CharField(max_length=12)
    description = models.TextField(max_length=2048)
    score = models.FloatField(null=True)

    def __str__(self):
        return self.id

    def init(self):
        # # # # # # # # # # MAIN # # # # # # # # # #
        TechnicalCondition.objects.update_or_create(
            id='btl_ema_7__trend_ema_610+',
            defaults={'name': 'BTL EMA 7 and Trend EMA 610',
                      'type': 'purchase',
                      'description': 'Price is getting more support and '
                                     'starting an upward trend. '
                                     'Moving Averages 34, 144 and 610 are aligned up '
                                     'and Price is breaking above EMA 34. '
                                     'Gains may vary between 7% and 23%.',
                      'score': None})
        TechnicalCondition.objects.update_or_create(
            id='btl_ema_7__trend_ema_144+',
            defaults={'name': 'BTL Ema 7 and Trend Ema 144',
                      'type': 'purchase',
                      'description': 'Price is getting more support and '
                                     'starting an upward trend. '
                                     'Moving Averages 34, 144 and 610 are aligned up '
                                     'and Price is breaking above EMA 34. '
                                     'Gains may vary between 7% and 23%',
                      'score': None})
        TechnicalCondition.objects.update_or_create(
            id='btl_ema_0__trend_ema_610-',
            defaults={'name': 'BTL EMA 0 and Trend EMA 610',
                      'type': 'sale',
                      'description': 'Price is getting more resistance and '
                                     'starting an downward trend. '
                                     'Moving Averages 34, 144 and 610 are aligned down '
                                     'and Price is breaking bellow EMA 34. '
                                     'Gains may vary between 7% and 16%',
                      'score': None})
        TechnicalCondition.objects.update_or_create(
            id='btl_ema_0__trend_ema_144-',
            defaults={'name': 'BTL Ema 0 and Trend Ema 144',
                      'type': 'sale',
                      'description': 'Price is getting more resistance and '
                                     'starting an downward trend. '
                                     'Moving Averages 34, 144 and 610 are aligned down '
                                     'and Price is breaking bellow EMA 34. '
                                     'Gains may vary between 7% and 13%',
                      'score': None})
        # EMA PRICE TESTING
        TechnicalCondition.objects.update_or_create(
            id='ema_610_up',
            defaults={'name': 'Decision ema610 and BTL Ema 4',
                      'type': 'purchase',
                      'description': 'Price reached a key technical support '
                                     'and drew a pivot up. '
                                     'Lines ema34, ema144 and ema610 are aligned up '
                                     'and Price just tested ema610.',
                      'score': None})
        TechnicalCondition.objects.update_or_create(
            id='ema_144_up',
            defaults={'name': 'Decision ema144 and BTL Ema 6',
                      'type': 'purchase',
                      'description': 'Price reached a key technical support '
                                     'and drew a pivot up. '
                                     'Lines ema34, ema144 and ema610 are aligned up '
                                     'and Price just tested ema610.',
                      'score': None})
        TechnicalCondition.objects.update_or_create(
            id='ema_610_down',
            defaults={'name': 'Decision ema610 and BTL Ema 3',
                      'type': 'sale',
                      'description': 'Price reached a key technical resistance '
                                     'and drew a pivot down. '
                                     'Lines ema34, ema144 and ema610 are aligned down '
                                     'and Price just tested ema610.',
                      'score': None})
        TechnicalCondition.objects.update_or_create(
            id='ema_144_down',
            defaults={'name': 'Decision ema610 and BTL Ema 1',
                      'type': 'sale',
                      'description': 'Price reached a key technical resistance '
                                     'and drew a pivot down. '
                                     'Lines ema34, ema144 and ema610 are aligned down '
                                     'and Price just tested ema144.',
                      'score': None})

        # PHIBO PRICE TESTING
        TechnicalCondition.objects.update_or_create(
            id='phibo_1292_up',
            defaults={'name': 'Decision pv1292 and BTL Ema 6',
                      'type': 'purchase',
                      'description': 'Price reached a key technical support '
                                     'and drew a pivot up. '
                                     'Lines pv72, pv305 and pv1292 are aligned up '
                                     'and Price just tested pv1292. '
                                     'Stop Loss: Bellow this pivot. '
                                     'Gains may vary between 8% and 23%',
                      'score': None})
        TechnicalCondition.objects.update_or_create(
            id='phibo_305_up',
            defaults={'name': 'Decision pv305 and BTL Ema 6',
                      'type': 'purchase',
                      'description': 'Price reached a key technical support '
                                     'and drew a pivot up. '
                                     'Lines pv72, pv305 and pv1292 are aligned up '
                                     'and Price just tested pv305. '
                                     'Stop Loss: Bellow this pivot. '
                                     'Gains may vary between 8% and 17%.',
                      'score': None})
        TechnicalCondition.objects.update_or_create(
            id='phibo_72_up',
            defaults={'name': 'Decision pv72 and BTL Ema 6',
                      'type': 'purchase',
                      'description': 'Price reached a key technical support '
                                     'and drew a pivot up. '
                                     'Lines pv72, pv305 and pv1292 are aligned up '
                                     'and Price just tested pv72. '
                                     'Stop Loss: Bellow this pivot. '
                                     'Gains may vary between 4% and 9%.',
                      'score': None})
        TechnicalCondition.objects.update_or_create(
            id='phibo_1292_down',
            defaults={'name': 'Decision pc1292 and BTL Ema 1',
                      'type': 'sale',
                      'description': 'Price reached a key technical support '
                                     'and drew a pivot down. '
                                     'Lines pc72, pc305 and pc1292 are aligned down '
                                     'and Price just tested pc1292. '
                                     'Stop Loss: Above this pivot. '
                                     'Gains may vary between 8% and 17%.',
                      'score': None})
        TechnicalCondition.objects.update_or_create(
            id='phibo_305_down',
            defaults={'name': 'Decision pc305 and BTL Ema 1',
                      'type': 'sale',
                      'description': 'Price reached a key technical support '
                                     'and drew a pivot down. '
                                     'Lines pc72, pc305 and pc1292 are aligned down '
                                     'and Price just tested pc305. '
                                     'Stop Loss: Above this pivot. '
                                     'Gains may vary between 7% and 14%.',
                      'score': None})
        TechnicalCondition.objects.update_or_create(
            id='phibo_72_down',
            defaults={'name': 'Decision pc72 and BTL Ema 1',
                      'type': 'sale',
                      'description': 'Price reached a key technical support '
                                     'and drew a pivot down. '
                                     'Lines pc72, pc305 and pc1292 are aligned down '
                                     'and Price just tested pc72. '
                                     'Stop Loss: Above this pivot. '
                                     'Gains may vary between 7% and 14%.',
                      'score': None})
        # # # # # # # # # # BTL EMAs # # # # # # # # # #
        TechnicalCondition.objects.update_or_create(
            id='ema_btl_7',
            defaults={'name': 'Price has range ema610 up',
                      'type': 'purchase',
                      'description': 'Price is above ema34. '
                                     'ema34 is above ema144. '
                                     'ema144 is above ema610.',
                      'score': None})
        TechnicalCondition.objects.update_or_create(
            id='ema_btl_6',
            defaults={'name': 'Price is between ema34 and ema144',
                      'type': 'purchase',
                      'description': 'Price is bellow ema34. '
                                     'ema34 is above ema144. '
                                     'ema144 is above ema610.',
                      'score': None})
        TechnicalCondition.objects.update_or_create(
            id='ema_btl_1',
            defaults={'name': 'Price is between ema144 and ema34',
                      'type': 'sale',
                      'description': 'Price is above ema34. '
                                     'ema34 is bellow ema144. '
                                     'ema144 is bellow ema610.',
                      'score': None})
        TechnicalCondition.objects.update_or_create(
            id='ema_btl_0',
            defaults={'name': 'Price has range ema610 down',
                      'type': 'sale',
                      'description': 'Price is bellow ema34. '
                                     'ema34 is bellow ema144. '
                                     'ema144 is bellow ema610.',
                      'score': None})

    @staticmethod
    def pivot(high_4p, low_4p):
        if len(high_4p) == 4:
            # Tolerance to avoid '
            min_low_pivot = low_4p[2] * 0.99382     # 0.618%
            max_high_pivot = high_4p[2] * 1.00618  # 0.618%

            if (high_4p[0] > high_4p[1] >= high_4p[2] and
                    high_4p[2] < high_4p[3] and
                    min_low_pivot <= low_4p[3]):
                return 1

            elif (high_4p[1] >= high_4p[2] and
                  high_4p[2] < high_4p[3] and
                  min_low_pivot <= low_4p[3]):
                return 1

            if (low_4p[0] < low_4p[1] <= low_4p[2] and
                    low_4p[2] > low_4p[3] and
                    max_high_pivot >= high_4p[3]):
                return -1

            elif (low_4p[1] <= low_4p[2] and
                  low_4p[2] > low_4p[3] and
                  max_high_pivot >= high_4p[3]):
                return -1

    @staticmethod
    def ema_btl(raw_field, emaClose34, emaClose144, emaClose610):
        # Firstly, check if there is enough data.
        if emaClose610 is not None:
            if raw_field >= emaClose34 >= emaClose144 > emaClose610:
                return 7
            elif emaClose34 >= raw_field >= emaClose144 > emaClose610:
                return 6
            elif emaClose34 >= emaClose144 >= raw_field >= emaClose610:
                return 4
            elif emaClose34 <= emaClose144 <= raw_field <= emaClose610:
                return 3
            elif emaClose34 <= raw_field <= emaClose144 < emaClose610:
                return 1
            elif raw_field <= emaClose34 <= emaClose144 < emaClose610:
                return 0

    @staticmethod
    def ema_range(varEma1734, varEma3472, varEma72144, varEma144305, varEma305610):
        range = None

        pct_var1734_min = 0
        pct_var3472_min = 0
        pct_var72144_min = 0.382
        pct_var144305_min = 0.618
        pct_var305610_min = 0

        # Firstly, check if there is enough data.
        if varEma3472 is not None:
            # UP
            if (pct_var1734_min <= varEma1734 and
                    pct_var3472_min <= varEma3472):
                range = 72
                if varEma72144 is not None and -pct_var72144_min <= varEma72144:
                    range = 144
                    if varEma144305 is not None and -pct_var144305_min <= varEma144305:
                        range = 305
                        if varEma305610 is not None and pct_var305610_min <= varEma305610:
                            range = 610
            # DOWN
            elif (pct_var1734_min >= varEma1734 and
                  pct_var3472_min >= varEma3472):
                range = -72
                if varEma72144 is not None and pct_var72144_min >= varEma72144:
                    range = -144
                    if varEma144305 is not None and pct_var144305_min >= varEma144305:
                        range = -305
                        if varEma305610 is not None and pct_var305610_min >= varEma305610:
                            range = -610

        return range

    @staticmethod
    def ema_trend(varEma1734, varEma3472, varEma72144, varEma144305, varEma305610):
        trend = None

        pct_var1734_min = 0
        pct_var1734_max = 1.618

        pct_var3472_min = 0
        pct_var3472_max = 1

        pct_var72144_min = 0.382
        pct_var72144_max = 0.618

        pct_var144305_min = 0.618
        pct_var144305_max = 0.618

        pct_var305610_min = 0
        pct_var305610_max = 0.618

        # Firstly, check if there is enough data.
        if varEma3472 is not None:
            # UP
            if (pct_var1734_min <= varEma1734 <= pct_var1734_max and
                    pct_var3472_min <= varEma3472 <= pct_var3472_max):
                trend = 72
                if varEma72144 is not None and -pct_var72144_min <= varEma72144 <= pct_var72144_max:
                    trend = 144
                    if varEma144305 is not None and -pct_var144305_min <= varEma144305 <= pct_var144305_max:
                        trend = 305
                        if varEma305610 is not None and pct_var305610_min <= varEma305610 <= pct_var305610_max:
                            trend = 610
            # DOWN
            elif (pct_var1734_min >= varEma1734 >= -pct_var1734_max and
                  pct_var3472_min >= varEma3472 >= -pct_var3472_max):
                trend = -72
                if varEma72144 is not None and pct_var72144_min >= varEma72144 >= -pct_var72144_max:
                    trend = -144
                    if varEma144305 is not None and pct_var144305_min >= varEma144305 >= -pct_var144305_max:
                        trend = -305
                        if varEma305610 is not None and pct_var305610_min >= varEma305610 >= -pct_var305610_max:
                            trend = -610

        return trend

    @staticmethod
    def phibo_alignment(pvList, pcList):
        pv1292 = pvList[2]
        pv305 = pvList[1]
        pv72 = pvList[0]

        pc1292 = pcList[2]
        pc305 = pcList[1]
        pc72 = pcList[0]

        if pv305 is not None:
            if pv1292 is not None:
                if pv72 >= pv305 >= pv1292:
                    return 7
                elif pv1292 >= pv72 >= pv305:
                    return 6

                elif pc72 <= pc305 <= pc1292:
                    return 0
                elif pc1292 <= pc72 <= pc305:
                    return 1
            else:
                if pv72 >= pv305:
                    return 6
                elif pc72 <= pc305:
                    return 6

    @staticmethod
    def phibo_test(lowList, highList, closeList, pvList, pcList):
        last_index = len(lowList) - 1
        pv1292 = pvList[last_index][2]
        pc1292 = pcList[last_index][2]
        pv305 = pvList[last_index][1]
        pc305 = pcList[last_index][1]
        pv72 = pvList[last_index][0]
        pc72 = pcList[last_index][0]

        if pv305 is None:
            return None

        min_limit_periods_ago = 0.95786  # 4.23%
        max_limit_periods_ago = 1.04235  # 4.23%
        range_min = 0.98786  # 1.214%
        range_max = 1.01214  # 1.214%

        low = lowList[last_index]
        high = highList[last_index]

        # Lowests and highests
        lowest_low = min(lowList)
        highest_high = max(highList)

        lowest_close_3p = min(closeList[last_index - 3:])
        highest_close_3p = max(closeList[last_index - 3:])

        if pv1292 is not None:
            pv1292_range_min = pv1292 * range_min
            pv1292_range_max = pv1292 * range_max
            pv1292_limit_min = pv1292 * min_limit_periods_ago
            pc1292_range_min = pc1292 * range_min
            pc1292_range_max = pc1292 * range_max
            pc1292_limit_max = pc1292 * max_limit_periods_ago

        pv305_range_min = pv305 * range_min
        pv305_range_max = pv305 * range_max
        pv305_limit_min = pv305 * min_limit_periods_ago
        pc305_range_min = pc305 * range_min
        pc305_range_max = pc305 * range_max
        pc305_limit_max = pc305 * max_limit_periods_ago

        pv72_range_min = pv72 * range_min
        pv72_range_max = pv72 * range_max
        pv72_limit_min = pv72 * min_limit_periods_ago
        pc72_range_min = pc72 * range_min
        pc72_range_max = pc72 * range_max
        pc72_limit_max = pc72 * max_limit_periods_ago

        # BUY
        if lowest_low > pc72:
            if (pv1292 is not None and
                    lowest_close_3p >= pv1292_limit_min and
                    pv1292_range_min <= low <= pv1292_range_max):
                return 1292
            elif (lowest_close_3p >= pv305_limit_min and
                  pv305_range_min <= low <= pv305_range_max):
                return 305
            elif (lowest_close_3p >= pv72_limit_min and
                  pv72_range_min <= low <= pv72_range_max):
                return 72

        # SELL
        elif highest_high < pv72:
            if (pc1292 is not None and
                    highest_close_3p <= pc1292_limit_max and
                    pc1292_range_min <= high <= pc1292_range_max):
                return -1292
            elif (highest_close_3p <= pc305_limit_max and
                  pc305_range_min <= high <= pc305_range_max):
                return -305
            elif (highest_close_3p <= pc72_limit_max and
                  pc72_range_min <= high <= pc72_range_max):
                return -72

    @staticmethod
    def ema_test(lowList, highList, closeList, closeEmaList):
        last_index = len(lowList) - 1
        ema610 = closeEmaList[last_index][2]
        ema144 = closeEmaList[last_index][1]

        if ema610 is None:
            return None

        min_limit_periods_ago = 0.95786  # 4.23%
        max_limit_periods_ago = 1.04235  # 4.23%
        range_min = 0.98786  # 1.214%
        range_max = 1.01214  # 1.214%

        # Lowests and highests
        lowest_low = min(lowList)
        highest_high = max(highList)

        lowest_close = min(closeList)
        highest_close = max(closeList)

        ema610_range_min = ema610 * range_min
        ema610_range_max = ema610 * range_max
        ema610_limit_min = ema610 * min_limit_periods_ago
        ema610_limit_max = ema610 * max_limit_periods_ago

        ema144_range_min = ema144 * range_min
        ema144_range_max = ema144 * range_max
        ema144_limit_min = ema144 * min_limit_periods_ago
        ema144_limit_max = ema144 * max_limit_periods_ago

        low = lowList[last_index]
        high = highList[last_index]

        # BUY
        if (lowest_close >= ema610_limit_min and
                ema610_range_min <= low <= ema610_range_max):
            return 610
        elif (lowest_close >= ema144_limit_min and
              ema144_range_min <= low <= ema144_range_max):
            return 144

        # SELL
        if (highest_close <= ema610_limit_max and
                ema610_range_min <= high <= ema610_range_max):
            return -610
        elif (highest_close <= ema144_limit_max and
              ema144_range_min <= high <= ema144_range_max):
            return -144


class StockExchange(models.Model):
    created_time = models.DateField(auto_now_add=True)
    modified_time = models.DateField(auto_now=True)

    se_short = models.CharField(max_length=32, verbose_name='Stock Exchange Short', primary_key=True)
    se_name = models.CharField(max_length=128, verbose_name='Stock Exchange Name', db_index=True)

    se_startTime = models.TimeField(default='10:00:00', verbose_name='Usual time the market starts')
    se_endTime = models.TimeField(default='18:00:00', verbose_name='Usual time the market ends')
    se_timezone = models.CharField(max_length=32, verbose_name='Timezone (TZ database name)')

    country_code = models.CharField(max_length=8, verbose_name='Alpha-2 Code')
    currency_code = models.CharField(max_length=8, verbose_name='ISO 4217 Code')
    website = models.CharField(max_length=128, null=True)

    def __str__(self):
        return self.se_short

    # On-Demand
    def update_stock_exchange_list(self):
        provider_manager = managers.ProviderManager()
        data = provider_manager.get_stock_exchange_list()

        for obj in data:
            StockExchange.objects.update_or_create(
                se_short=obj['se_short'],
                defaults={
                    'se_name': obj['se_name'],
                    'se_timezone': obj['se_timezone'],
                    'country_code': obj['country_code'],
                    'currency_code': obj['currency_code'],
                    'website': obj['website']
                })

    # On-Demand
    def update_stock_exchange_data(self, se_short):
        provider_manager = managers.ProviderManager()
        data = provider_manager.get_stock_exchange_data(se_short=se_short)

        if data:

            try:
                stock_exchange = StockExchange.objects.get(pk=se_short)
            except StockExchange.DoesNotExist:
                stock_exchange = StockExchange(pk=se_short)

            stock_exchange.se_name = data['se_name']
            stock_exchange.country_code = data['country_code']
            stock_exchange.currency_code = data['currency_code']
            stock_exchange.se_timezone = data['se_timezone']
            stock_exchange.website = data['website']
            if 'se_startTime' in data:
                stock_exchange.se_startTime = data['se_startTime']
            if 'se_endTime' in data:
                stock_exchange.se_endTime = data['se_endTime']

            stock_exchange.save()


class Asset(models.Model):
    created_time = models.DateField(auto_now_add=True)
    modified_time = models.DateField(auto_now=True)
    last_access_time = models.DateField(default='2001-01-01', db_index=True)

    stockExchange = models.ForeignKey(StockExchange, related_name='assets', on_delete=models.CASCADE)

    asset_symbol = models.CharField(max_length=32, primary_key=True)
    asset_volume_avg = models.IntegerField(null=True, verbose_name='Volume average over last 10 days.')
    is_considered_for_analysis = models.BooleanField(default=False,
                                                     verbose_name='Is considered for Technical Analysis?')

    def __str__(self):
        return self.asset_symbol

    def frontend_access(self, assets):
        assets = Asset.objects.filter(asset_symbol__in=assets)
        today = datetime.today().date()
        refresh_access = None

        for a in assets:
            sync_raw_data = None

            if (today - a.last_access_time) >= timedelta(days=30):
                # If Asset hasn't synchronized for 30 days or more,
                # it must sync now before return data to frontend
                refresh_access = True
                sync_raw_data = True
                realtime = Realtime()
                realtime.update_realtime_data(a.asset_symbol)

            elif (today - a.last_access_time) >= timedelta(days=1):
                refresh_access = True

            if sync_raw_data:
                d_raw = D_raw()
                d_raw.updateAsset(symbol=a.asset_symbol)


        if refresh_access:
            assets.update(last_access_time=today)


    # Monthly
    def update_assets_by_stock_exchange(self, se_short):
        provider_manager = managers.ProviderManager()
        data = provider_manager.get_assets_by_stock_exchange(se_short=se_short)
        stockExchange = StockExchange.objects.get(se_short=se_short)

        client = tasks_v2.CloudTasksClient()
        parent = client.queue_path(settings.GAE_PROJECT,
                                   settings.GAE_QUEUES['market-asset']['location'],
                                   settings.GAE_QUEUES['market-asset']['name'])

        for obj in data:
            asset_symbol = obj['asset_symbol']
            asset, created = Asset.objects.get_or_create(asset_symbol=asset_symbol,
                                                         stockExchange=stockExchange)

            profile = Profile()
            update_profile = False

            try:
                # If Profile exists, update it only if timedelta is greater than 25 days.
                profile_mtime = asset.profile.modified_time

                today = datetime.today().date()
                delta = today - profile_mtime

                if delta >= timedelta(days=25):
                    update_profile = True

            except Asset.profile.RelatedObjectDoesNotExist:
                update_profile = True

            if update_profile:
                if settings.ACCESS_PRD_DB:
                    url = settings.MARKET_API_BASE + 'task/updateProfile/asset/'
                    url += asset.asset_symbol + '/'
                    url += settings.API_KEY
                    task = {
                        'http_request': {
                            'http_method': 'GET',
                            'url': url}}
                    client.create_task(parent, task)
                else:
                    print('Updating Profile for %s...' % asset.asset_symbol)
                    profile.update_asset_profile(asset.asset_symbol)

    # D_Raw.updateAsset calls it every day
    def updateStats(self, symbol, lastXrows):
        self.updateVolumeAvg(symbol)
        lastXrows = self.runChecklist(symbol, lastXrows)

        return lastXrows

    def updateVolumeAvg(self, symbol):
        # Ordered by 'd_datetime' DESCENDENT
        volList = list(D_raw.objects.filter(asset_symbol=symbol)
                       .exclude(d_close=0)
                       .values_list('d_volume', flat=True)
                       .order_by('-d_datetime'))[:10]

        # Calculate volume average of last 10 days
        if len(volList) > 0:
            vol = int(sum(volList) / len(volList))
        else:
            vol = 0

        obj = Asset(asset_symbol=Asset.objects.get(asset_symbol=symbol),
                    asset_volume_avg=vol)
        self.updateOrCreateObj(obj)

    def runChecklist(self, symbol, lastXrows):
        asset = Asset.objects.get(asset_symbol=symbol)

        is_considered_for_analysis = asset.is_considered_for_analysis

        if hasattr(asset, 'profile') and asset.stockExchange.country_code == asset.profile.country_code:
            if asset.asset_volume_avg >= 100000:
                is_considered_for_analysis = True
            else:
                is_considered_for_analysis = False
        else:
            # It doesn't have a Profile or it's a foreign asset
            if asset.asset_volume_avg >= 10000:
                is_considered_for_analysis = True
            else:
                is_considered_for_analysis = False

        if asset.is_considered_for_analysis != is_considered_for_analysis:
            asset.is_considered_for_analysis = is_considered_for_analysis
            asset.save()

            if is_considered_for_analysis:
                # If asset was not considered before and now it became considered,
                # it doesn't matter what is the current lastXrows value, bring data from scratch
                # And let D_raw know next dependencies should run with the new lastXrows value.
                lastXrows = 10000

        return lastXrows

    def updateOrCreateObj(self, obj):
        if obj.asset_volume_avg is not None:
            Asset.objects.update_or_create(asset_symbol=obj.asset_symbol,
                                           defaults={'asset_volume_avg': obj.asset_volume_avg})


class Profile(models.Model):
    modified_time = models.DateField(auto_now=True)

    asset_symbol = models.OneToOneField(Asset, related_name='profile', on_delete=models.CASCADE)
    asset_label = models.CharField(max_length=32)
    asset_name = models.CharField(max_length=128)

    country_code = models.CharField(max_length=8, verbose_name='Alpha-2 Code')
    sector_id = models.CharField(max_length=64, null=True)
    sector_name = models.CharField(max_length=64, null=True)
    website = models.CharField(max_length=128, null=True)
    business_summary = models.TextField(null=True)

    def __str__(self):
        return self.asset_symbol.asset_symbol

    def update_asset_profile(self, symbol):
        # If Profile already exists, update only fields which are not filled yet.
        provider_manager = managers.ProviderManager()
        data = provider_manager.get_profile_data(asset_symbol=symbol)

        if data:
            asset = Asset.objects.get(asset_symbol=symbol)

            if hasattr(asset, 'profile'):
                profile = Profile.objects.get(asset_symbol=symbol)
            else:
                profile = Profile()
                profile.asset_symbol = asset

            if not profile.asset_name:
                profile.asset_name = data['asset_name']

            if not profile.asset_label:
                profile.asset_label = data['asset_label']

            if not profile.country_code:
                if data['country_code']:
                    profile.country_code = data['country_code']
                else:
                    profile.country_code = asset.stockExchange.country_code

            if not profile.sector_id:
                profile.sector_id = data['sector_id']
                profile.sector_name = data['sector_name']

            if not profile.website:
                profile.website = data['website']

            if not profile.business_summary:
                profile.business_summary = data['business_summary']

            profile.save()

    def updateOrCreateObj(self, obj):
        Profile.objects.update_or_create(
            asset_symbol=obj.asset_symbol,
            defaults={'asset_label': obj.asset_label,
                      'asset_name': obj.asset_name,
                      'country_code': obj.country_code,
                      'sector_id': obj.sector_id,
                      'sector_name': obj.sector_name,
                      'website': obj.website,
                      'business_summary': obj.business_summary})


class Realtime(models.Model):
    asset_symbol = models.OneToOneField(Asset, related_name='realtime', on_delete=models.CASCADE)

    last_trade_time = models.CharField(max_length=32, db_index=True)
    open = models.FloatField(null=True)
    high = models.FloatField(null=True)
    low = models.FloatField(null=True)
    price = models.FloatField()
    volume = models.BigIntegerField(null=True)
    pct_change = models.FloatField(null=True)

    def __str__(self):
        return self.asset_symbol.asset_symbol

    def update_realtime_data(self, symbol):
        provider_manager = managers.ProviderManager()
        data = provider_manager.get_realtime_data(asset_symbol=symbol)

        try:
            realtime = Realtime.objects.get(asset_symbol=Asset.objects.get(pk=symbol))
        except Realtime.DoesNotExist:
            realtime = Realtime(asset_symbol=Asset.objects.get(pk=symbol))

        if data:
            realtime.last_trade_time = data['last_trade_time']
            if data['open']:
                realtime.open = data['open']
            if data['high']:
                realtime.high = data['high']
            if data['low']:
                realtime.low = data['low']
            if data['price']:
                realtime.price = data['price']
            if data['volume']:
                realtime.volume = data['volume']
            if data['pct_change']:
                realtime.pct_change = data['pct_change']

            realtime.save()


class D_raw(models.Model):
    asset_symbol = models.ForeignKey(Asset, related_name='draws', verbose_name='Asset Symbol', on_delete=models.CASCADE)
    asset_datetime = models.CharField(max_length=64, unique=True, db_index=True)  # (PETR4.SAO_20191231000000)
    d_datetime = models.CharField(max_length=32, db_index=True)
    d_open = models.FloatField()
    d_high = models.FloatField()
    d_low = models.FloatField()
    d_close = models.FloatField()
    d_volume = models.BigIntegerField()

    def __str__(self):
        return self.asset_datetime

    def get_field_list(self, field_type='indicator'):
        # Possible entries for 'field_type': ['indicator']
        fields = []

        if field_type == 'indicator':
            fields = ['d_open', 'd_high', 'd_low', 'd_close']

        return fields

    def updateAsset(self, symbol, lastXrows=5):
        a = Asset()
        lastXrows = a.updateStats(symbol=symbol, lastXrows=lastXrows)

        if lastXrows < 10:
            rows_count = D_raw.objects.filter(asset_symbol=symbol).values('pk').count()
            if rows_count <= 10:
                # Situation 1: Asset is pretty new and company just launched their IPO
                # Situation 2: Asset hasn't been synced yet
                lastXrows = 10000

        symbolData_d.updateRaw(symbol=symbol, last_x_rows=lastXrows)
        self.updateDependencies(symbol, lastXrows=lastXrows)

    def updateDependencies(self, symbol, lastXrows):
        pvpc = D_pvpc()
        sma = D_sma()
        ema = D_ema()
        roc = D_roc()
        var = D_var()
        tc = D_technicalCondition()
        setup = D_setup()

        pvpc.updateAsset(symbol=symbol, lastXrows=lastXrows)
        sma.updateAsset(symbol=symbol, lastXrows=lastXrows)
        ema.updateAsset(symbol=symbol, lastXrows=lastXrows)
        roc.updateAsset(symbol=symbol, lastXrows=lastXrows)
        var.updateAsset(symbol=symbol, lastXrows=lastXrows)
        tc.updateAsset(symbol=symbol, lastXrows=lastXrows)
        setup.updateAsset(symbol=symbol)

    def bulk_create(self, objs):
        D_raw.objects.bulk_create(objs, ignore_conflicts=True)

    def updateOrCreateObjs(self, objs):
        for x in range(len(objs)):
            D_raw.objects.update_or_create(
                asset_datetime=objs[x].asset_datetime,
                defaults={'asset_symbol': objs[x].asset_symbol,
                          'd_datetime': objs[x].d_datetime,
                          'd_open': objs[x].d_open,
                          'd_high': objs[x].d_high,
                          'd_low': objs[x].d_low,
                          'd_close': objs[x].d_close,
                          'd_volume': objs[x].d_volume})


class D_pvpc(models.Model):
    d_raw = models.OneToOneField(D_raw, on_delete=models.CASCADE)
    asset_datetime = models.CharField(max_length=64, unique=True, db_index=True)  # (PETR4.SA_20191231000000)

    d_pv72 = models.FloatField(null=True)
    d_pv305 = models.FloatField(null=True)
    d_pv1292 = models.FloatField(null=True)

    d_pc72 = models.FloatField(null=True)
    d_pc305 = models.FloatField(null=True)
    d_pc1292 = models.FloatField(null=True)

    def __str__(self):
        return self.asset_datetime

    def get_field_list(self, field_type='indicator'):
        # Possible entries for 'field_type': ['indicator']
        fields = []

        if field_type == 'indicator':
            ignore_fields = ['id', 'd_raw', 'asset_datetime']
            for field in self._meta.fields:
                if field.name not in ignore_fields:
                    fields.append(field.name)

        return fields

    def updateAsset(self, symbol, lastXrows=0):
        symbolData_d.updatePvpc(symbol=symbol, lastXrows=lastXrows)

    def bulk_create(self, objs):
        D_pvpc.objects.bulk_create(objs, ignore_conflicts=True)

    def updateOrCreateObjs(self, objs):
        for x in range(len(objs)):
            D_pvpc.objects.update_or_create(
                asset_datetime=objs[x].asset_datetime,
                defaults={
                    'd_raw': objs[x].d_raw,
                    'd_pv72': objs[x].d_pv72,
                    'd_pv305': objs[x].d_pv305,
                    'd_pv1292': objs[x].d_pv1292,
                    'd_pc72': objs[x].d_pc72,
                    'd_pc305': objs[x].d_pc305,
                    'd_pc1292': objs[x].d_pc1292
                })


class D_sma(models.Model):
    d_raw = models.OneToOneField(D_raw, db_index=True, on_delete=models.CASCADE)
    asset_datetime = models.CharField(max_length=64, unique=True, db_index=True)  # (PETR4.SA_20191231000000)

    d_sma_close7 = models.FloatField(null=True)
    d_sma_close10 = models.FloatField(null=True)
    d_sma_close20 = models.FloatField(null=True)
    d_sma_close21 = models.FloatField(null=True)
    d_sma_close30 = models.FloatField(null=True)
    d_sma_close50 = models.FloatField(null=True)
    d_sma_close55 = models.FloatField(null=True)
    d_sma_close100 = models.FloatField(null=True)
    d_sma_close200 = models.FloatField(null=True)

    def __str__(self):
        return self.asset_datetime

    def get_field_list(self, field_type='indicator'):
        # Possible entries for 'field_type': ['indicator']
        fields = []

        if field_type == 'indicator':
            ignore_fields = ['id', 'd_raw', 'asset_datetime']
            for field in self._meta.fields:
                if field.name not in ignore_fields:
                    fields.append(field.name)

        return fields

    def updateAsset(self, symbol, lastXrows=0):
        symbolData_d.updateSma(symbol=symbol, lastXrows=lastXrows)

    def bulk_create(self, objs):
        D_sma.objects.bulk_create(objs, ignore_conflicts=True)

    def updateOrCreateObjs(self, objs):
        for x in range(len(objs)):
            D_sma.objects.update_or_create(
                asset_datetime=objs[x].asset_datetime,
                defaults={
                    'd_raw': objs[x].d_raw,
                    'd_sma_close7': objs[x].d_sma_close7,
                    'd_sma_close10': objs[x].d_sma_close10,
                    'd_sma_close20': objs[x].d_sma_close20,
                    'd_sma_close21': objs[x].d_sma_close21,
                    'd_sma_close30': objs[x].d_sma_close30,
                    'd_sma_close50': objs[x].d_sma_close50,
                    'd_sma_close55': objs[x].d_sma_close55,
                    'd_sma_close100': objs[x].d_sma_close100,
                    'd_sma_close200': objs[x].d_sma_close200})


class D_ema(models.Model):
    d_raw = models.OneToOneField(D_raw, db_index=True, on_delete=models.CASCADE)
    asset_datetime = models.CharField(max_length=64, unique=True, db_index=True)  # (PETR4.SA_20191231000000)

    d_ema_close8 = models.FloatField(null=True)
    d_ema_close9 = models.FloatField(null=True)
    d_ema_close17 = models.FloatField(null=True)
    d_ema_close34 = models.FloatField(null=True)
    d_ema_close50 = models.FloatField(null=True)
    d_ema_close72 = models.FloatField(null=True)
    d_ema_close144 = models.FloatField(null=True)
    d_ema_close200 = models.FloatField(null=True)
    d_ema_close305 = models.FloatField(null=True)
    d_ema_close610 = models.FloatField(null=True)
    d_ema_close1292 = models.FloatField(null=True)
    d_ema_close2584 = models.FloatField(null=True)

    def __str__(self):
        return self.asset_datetime

    def get_field_list(self, field_type='indicator'):
        # Possible entries for 'field_type': ['indicator']
        fields = []

        if field_type == 'indicator':
            ignore_fields = ['id', 'd_raw', 'asset_datetime']
            for field in self._meta.fields:
                if field.name not in ignore_fields:
                    fields.append(field.name)

        return fields

    def updateAsset(self, symbol, lastXrows=0):
        symbolData_d.updateEma(symbol=symbol, lastXrows=lastXrows)

    def bulk_create(self, objs):
        D_ema.objects.bulk_create(objs, ignore_conflicts=True)

    def updateOrCreateObjs(self, objs):
        for x in range(len(objs)):
            D_ema.objects.update_or_create(
                asset_datetime=objs[x].asset_datetime,
                defaults={
                    'd_raw': objs[x].d_raw,
                    'd_ema_close8': objs[x].d_ema_close8,
                    'd_ema_close9': objs[x].d_ema_close9,
                    'd_ema_close17': objs[x].d_ema_close17,
                    'd_ema_close34': objs[x].d_ema_close34,
                    'd_ema_close50': objs[x].d_ema_close50,
                    'd_ema_close72': objs[x].d_ema_close72,
                    'd_ema_close144': objs[x].d_ema_close144,
                    'd_ema_close200': objs[x].d_ema_close200,
                    'd_ema_close305': objs[x].d_ema_close305,
                    'd_ema_close610': objs[x].d_ema_close610,
                    'd_ema_close1292': objs[x].d_ema_close1292,
                    'd_ema_close2584': objs[x].d_ema_close2584})


class D_roc(models.Model):
    d_raw = models.OneToOneField(D_raw, verbose_name='Asset and Datetime', on_delete=models.CASCADE)
    asset_datetime = models.CharField(max_length=64, unique=True, db_index=True)  # (PETR4.SA_20191231000000)

    d_roc_smaclose7 = models.FloatField(null=True)
    d_roc_smaclose10 = models.FloatField(null=True)
    d_roc_smaclose20 = models.FloatField(null=True)
    d_roc_smaclose21 = models.FloatField(null=True)
    d_roc_smaclose30 = models.FloatField(null=True)
    d_roc_smaclose50 = models.FloatField(null=True)
    d_roc_smaclose55 = models.FloatField(null=True)
    d_roc_smaclose100 = models.FloatField(null=True)
    d_roc_smaclose200 = models.FloatField(null=True)

    d_roc_emaclose8 = models.FloatField(null=True)
    d_roc_emaclose9 = models.FloatField(null=True)
    d_roc_emaclose17 = models.FloatField(null=True)
    d_roc_emaclose34 = models.FloatField(null=True)
    d_roc_emaclose50 = models.FloatField(null=True)
    d_roc_emaclose72 = models.FloatField(null=True)
    d_roc_emaclose144 = models.FloatField(null=True)
    d_roc_emaclose200 = models.FloatField(null=True)
    d_roc_emaclose305 = models.FloatField(null=True)
    d_roc_emaclose610 = models.FloatField(null=True)
    d_roc_emaclose1292 = models.FloatField(null=True)
    d_roc_emaclose2584 = models.FloatField(null=True)

    def __str__(self):
        return self.asset_datetime

    def get_field_list(self, field_type='indicator'):
        # Possible entries for 'field_type': ['indicator']
        fields = []

        if field_type == 'indicator':
            ignore_fields = ['id', 'd_raw', 'asset_datetime']
            for field in self._meta.fields:
                if field.name not in ignore_fields:
                    fields.append(field.name)

        return fields

    def updateAsset(self, symbol, lastXrows=0):
        symbolData_d.updateRoc(symbol=symbol, lastXrows=lastXrows)

    def bulk_create(self, objs):
        D_roc.objects.bulk_create(objs, ignore_conflicts=True)

    def updateOrCreateObjs(self, objs):
        for x in range(len(objs)):
            D_roc.objects.update_or_create(
                asset_datetime=objs[x].asset_datetime,
                defaults={
                    'd_raw': objs[x].d_raw,
                    'd_roc_smaclose7': objs[x].d_roc_smaclose7,
                    'd_roc_smaclose10': objs[x].d_roc_smaclose10,
                    'd_roc_smaclose20': objs[x].d_roc_smaclose20,
                    'd_roc_smaclose21': objs[x].d_roc_smaclose21,
                    'd_roc_smaclose30': objs[x].d_roc_smaclose30,
                    'd_roc_smaclose50': objs[x].d_roc_smaclose50,
                    'd_roc_smaclose55': objs[x].d_roc_smaclose55,
                    'd_roc_smaclose100': objs[x].d_roc_smaclose100,
                    'd_roc_smaclose200': objs[x].d_roc_smaclose200,

                    'd_roc_emaclose8': objs[x].d_roc_emaclose8,
                    'd_roc_emaclose9': objs[x].d_roc_emaclose9,
                    'd_roc_emaclose17': objs[x].d_roc_emaclose17,
                    'd_roc_emaclose34': objs[x].d_roc_emaclose34,
                    'd_roc_emaclose50': objs[x].d_roc_emaclose50,
                    'd_roc_emaclose72': objs[x].d_roc_emaclose72,
                    'd_roc_emaclose144': objs[x].d_roc_emaclose144,
                    'd_roc_emaclose200': objs[x].d_roc_emaclose200,
                    'd_roc_emaclose305': objs[x].d_roc_emaclose305,
                    'd_roc_emaclose610': objs[x].d_roc_emaclose610,
                    'd_roc_emaclose1292': objs[x].d_roc_emaclose1292,
                    'd_roc_emaclose2584': objs[x].d_roc_emaclose2584})


class D_var(models.Model):
    d_raw = models.OneToOneField(D_raw, verbose_name='Asset and Datetime', on_delete=models.CASCADE)
    asset_datetime = models.CharField(max_length=64, unique=True, db_index=True)  # (PETR4.SA_20191231000000)

    d_var_emaclose1734 = models.FloatField(null=True, verbose_name='Percent variation between values')
    d_var_emaclose3472 = models.FloatField(null=True, verbose_name='Percent variation between values')
    d_var_emaclose72144 = models.FloatField(null=True, verbose_name='Percent variation between values')
    d_var_emaclose144305 = models.FloatField(null=True, verbose_name='Percent variation between values')
    d_var_emaclose305610 = models.FloatField(null=True, verbose_name='Percent variation between values')

    def __str__(self):
        return self.asset_datetime

    def updateAsset(self, symbol, lastXrows=0):
        symbolData_d.updateVar(symbol=symbol, lastXrows=lastXrows)

    def bulk_create(self, objs):
        D_var.objects.bulk_create(objs, ignore_conflicts=True)

    def updateOrCreateObjs(self, objs):
        for x in range(len(objs)):
            D_var.objects.update_or_create(
                asset_datetime=objs[x].asset_datetime,
                defaults={
                    'd_raw': objs[x].d_raw,
                    'd_var_emaclose1734': objs[x].d_var_emaclose1734,
                    'd_var_emaclose3472': objs[x].d_var_emaclose3472,
                    'd_var_emaclose72144': objs[x].d_var_emaclose72144,
                    'd_var_emaclose144305': objs[x].d_var_emaclose144305,
                    'd_var_emaclose305610': objs[x].d_var_emaclose305610})


class D_technicalCondition(models.Model):
    d_raw = models.OneToOneField(D_raw, on_delete=models.CASCADE)
    asset_datetime = models.CharField(max_length=64, unique=True, db_index=True)  # (PETR4.SAO_20191231000000)

    pivot = models.IntegerField(null=True)
    low_ema_btl = models.IntegerField(null=True)
    high_ema_btl = models.IntegerField(null=True)
    ema_range = models.IntegerField(null=True)
    ema_trend = models.IntegerField(null=True)
    ema_test = models.IntegerField(null=True)

    phibo_alignment = models.IntegerField(null=True)
    phibo_test = models.IntegerField(null=True)

    def __str__(self):
        return self.asset_datetime

    def updateAsset(self, symbol, lastXrows=0):
        symbolData_d.updateTechnicalCondition(symbol=symbol, lastXrows=lastXrows)

    def bulk_create(self, objs):
        D_technicalCondition.objects.bulk_create(objs, ignore_conflicts=True)

    def updateOrCreateObjs(self, objs):
        for x in range(len(objs)):
            D_technicalCondition.objects.update_or_create(asset_datetime=objs[x].asset_datetime,
                                                          defaults={
                                                              'd_raw': objs[x].d_raw,

                                                              'pivot': objs[x].pivot,
                                                              'low_ema_btl': objs[x].low_ema_btl,
                                                              'high_ema_btl': objs[x].high_ema_btl,
                                                              'ema_range': objs[x].ema_range,
                                                              'ema_trend': objs[x].ema_trend,
                                                              'ema_test': objs[x].ema_test,
                                                              'phibo_alignment': objs[x].phibo_alignment,
                                                              'phibo_test': objs[x].phibo_test})


class D_setup(models.Model):
    d_raw = models.OneToOneField(D_raw, on_delete=models.CASCADE)
    asset_datetime = models.CharField(max_length=64, unique=True, db_index=True)  # (PETR4.SAO_20191231000000)
    asset_setup = models.CharField(max_length=64, db_index=True)  # (PETR4.SAO_phibo_1292_up)
    tc = models.ForeignKey(TechnicalCondition, on_delete=models.CASCADE)

    is_public = models.BooleanField(default=False)

    started_on = models.CharField(max_length=32, null=True)
    ended_on = models.CharField(max_length=32, null=True)
    is_success = models.BooleanField(null=True)
    duration = models.IntegerField(default=True)

    max_price = models.FloatField(null=True)
    target = models.FloatField(null=True)
    stop_loss = models.FloatField(null=True)
    gain_percent = models.FloatField(null=True)
    loss_percent = models.FloatField(null=True)
    risk_reward = models.FloatField(null=True)

    # fiboProjection
    fibo_periods_needed = models.FloatField(null=True)
    fibo_p1 = models.FloatField(null=True)
    fibo_p2 = models.FloatField(null=True)
    fibo_p3 = models.FloatField(null=True)
    fibo_wave_1 = models.FloatField(null=True)
    fibo_retraction = models.FloatField(null=True)
    fibo_pct_retraction = models.FloatField(null=True)
    fibo_projection = models.FloatField(null=True)

    def __str__(self):
        return self.asset_datetime

    def updateAsset(self, symbol):
        asset = Asset.objects.get(pk=symbol)

        if asset.is_considered_for_analysis:
            symbolData_d.updateSetup(symbol=symbol)
            self.updateDependencies(symbol=symbol)

    def updateDependencies(self, symbol):
        symbolData_d.updateSetupSummary(symbol=symbol)

    def bulk_create(self, objs):
        D_setup.objects.bulk_create(objs, ignore_conflicts=True)

    def updateOrCreateObjs(self, objs):
        for x in range(len(objs)):
            D_setup.objects.update_or_create(
                asset_datetime=objs[x].asset_datetime,
                defaults={
                    'asset_setup': objs[x].asset_setup,
                    'd_raw': objs[x].d_raw,
                    'tc': objs[x].tc,

                    'started_on': objs[x].started_on,
                    'ended_on': objs[x].ended_on,
                    'is_success': objs[x].is_success,
                    'duration': objs[x].duration,

                    'max_price': objs[x].max_price,
                    'target': objs[x].target,
                    'stop_loss': objs[x].stop_loss,
                    'gain_percent': objs[x].gain_percent,
                    'loss_percent': objs[x].loss_percent,
                    'risk_reward': objs[x].risk_reward,

                    'fibo_periods_needed': objs[x].fibo_periods_needed,
                    'fibo_p1': objs[x].fibo_p1,
                    'fibo_p2': objs[x].fibo_p2,
                    'fibo_p3': objs[x].fibo_p3,
                    'fibo_wave_1': objs[x].fibo_wave_1,
                    'fibo_retraction': objs[x].fibo_retraction,
                    'fibo_pct_retraction': objs[x].fibo_pct_retraction,
                    'fibo_projection': objs[x].fibo_projection})


class D_setupSummary(models.Model):
    asset_setup = models.CharField(max_length=64, unique=True, db_index=True)  # (PETR4.SAO_phibo_1292_up)
    asset_symbol = models.ForeignKey(Asset, db_index=True, on_delete=models.CASCADE)
    tc = models.ForeignKey(TechnicalCondition, on_delete=models.CASCADE)

    has_position_open = models.BooleanField(default=False)

    occurrencies = models.IntegerField(default=0)
    gain_count = models.IntegerField(default=0)
    loss_count = models.IntegerField(default=0)
    success_rate = models.FloatField(default=0)
    avg_duration_gain = models.IntegerField(null=True)
    avg_duration_loss = models.IntegerField(null=True)

    last_ended_occurrence = models.CharField(max_length=32, null=True)
    last_ended_duration = models.IntegerField(null=True)
    last_was_success = models.BooleanField(null=True)

    def __str__(self):
        return self.asset_setup

    def updateOrCreateObjs(self, objs):
        for x in range(len(objs)):
            D_setupSummary.objects.update_or_create(
                asset_setup=objs[x].asset_setup,
                defaults={'asset_symbol': objs[x].asset_symbol,
                          'tc': objs[x].tc,

                          'has_position_open': objs[x].has_position_open,

                          'occurrencies': objs[x].occurrencies,
                          'gain_count': objs[x].gain_count,
                          'loss_count': objs[x].loss_count,
                          'success_rate': objs[x].success_rate,

                          'avg_duration_gain': objs[x].avg_duration_gain,
                          'avg_duration_loss': objs[x].avg_duration_loss,
                          'last_ended_occurrence': objs[x].last_ended_occurrence,
                          'last_ended_duration': objs[x].last_ended_duration,
                          'last_was_success': objs[x].last_was_success})
