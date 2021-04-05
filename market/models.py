from django.db import models
from django_engine import settings
from market.managers.ProviderManager import ProviderManager
from datetime import datetime


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
                      'type': 'long',
                      'description': 'Price is getting more support and '
                                     'starting an upward trend. '
                                     'Moving Averages 34, 144 and 610 are aligned up '
                                     'and Price is breaking above EMA 34. '
                                     'Gains may vary between 7% and 23%.',
                      'score': None})
        TechnicalCondition.objects.update_or_create(
            id='btl_ema_7__trend_ema_144+',
            defaults={'name': 'BTL Ema 7 and Trend Ema 144',
                      'type': 'long',
                      'description': 'Price is getting more support and '
                                     'starting an upward trend. '
                                     'Moving Averages 34, 144 and 610 are aligned up '
                                     'and Price is breaking above EMA 34. '
                                     'Gains may vary between 7% and 23%',
                      'score': None})
        TechnicalCondition.objects.update_or_create(
            id='btl_ema_0__trend_ema_610-',
            defaults={'name': 'BTL EMA 0 and Trend EMA 610',
                      'type': 'short',
                      'description': 'Price is getting more resistance and '
                                     'starting an downward trend. '
                                     'Moving Averages 34, 144 and 610 are aligned down '
                                     'and Price is breaking bellow EMA 34. '
                                     'Gains may vary between 7% and 16%',
                      'score': None})
        TechnicalCondition.objects.update_or_create(
            id='btl_ema_0__trend_ema_144-',
            defaults={'name': 'BTL Ema 0 and Trend Ema 144',
                      'type': 'short',
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
                      'type': 'long',
                      'description': 'Price reached a key technical support '
                                     'and drew a pivot up. '
                                     'Lines ema34, ema144 and ema610 are aligned up '
                                     'and Price just tested ema610.',
                      'score': None})
        TechnicalCondition.objects.update_or_create(
            id='ema_144_up',
            defaults={'name': 'Decision ema144 and BTL Ema 6',
                      'type': 'long',
                      'description': 'Price reached a key technical support '
                                     'and drew a pivot up. '
                                     'Lines ema34, ema144 and ema610 are aligned up '
                                     'and Price just tested ema610.',
                      'score': None})
        TechnicalCondition.objects.update_or_create(
            id='ema_610_down',
            defaults={'name': 'Decision ema610 and BTL Ema 3',
                      'type': 'short',
                      'description': 'Price reached a key technical resistance '
                                     'and drew a pivot down. '
                                     'Lines ema34, ema144 and ema610 are aligned down '
                                     'and Price just tested ema610.',
                      'score': None})
        TechnicalCondition.objects.update_or_create(
            id='ema_144_down',
            defaults={'name': 'Decision ema610 and BTL Ema 1',
                      'type': 'short',
                      'description': 'Price reached a key technical resistance '
                                     'and drew a pivot down. '
                                     'Lines ema34, ema144 and ema610 are aligned down '
                                     'and Price just tested ema144.',
                      'score': None})

        # PHIBO PRICE TESTING
        TechnicalCondition.objects.update_or_create(
            id='pvpc_1292_long',
            defaults={'name': 'Decision pv1292 and EMA alignment 144+',
                      'type': 'long',
                      'description': 'Price reached a key technical support '
                                     'and drew a pivot up. '
                                     'Lines pv72, pv305 and pv1292 are aligned up '
                                     'and Price just tested pv1292. '
                                     'Stop Loss: Bellow this pivot. '
                                     'Gains may vary between 8% and 23%',
                      'score': None})
        TechnicalCondition.objects.update_or_create(
            id='pvpc_305_long',
            defaults={'name': 'Decision pv305 and EMA alignment 144+',
                      'type': 'long',
                      'description': 'Price reached a key technical support '
                                     'and drew a pivot up. '
                                     'Lines pv72, pv305 and pv1292 are aligned up '
                                     'and Price just tested pv305. '
                                     'Stop Loss: Bellow this pivot. '
                                     'Gains may vary between 8% and 17%.',
                      'score': None})
        TechnicalCondition.objects.update_or_create(
            id='pvpc_72_long',
            defaults={'name': 'Decision pv72 and EMA alignment 144+',
                      'type': 'long',
                      'description': 'Price reached a key technical support '
                                     'and drew a pivot up. '
                                     'Lines pv72, pv305 and pv1292 are aligned up '
                                     'and Price just tested pv72. '
                                     'Stop Loss: Bellow this pivot. '
                                     'Gains may vary between 4% and 9%.',
                      'score': None})
        TechnicalCondition.objects.update_or_create(
            id='pvpc_1292_short',
            defaults={'name': 'Decision pc1292 and EMA alignment 144-',
                      'type': 'short',
                      'description': 'Price reached a key technical support '
                                     'and drew a pivot down. '
                                     'Lines pc72, pc305 and pc1292 are aligned down '
                                     'and Price just tested pc1292. '
                                     'Stop Loss: Above this pivot. '
                                     'Gains may vary between 8% and 17%.',
                      'score': None})
        TechnicalCondition.objects.update_or_create(
            id='pvpc_305_short',
            defaults={'name': 'Decision pc305 and EMA alignment 144-',
                      'type': 'short',
                      'description': 'Price reached a key technical support '
                                     'and drew a pivot down. '
                                     'Lines pc72, pc305 and pc1292 are aligned down '
                                     'and Price just tested pc305. '
                                     'Stop Loss: Above this pivot. '
                                     'Gains may vary between 7% and 14%.',
                      'score': None})
        TechnicalCondition.objects.update_or_create(
            id='pvpc_72_short',
            defaults={'name': 'Decision pc72 and EMA alignment 144-',
                      'type': 'short',
                      'description': 'Price reached a key technical support '
                                     'and drew a pivot down. '
                                     'Lines pc72, pc305 and pc1292 are aligned down '
                                     'and Price just tested pc72. '
                                     'Stop Loss: Above this pivot. '
                                     'Gains may vary between 7% and 14%.',
                      'score': None})

    @staticmethod
    def pivot(last_4_highs, last_4_lows):
        if len(last_4_highs) == 4:
            # Tolerance to avoid '
            min_low_pivot = last_4_lows[2] * 0.99382     # 0.618%
            max_high_pivot = last_4_highs[2] * 1.00618  # 0.618%

            if (last_4_highs[0] > last_4_highs[1] >= last_4_highs[2] and
                    last_4_highs[2] < last_4_highs[3] and
                    min_low_pivot <= last_4_lows[3]):
                return 1

            elif (last_4_highs[1] >= last_4_highs[2] and
                  last_4_highs[2] < last_4_highs[3] and
                  min_low_pivot <= last_4_lows[3]):
                return 1

            if (last_4_lows[0] < last_4_lows[1] <= last_4_lows[2] and
                    last_4_lows[2] > last_4_lows[3] and
                    max_high_pivot >= last_4_highs[3]):
                return -1

            elif (last_4_lows[1] <= last_4_lows[2] and
                  last_4_lows[2] > last_4_lows[3] and
                  max_high_pivot >= last_4_highs[3]):
                return -1

    @staticmethod
    def btl(raw_field, indicator_fast, indicator_mid, indicator_slow):
        # Firstly, check if there is enough data.
        if indicator_slow is not None:
            if raw_field >= indicator_fast >= indicator_mid > indicator_slow:
                return 7
            elif indicator_fast >= raw_field >= indicator_mid > indicator_slow:
                return 6
            elif indicator_fast >= indicator_mid >= raw_field >= indicator_slow:
                return 4
            elif indicator_fast <= indicator_mid <= raw_field <= indicator_slow:
                return 3
            elif indicator_fast <= raw_field <= indicator_mid < indicator_slow:
                return 1
            elif raw_field <= indicator_fast <= indicator_mid < indicator_slow:
                return 0

    @staticmethod
    def ema_alignment(var_ema_34_72, var_ema_72_144, var_ema_144_305, var_ema_305_610):
        alignment = None
        if var_ema_34_72:
            # LONG
            if var_ema_34_72 >= 0:
                alignment = 72
                if var_ema_72_144 and var_ema_72_144 >= 0:
                    alignment = 144
                    if var_ema_144_305 and var_ema_144_305 >= 0:
                        alignment = 305
                        if var_ema_305_610 and var_ema_305_610 >= 0:
                            alignment = 610
            # SHORT
            if var_ema_34_72 < 0:
                alignment = -72
                if var_ema_72_144 and var_ema_72_144 < 0:
                    alignment = -144
                    if var_ema_144_305 and var_ema_144_305 < 0:
                        alignment = -305
                        if var_ema_305_610 and var_ema_305_610 < 0:
                            alignment = -610
        return alignment

    @staticmethod
    def ema_trend(var_ema_17_34, var_ema_34_72, var_ema_72_144, var_ema_144_305, var_ema_305_610):
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
        if var_ema_34_72 is not None:
            # UP
            if (pct_var1734_min <= var_ema_17_34 <= pct_var1734_max and
                    pct_var3472_min <= var_ema_34_72 <= pct_var3472_max):
                trend = 72
                if var_ema_72_144 is not None and -pct_var72144_min <= var_ema_72_144 <= pct_var72144_max:
                    trend = 144
                    if var_ema_144_305 is not None and -pct_var144305_min <= var_ema_144_305 <= pct_var144305_max:
                        trend = 305
                        if var_ema_305_610 is not None and pct_var305610_min <= var_ema_305_610 <= pct_var305610_max:
                            trend = 610
            # DOWN
            elif (pct_var1734_min >= var_ema_17_34 >= -pct_var1734_max and
                  pct_var3472_min >= var_ema_34_72 >= -pct_var3472_max):
                trend = -72
                if var_ema_72_144 is not None and pct_var72144_min >= var_ema_72_144 >= -pct_var72144_max:
                    trend = -144
                    if var_ema_144_305 is not None and pct_var144305_min >= var_ema_144_305 >= -pct_var144305_max:
                        trend = -305
                        if var_ema_305_610 is not None and pct_var305610_min >= var_ema_305_610 >= -pct_var305610_max:
                            trend = -610

        return trend

    @staticmethod
    def phibo_alignment(pv_72, pv_305, pv_1292, pc_72, pc_305, pc_1292):
        if pv_305:
            if pv_1292:
                if pv_72 >= pv_305 >= pv_1292:
                    return 7
                elif pv_1292 >= pv_72 >= pv_305:
                    return 6
                elif pv_72 >= pv_1292:
                    return 6

                elif pc_72 <= pc_305 <= pc_1292:
                    return 0
                elif pc_1292 <= pc_72 <= pc_305:
                    return 1
                elif pc_72 <= pc_1292:
                    return 1
            else:
                if pv_72 >= pv_305:
                    return 6
                elif pc_72 <= pc_305:
                    return 1

    @staticmethod
    def is_testing(lows, highs, closes, i_values, period=None):
        is_testing = TechnicalCondition.is_testing_support(lows=lows,
                                                           closes=closes,
                                                           i_values=i_values)
        if is_testing:
            # It's testing a Support line
            if period:
                return period
            else:
                return 1

        is_testing = TechnicalCondition.is_testing_resistance(highs=highs,
                                                              closes=closes,
                                                              i_values=i_values)
        if is_testing:
            # It's testing a Resistance line
            if period:
                return period * -1
            else:
                return -1

    @staticmethod
    def is_testing_support(lows, closes, i_values):
        # 1. Requirements
        last_index = len(lows) - 1

        if i_values[last_index] is not None:
            # 2. Calculations
            limit_history = 0.04235     # 4.235%
            limit_range = 0.00618       # 0.618%

            last_low = lows[last_index]
            last_close = closes[last_index]
            last_i_value = i_values[last_index]

            lowest_close_4p = min(closes[last_index - 4:])

            limit_min = last_i_value * (1 - limit_history)
            range_min = last_i_value * (1 - limit_range)
            range_max = last_i_value * (1 + limit_range)

            # 3. Validating
            if (lowest_close_4p >= limit_min and
                    (range_min <= last_low <= range_max or range_min <= last_close <= range_max)):
                return True

    @staticmethod
    def is_testing_resistance(highs, closes, i_values):
        # 1. Requirements
        last_index = len(highs) - 1

        if i_values[last_index] is not None:
            # 2. Calculations
            limit_history = 0.04235  # 4.235%
            limit_range = 0.01214  # 1.214%

            last_high = highs[last_index]
            last_close = closes[last_index]
            last_i_value = i_values[last_index]

            highest_close_4p = max(closes[last_index - 4:])

            limit_max = last_i_value * (1 + limit_history)
            range_min = last_i_value * (1 - limit_range)
            range_max = last_i_value * (1 + limit_range)

            # 3. Validating
            if (highest_close_4p <= limit_max and
                    (range_min <= last_high <= range_max or range_min <= last_close <= range_max)):
                return True

    # DEPRECATED
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

    # DEPRECATED
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

    se_short = models.CharField(max_length=32, verbose_name='Stock Exchange Symbol', primary_key=True)
    name = models.CharField(max_length=128, verbose_name='Stock Exchange Name', db_index=True)

    start_time = models.TimeField(default='10:00:00', verbose_name='Usual time the market starts')
    end_time = models.TimeField(default='18:00:00', verbose_name='Usual time the market ends')
    timezone = models.CharField(max_length=32, verbose_name='Timezone (TZ database name)')

    country_code = models.CharField(max_length=8, verbose_name='Alpha-2 Code')
    currency_code = models.CharField(max_length=8, verbose_name='ISO 4217 Code')
    website = models.CharField(max_length=128, null=True)

    def __str__(self):
        return self.se_short


class Asset(models.Model):
    created_time = models.DateField(auto_now_add=True)
    modified_time = models.DateField(auto_now=True)
    last_access_time = models.DateField(default='2001-01-01', db_index=True)

    stock_exchange = models.ForeignKey(StockExchange, related_name='assets', on_delete=models.CASCADE)

    asset_symbol = models.CharField(max_length=32, primary_key=True)
    asset_volume_avg = models.IntegerField(null=True, verbose_name='Volume average over last 10 days.')
    is_considered_for_analysis = models.BooleanField(default=False,
                                                     verbose_name='Is considered for Technical Analysis?')

    def __str__(self):
        return self.asset_symbol

    def update_profile(self):
        # If Profile already exists, update only fields which are not filled yet.
        provider_manager = ProviderManager()
        data = provider_manager.get_profile_data(asset_symbol=self.pk)

        if data:
            if hasattr(self, 'profile'):
                profile = self.profile
            else:
                profile = Profile()
                profile.asset = self

            if not profile.asset_name:
                profile.asset_name = data['asset_name']

            if not profile.asset_label:
                profile.asset_label = data['asset_label']

            if not profile.country_code:
                if data['country_code']:
                    profile.country_code = data['country_code']
                else:
                    profile.country_code = asset.stock_exchange.country_code

            if not profile.sector_id:
                profile.sector_id = data['sector_id']
                profile.sector_name = data['sector_name']

            if not profile.website:
                profile.website = data['website']

            if not profile.business_summary:
                profile.business_summary = data['business_summary']

            profile.save()

    # D_Raw.update_asset calls it every day
    def update_stats(self, last_periods=10):
        self.update_volume_avg()
        last_periods = self.run_check_list(last_periods)

        return last_periods

    def update_volume_avg(self):
        # Ordered by 'd_datetime' DESCENDENT
        vol_list = list(self.draws.exclude(d_close=0)
                        .values_list('d_volume', flat=True)
                        .order_by('-d_datetime')[:10])

        # Calculate volume average of last 10 days
        if len(vol_list) > 0:
            self.asset_volume_avg = int(sum(vol_list) / len(vol_list))
        else:
            self.asset_volume_avg = 0

        self.save()

    # Raw Data
    def run_check_list(self, last_periods):
        is_considered_for_analysis = self.is_considered_for_analysis

        if hasattr(self, 'profile'):
            if self.stock_exchange.country_code == self.profile.country_code:
                if self.asset_volume_avg >= 100000:
                    is_considered_for_analysis = True
                else:
                    is_considered_for_analysis = False
            else:
                # It's a foreign asset
                if self.asset_volume_avg >= 10000:
                    is_considered_for_analysis = True
                else:
                    is_considered_for_analysis = False

        if self.is_considered_for_analysis != is_considered_for_analysis:
            self.is_considered_for_analysis = is_considered_for_analysis
            self.save()

            if is_considered_for_analysis:
                # If asset was not considered before and now it became considered,
                # it doesn't matter what is the current lastXrows value, bring data from scratch
                # And let D_raw know next dependencies should run with the new lastXrows value.
                last_periods = 10000

        return last_periods


class Profile(models.Model):
    modified_time = models.DateField(auto_now=True)

    asset = models.OneToOneField(Asset, related_name='profile', on_delete=models.CASCADE)
    asset_label = models.CharField(max_length=32)
    asset_name = models.CharField(max_length=128)

    country_code = models.CharField(max_length=8, verbose_name='Alpha-2 Code')
    sector_id = models.CharField(max_length=64, null=True)
    sector_name = models.CharField(max_length=64, null=True)
    website = models.CharField(max_length=128, null=True)
    business_summary = models.TextField(null=True)

    def __str__(self):
        return self.asset.asset_symbol

    def updateOrCreateObj(self, obj):
        Profile.objects.update_or_create(
            asset=obj.asset,
            defaults={'asset_label': obj.asset_label,
                      'asset_name': obj.asset_name,
                      'country_code': obj.country_code,
                      'sector_id': obj.sector_id,
                      'sector_name': obj.sector_name,
                      'website': obj.website,
                      'business_summary': obj.business_summary})


class Realtime(models.Model):
    asset = models.OneToOneField(Asset, related_name='realtime', on_delete=models.CASCADE)

    last_trade_time = models.CharField(max_length=32, db_index=True)
    open = models.FloatField(null=True)
    high = models.FloatField(null=True)
    low = models.FloatField(null=True)
    price = models.FloatField()
    volume = models.BigIntegerField(null=True)
    pct_change = models.FloatField(null=True)

    def __str__(self):
        return self.asset.asset_symbol