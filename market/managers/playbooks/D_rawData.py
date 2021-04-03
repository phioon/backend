from django_engine.functions import utils as phioon_utils
from django_engine import settings
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from market import models, models_d
from market.managers.ProviderManager import ProviderManager
from market.managers.playbooks.RawData import RawData
from market import setups


class D_rawData(RawData):
    def __init__(self, kwargs={}):
        if 'stock_exchange' in kwargs:
            self.stock_exchange = kwargs['stock_exchange']
        if 'asset' in kwargs:
            self.asset = kwargs['asset']
            self.asset_symbol = kwargs['asset'].asset_symbol
        self.last_periods = kwargs['last_periods']

        self.prepare_requirements()

    def prepare_requirements(self):
        self.prepare_last_periods()

    def prepare_last_periods(self):
        self.last_periods = self.asset.update_stats(last_periods=self.last_periods)

        if self.last_periods < 10:
            rows_count = self.asset.draws.count()
            if rows_count <= 10:
                # Situation 1: Asset is pretty new (company just launched their IPO)
                # Situation 2: Asset hasn't been synced yet
                self.last_periods = 10000

    def run(self, only_offline=False):
        # 1.  Raw Data
        if not only_offline:
            self.run_raw()
        self.prepare_cache_raw()

        # 2.  Phibo PVPC
        self.run_phibo_pvpc()
        self.prepare_cache_phibo_pvpc()

        # 3.  Moving Averages
        # 3.1 EMA
        self.run_ema()
        self.prepare_cache_ema()
        # 3.1 SMA
        self.run_sma()
        self.prepare_cache_sma()

        # 4. Rate of Change (ROC)
        self.run_roc()

        # 5. Variation
        self.run_var()
        self.prepare_cache_var()

        # 6. Technical Conditions
        self.run_tc()
        self.prepare_cache_tc()

        # 7. Phi Trader: Setups and Stats
        self.run_phi_trader_setups()
        self.run_phi_trader_setup_stats()

    def run_phi_trader(self):
        # 1.  Requirements
        # 1.1 Raw Data
        self.prepare_cache_raw()

        # 1.2 Phibo PVPC
        self.prepare_cache_phibo_pvpc()

        # 1.3 Moving Averages
        # 1.3.1 EMA
        self.prepare_cache_ema()

        # 1.3.2 SMA
        # self.prepare_cache_sma()

        # 1.4 Technical Conditions
        self.prepare_cache_tc()

        # 2. Phi Trader: Setups and Stats
        self.run_phi_trader_setups()
        self.run_phi_trader_setup_stats()

    # 1. Raw
    def run_raw(self):
        # 1.  Requirements
        # 1.1 Raw data
        provider_manager = ProviderManager()
        provider_data = provider_manager.get_eod_data(asset_symbol=self.asset_symbol, last_periods=self.last_periods)

        # 2. Prepare for DB
        objs = []
        for item in provider_data:
            objs.append(models_d.D_raw(asset_datetime=phioon_utils.get_asset_datetime(self.asset_symbol,
                                                                                      item['datetime']),
                                       asset=self.asset,
                                       d_datetime=item['datetime'],
                                       d_open=item['open'],
                                       d_high=item['high'],
                                       d_low=item['low'],
                                       d_close=item['close'],
                                       d_volume=item['volume']))

        if self.last_periods > 0:
            models_d.D_raw.bulk_update_or_create(objs[:self.last_periods])  # Descending
        else:
            models_d.D_raw.bulk_create(objs)

    def prepare_cache_raw(self):
        mod = 'raw'

        self.cache[mod]['qs'] = models_d.D_raw.objects.filter(asset=self.asset).exclude(d_close=0)

        self.cache[mod]['df'] = pd.DataFrame(data=self.cache[mod]['qs'].values('asset_datetime',
                                                                               'd_datetime',
                                                                               'd_high',
                                                                               'd_low',
                                                                               'd_close'))
        self.cache[mod]['df'].replace({np.nan: None}, inplace=True)

    # 2. Phibo PVPC
    def run_phibo_pvpc(self):
        # 1.  Requirements
        ascending = False
        # 1.1 Raw Data
        mod = 'raw'
        order_by = ['d_datetime']

        raw_qs = self.cache[mod]['qs']
        df = self.cache[mod]['df'].sort_values(by=order_by, ascending=ascending, ignore_index=True)

        adts = df['asset_datetime'].tolist()
        highs = df['d_high'].tolist()
        lows = df['d_low'].tolist()

        # 2. Calculations and Prepare for DB
        objs = []
        for x in range(len(df)):
            adt = adts[x]
            obj = {
                'd_raw': raw_qs.get(asset_datetime=adt),
                'asset_datetime': adt
            }

            if x + 1292 < len(adts):
                high_1292 = max(highs[x: x + 1292])
                low_1292 = min(lows[x: x + 1292])
                obj['d_pv_1292'] = round(((high_1292 - low_1292) * .786) + low_1292, 2)
                obj['d_pc_1292'] = round(((high_1292 - low_1292) * .214) + low_1292, 2)

            if x + 305 < len(adts):
                high_305 = max(highs[x: x + 305])
                low_305 = min(lows[x: x + 305])
                obj['d_pv_305'] = round(((high_305 - low_305) * .786) + low_305, 2)
                obj['d_pc_305'] = round(((high_305 - low_305) * .214) + low_305, 2)

            if x + 72 < len(adts):
                high_72 = max(highs[x: x + 72])
                low_72 = min(lows[x: x + 72])
                obj['d_pv_72'] = round(((high_72 - low_72) * .786) + low_72, 2)
                obj['d_pc_72'] = round(((high_72 - low_72) * .214) + low_72, 2)

            obj = models_d.D_pvpc(**obj)
            objs.append(obj)

        # 3. Send to DB
        if self.last_periods > 0:
            models_d.D_pvpc.bulk_update_or_create(objs[:self.last_periods])  # Descending
        else:
            models_d.D_pvpc.bulk_create(objs)

    def prepare_cache_phibo_pvpc(self):
        mod = 'pvpc'
        self.cache[mod]['df'] = pd.DataFrame(data=models_d.D_pvpc.objects.filter(d_raw__asset=self.asset).values())

        # Ignoring extra fields...
        self.cache[mod]['df'] = self.cache[mod]['df'].drop(columns=['id', 'd_raw_id'])
        self.cache[mod]['df'].replace({np.nan: None}, inplace=True)

    # 3.  Moving Averages
    # 3.1 EMA
    def run_ema(self):
        # 1.  Requirements
        ascending = True
        # 1.1 Raw Data
        mod = 'raw'
        order_by = ['d_datetime']

        raw_qs = self.cache[mod]['qs']
        raw_df = self.cache[mod]['df'].sort_values(by=order_by, ascending=ascending, ignore_index=True)

        adts = raw_df['asset_datetime'].tolist()
        close_df = raw_df['d_close']

        # 2.  Calculations
        # 2.1 Close
        db_prefix = 'd_ema_close_'
        periods = self.ema_periods
        ema_closes = {}
        for period in periods:
            ema_closes[db_prefix + str(period)] = phioon_utils.get_ema_list(close_df, period)

        # 3. Prepare for DB
        objs = []
        for x in range(len(raw_df)):
            adt = adts[x]
            obj = {
                'd_raw': raw_qs.get(asset_datetime=adt),
                'asset_datetime': adt
            }

            for [k, v] in ema_closes.items():
                obj[k] = v[x]

            obj = models_d.D_ema(**obj)
            objs.append(obj)

        # 4. Send to DB
        if self.last_periods > 0:
            models_d.D_ema.bulk_update_or_create(objs[-self.last_periods:])  # Ascending
        else:
            models_d.D_ema.bulk_create(objs)

    def prepare_cache_ema(self):
        mod = 'ema'
        self.cache[mod]['df'] = pd.DataFrame(data=models_d.D_ema.objects.filter(d_raw__asset=self.asset).values())

        # Ignoring extra fields...
        self.cache[mod]['df'] = self.cache[mod]['df'].drop(columns=['id', 'd_raw_id'])
        self.cache[mod]['df'].replace({np.nan: None}, inplace=True)

    # 3.2 SMA
    def run_sma(self):
        # 1.  Requirements
        ascending = True
        # 1.1 Raw Data
        mod = 'raw'
        order_by = ['d_datetime']

        raw_qs = self.cache[mod]['qs']
        raw_df = self.cache[mod]['df'].sort_values(by=order_by, ascending=ascending, ignore_index=True)

        adts = raw_df['asset_datetime'].tolist()
        close_df = raw_df['d_close']

        # 2.  Calculations
        # 2.1 Close
        db_prefix = 'd_sma_close_'
        periods = self.sma_periods
        sma_closes = {}
        for period in periods:
            sma_closes[db_prefix + str(period)] = phioon_utils.get_sma_list(close_df, period)

        # 3. Prepare for DB
        objs = []
        for x in range(len(raw_df)):
            adt = adts[x]
            obj = {
                'd_raw': raw_qs.get(asset_datetime=adt),
                'asset_datetime': adt
            }

            for [k, v] in sma_closes.items():
                obj[k] = v[x]

            obj = models_d.D_sma(**obj)
            objs.append(obj)

        # 4. Send to DB
        if self.last_periods > 0:
            models_d.D_sma.bulk_update_or_create(objs[-self.last_periods:])  # Ascending
        else:
            models_d.D_sma.bulk_create(objs)

    def prepare_cache_sma(self):
        mod = 'sma'
        self.cache[mod]['df'] = pd.DataFrame(data=models_d.D_sma.objects.filter(d_raw__asset=self.asset).values())

        # Ignoring extra fields...
        self.cache[mod]['df'] = self.cache[mod]['df'].drop(columns=['id', 'd_raw_id'])
        self.cache[mod]['df'].replace({np.nan: None}, inplace=True)

    # 4. Rate of Change (ROC)
    def run_roc(self):
        # 1.  Requirements
        ascending = True
        # 1.1 Raw Data
        mod = 'raw'
        order_by = ['d_datetime']
        raw_qs = self.cache[mod]['qs']
        raw_df = self.cache[mod]['df'].sort_values(by=order_by, ascending=ascending, ignore_index=True)

        adts = raw_df['asset_datetime'].tolist()

        # 1.2 EMA Data
        mod = 'ema'
        order_by = ['asset_datetime']
        ema_df = self.cache[mod]['df'].sort_values(by=order_by, ascending=ascending, ignore_index=True)

        # 1.3 SMA Data
        mod = 'sma'
        order_by = ['asset_datetime']
        sma_df = self.cache[mod]['df'].sort_values(by=order_by, ascending=ascending, ignore_index=True)

        # 2.  Calculations
        # 2.1 EMA (close)
        db_prefix = 'd_roc_ema_close_'
        db_prefix_ema = 'd_ema_close_'
        periods = self.ema_periods
        roc_ema_closes = {}
        for period in periods:
            ema_closes = ema_df[db_prefix_ema + str(period)]
            roc_ema_closes[db_prefix + str(period)] = phioon_utils.get_roc_list(ema_closes, period)

        # 2.2 SMA (close)
        db_prefix = 'd_roc_sma_close_'
        db_prefix_sma = 'd_sma_close_'
        periods = self.sma_periods
        roc_sma_closes = {}
        for period in periods:
            sma_closes = sma_df[db_prefix_sma + str(period)]
            roc_sma_closes[db_prefix + str(period)] = phioon_utils.get_roc_list(sma_closes, period)

        # 3. Prepare for DB
        objs = []
        for x in range(len(raw_df)):
            adt = adts[x]
            obj = {
                'd_raw': raw_qs.get(asset_datetime=adt),
                'asset_datetime': adt
            }

            # 3.1 EMA (close)
            for [k, v] in roc_ema_closes.items():
                obj[k] = v[x]

            # 3.2 SMA (close)
            for [k, v] in roc_sma_closes.items():
                obj[k] = v[x]

            obj = models_d.D_roc(**obj)
            objs.append(obj)

        # 4. Send to DB
        if self.last_periods > 0:
            models_d.D_roc.bulk_update_or_create(objs[-self.last_periods:])  # Ascending
        else:
            models_d.D_roc.bulk_create(objs)

    # 5. Variations
    def run_var(self):
        # 1.  Requirements
        ascending = True
        # 1.1 Raw Data
        mod = 'raw'
        order_by = ['d_datetime']
        raw_qs = self.cache[mod]['qs']
        raw_df = self.cache[mod]['df'].sort_values(by=order_by, ascending=ascending, ignore_index=True)

        adts = raw_df['asset_datetime'].tolist()

        # 1.2 EMA Data
        mod = 'ema'
        order_by = ['asset_datetime']
        ema_df = self.cache[mod]['df'].sort_values(by=order_by, ascending=ascending, ignore_index=True)

        # 2.  Calculations
        # 2.1 EMA (close)
        db_prefix = 'd_var_ema_close_'
        db_prefix_ema = 'd_ema_close_'
        period_tuples = [[8, 17], [17, 34], [34, 72], [72, 144], [144, 305], [305, 610]]
        var_ema_closes = {}

        for x in range(len(raw_df)):
            for [p0, p1] in period_tuples:
                db_field_name = db_prefix + str(p0) + '_' + str(p1)
                variation = None

                if db_field_name not in var_ema_closes:
                    var_ema_closes[db_field_name] = []

                v0 = ema_df[db_prefix_ema + str(p0)][x]
                v1 = ema_df[db_prefix_ema + str(p1)][x]

                if v0 and v1:
                    variation = phioon_utils.percentage(numerator=(v0 - v1),
                                                        denominator=v0,
                                                        decimals=3,
                                                        if_denominator_is_zero=0)

                var_ema_closes[db_field_name].append(variation)

        # 3. Prepare for DB
        objs = []
        for x in range(len(raw_df)):
            adt = adts[x]
            obj = {
                'd_raw': raw_qs.get(asset_datetime=adt),
                'asset_datetime': adt
            }

            # 3.1 EMA (close)
            for [k, v] in var_ema_closes.items():
                obj[k] = v[x]

            obj = models_d.D_var(**obj)
            objs.append(obj)

        # 4. Send to DB
        if self.last_periods > 0:
            models_d.D_var.bulk_update_or_create(objs[-self.last_periods:])  # Ascending
        else:
            models_d.D_var.bulk_create(objs)

    def prepare_cache_var(self):
        mod = 'var'
        self.cache[mod]['df'] = pd.DataFrame(data=models_d.D_var.objects.filter(d_raw__asset=self.asset).values())

        # Ignoring extra fields...
        self.cache[mod]['df'] = self.cache[mod]['df'].drop(columns=['id', 'd_raw_id'])
        self.cache[mod]['df'].replace({np.nan: None}, inplace=True)

    # 6. Technical Conditions
    def run_tc(self):
        # 1.  Requirements
        ascending = True
        # 1.1 Raw Data
        mod = 'raw'
        order_by = ['d_datetime']
        raw_qs = self.cache[mod]['qs']
        raw_df = self.cache[mod]['df'].sort_values(by=order_by, ascending=ascending, ignore_index=True)

        adts = raw_df['asset_datetime'].tolist()

        # 1.2 Phibo PVPC
        mod = 'pvpc'
        order_by = ['asset_datetime']
        pvpc_df = self.cache[mod]['df'].sort_values(by=order_by, ascending=ascending, ignore_index=True)

        # 1.3 EMA Data
        mod = 'ema'
        order_by = ['asset_datetime']
        ema_df = self.cache[mod]['df'].sort_values(by=order_by, ascending=ascending, ignore_index=True)

        # 1.4 SMA Data
        mod = 'sma'
        order_by = ['asset_datetime']
        sma_df = self.cache[mod]['df'].sort_values(by=order_by, ascending=ascending, ignore_index=True)

        # 1.5 Variations
        mod = 'var'
        order_by = ['asset_datetime']
        var_df = self.cache[mod]['df'].sort_values(by=order_by, ascending=ascending, ignore_index=True)

        # 2.  Calculations and Prepare for DB
        objs = []
        for x in range(self.tc_min_periods, len(raw_df)):
            adt = adts[x]
            obj = {
                'd_raw': raw_qs.get(asset_datetime=adt),
                'asset_datetime': adt,
            }

            last_4_highs = raw_df['d_high'][x - 3: x + 1].tolist()
            last_4_lows = raw_df['d_low'][x - 3: x + 1].tolist()

            # 2.1 Raw
            obj['pivot'] = models.TechnicalCondition.pivot(last_4_highs, last_4_lows)

            # 2.2 Phibo PVPC
            obj['pvpc_alignment'] = models.TechnicalCondition.phibo_alignment(pv_72=pvpc_df['d_pv_72'][x],
                                                                              pv_305=pvpc_df['d_pv_305'][x],
                                                                              pv_1292=pvpc_df['d_pv_1292'][x],
                                                                              pc_72=pvpc_df['d_pc_72'][x],
                                                                              pc_305=pvpc_df['d_pc_305'][x],
                                                                              pc_1292=pvpc_df['d_pc_1292'][x])

            # 2.3 EMA
            obj['ema_btl_high'] = models.TechnicalCondition.btl(raw_field=raw_df['d_high'][x],
                                                                indicator_fast=ema_df['d_ema_close_34'][x],
                                                                indicator_mid=ema_df['d_ema_close_144'][x],
                                                                indicator_slow=ema_df['d_ema_close_610'][x])
            obj['ema_btl_low'] = models.TechnicalCondition.btl(raw_field=raw_df['d_low'][x],
                                                               indicator_fast=ema_df['d_ema_close_34'][x],
                                                               indicator_mid=ema_df['d_ema_close_144'][x],
                                                               indicator_slow=ema_df['d_ema_close_610'][x])
            obj['ema_alignment'] = models.TechnicalCondition.ema_alignment(var_ema_34_72=var_df['d_var_ema_close_34_72'][x],
                                                                           var_ema_72_144=var_df['d_var_ema_close_72_144'][x],
                                                                           var_ema_144_305=var_df['d_var_ema_close_144_305'][x],
                                                                           var_ema_305_610=var_df['d_var_ema_close_305_610'][x])
            obj['ema_trend'] = models.TechnicalCondition.ema_trend(var_ema_17_34=var_df['d_var_ema_close_17_34'][x],
                                                                   var_ema_34_72=var_df['d_var_ema_close_34_72'][x],
                                                                   var_ema_72_144=var_df['d_var_ema_close_72_144'][x],
                                                                   var_ema_144_305=var_df['d_var_ema_close_144_305'][x],
                                                                   var_ema_305_610=var_df['d_var_ema_close_305_610'][x])

            # 2.4 SMA
            # Implement it!

            # 2.5 Testing
            is_testing = None
            last_8_highs = raw_df['d_high'][x - (8 - 1): x + 1].tolist()
            last_8_lows = raw_df['d_low'][x - (8 - 1): x + 1].tolist()
            last_8_closes = raw_df['d_close'][x - (8 - 1): x + 1].tolist()

            # 2.3.1 Phibo PVPC
            periods = [1292, 305, 72]
            for p in periods:
                db_prefix = 'd_pv_'
                db_field_name = db_prefix + str(p)

                last_8_i_values = pvpc_df[db_field_name][x - (8 - 1): x + 1]
                last_8_i_values = last_8_i_values.tolist()

                is_testing = models.TechnicalCondition.is_testing_support(lows=last_8_lows,
                                                                          closes=last_8_closes,
                                                                          i_values=last_8_i_values)
                if is_testing:
                    # It's testing a Support line
                    is_testing = p
                    break

                db_prefix = 'd_pc_'
                db_field_name = db_prefix + str(p)

                last_8_i_values = pvpc_df[db_field_name][x - (8 - 1): x + 1]
                last_8_i_values = last_8_i_values.tolist()

                is_testing = models.TechnicalCondition.is_testing_resistance(highs=last_8_highs,
                                                                             closes=last_8_closes,
                                                                             i_values=last_8_i_values)
                if is_testing:
                    # It's testing a Resistance line
                    is_testing = p * - 1
                    break

            obj['pvpc_test'] = is_testing

            # 2.3.2 EMA (close)
            periods = [610, 305, 144, 72]
            db_prefix = 'd_ema_close_'
            for p in periods:
                db_field_name = db_prefix + str(p)

                last_8_i_values = ema_df[db_field_name][x - (8 - 1): x + 1]
                last_8_i_values = last_8_i_values.tolist()

                is_testing = models.TechnicalCondition.is_testing(lows=last_8_lows,
                                                                  highs=last_8_highs,
                                                                  closes=last_8_closes,
                                                                  i_values=last_8_i_values,
                                                                  period=p)
                if is_testing:
                    break

            obj['ema_test'] = is_testing

            # 2.3.3 SMA (close)
            periods = [200, 50]
            db_prefix = 'd_sma_close_'
            for p in periods:
                db_field_name = db_prefix + str(p)

                last_8_i_values = sma_df[db_field_name][x - (8 - 1): x + 1]
                last_8_i_values = last_8_i_values.tolist()

                is_testing = models.TechnicalCondition.is_testing(lows=last_8_lows,
                                                                  highs=last_8_highs,
                                                                  closes=last_8_closes,
                                                                  i_values=last_8_i_values,
                                                                  period=p)
                if is_testing:
                    break

            obj['sma_test'] = is_testing

            obj = models_d.D_tc(**obj)
            objs.append(obj)

        # 4. Send to DB
        if self.last_periods > 0:
            models_d.D_tc.bulk_update_or_create(objs[-self.last_periods:])  # Ascending
        else:
            models_d.D_tc.bulk_create(objs)

    def prepare_cache_tc(self):
        mod = 'tc'
        self.cache[mod]['df'] = pd.DataFrame(data=models_d.D_tc.objects.filter(d_raw__asset=self.asset).values())

        # Ignoring extra fields...
        self.cache[mod]['df'] = self.cache[mod]['df'].drop(columns=['id', 'd_raw_id'])
        self.cache[mod]['df'].replace({np.nan: None}, inplace=True)

    # 7. Phi Trader: Setups and Stats
    def run_phi_trader_setups(self):
        # 1.  Requirements
        ascending = True
        # 1.1 Raw Data
        mod = 'raw'
        order_by = ['d_datetime']
        raw_qs = self.cache[mod]['qs']
        raw_df = self.cache[mod]['df'].sort_values(by=order_by, ascending=ascending)
        raw_df = raw_df.iloc[self.tc_min_periods:].reset_index(drop=True)

        # 1.2 Phibo PVPC
        mod = 'pvpc'
        order_by = ['asset_datetime']
        pvpc_df = self.cache[mod]['df'].sort_values(by=order_by, ascending=ascending)
        pvpc_df = pvpc_df.iloc[self.tc_min_periods:].reset_index(drop=True)

        # 1.3 EMA
        mod = 'ema'
        order_by = ['asset_datetime']
        ema_df = self.cache[mod]['df'].sort_values(by=order_by, ascending=ascending)
        ema_df = ema_df.iloc[self.tc_min_periods:].reset_index(drop=True)

        # 1.4 Technical Conditions
        # There is no need to apply .iloc to [tc_df]
        mod = 'tc'
        order_by = ['asset_datetime']
        tc_df = self.cache[mod]['df'].sort_values(by=order_by, ascending=ascending, ignore_index=True)

        # 2. Calculations
        objs = []
        setup_list = []
        for x in range(1, len(raw_df)):
            adt = raw_df['asset_datetime'][x]
            obj = {
                'd_raw': raw_qs.get(asset_datetime=adt),
                'asset': self.asset,
                'tc': None
            }

            # 2.1 Phibo PVPC
            setup = setups.PhiboPVPC(datetime=raw_df['d_datetime'][x],
                                     pvpc_test_p0=tc_df['pvpc_test'][x],
                                     pvpc_alignment_p0=tc_df['pvpc_alignment'][x],
                                     ema_alignment_p0=tc_df['ema_alignment'][x],
                                     raws_p1={
                                         'high': raw_df['d_high'][x - 1],
                                         'low': raw_df['d_low'][x - 1],
                                     },
                                     raws_p0={
                                         'high': raw_df['d_high'][x],
                                         'low': raw_df['d_low'][x],
                                     },
                                     emas_p0={
                                         'ema_close_17': ema_df['d_ema_close_17'][x],
                                         'ema_close_34': ema_df['d_ema_close_34'][x],
                                         'ema_close_72': ema_df['d_ema_close_72'][x],
                                         'ema_close_144': ema_df['d_ema_close_144'][x],
                                     })

            if setup.tc:
                if len(setup_list) > 0:
                    last_setup = setup_list[-1]
                    if setup.tc == last_setup.tc and (last_setup.ended_on is None or setup.radar_on < last_setup.ended_on):
                        # Current setup is the same as the last one
                        # And the last one is still on-going
                        continue

                setup.prepare_and_run(datetimes=raw_df['d_datetime'].tolist(),
                                      highs=raw_df['d_high'].tolist(),
                                      lows=raw_df['d_low'].tolist(),
                                      last_pvpcs={
                                          'pv_72': pvpc_df['d_pv_72'][x],
                                          'pv_305': pvpc_df['d_pv_305'][x],
                                          'pv_1292': pvpc_df['d_pv_1292'][x],
                                          'pc_72': pvpc_df['d_pc_72'][x],
                                          'pc_305': pvpc_df['d_pc_305'][x],
                                          'pc_1292': pvpc_df['d_pc_1292'][x]
                                      })
                setup_list.append(setup)

                obj.update(setup.get_attr_values())
                obj = models_d.D_phiOperation(**obj)
                objs.append(obj)

                # Setup found for this period. Jump to next one
                continue
        # 3. Send to DB
        models_d.D_phiOperation.bulk_update_or_create(objs)  # Ascending

    def run_phi_trader_setup_stats(self):
        # 1. Requirements
        # 1.1 Phi Operations (last 4 years only)
        order_by = 'radar_on'
        date_from = str(datetime.today().date() - timedelta(days=1460))
        operations = models_d.D_phiOperation.objects.filter(asset=self.asset, radar_on__gte=date_from)\
            .order_by(order_by)

        # 2. Calculations
        stats = {}
        objs = []
        for operation in operations:
            tc_id = operation.tc.id

            if tc_id not in stats:
                stats[tc_id] = {
                    'asset': self.asset,
                    'tc': operation.tc,
                    'has_open_position': False,
                    'occurrencies': 0,
                    'gain_count': 0,
                    'loss_count': 0,
                    'canceled_count': 0,
                    'duration_gain_sum': 0,
                    'duration_loss_sum': 0,
                    'last_ended_occurrence': None,
                    'last_ended_duration': None,
                    'last_was_success': None
                }

            stats[tc_id]['occurrencies'] += 1

            if operation.ended_on is None:
                stats[tc_id]['has_position_open'] = True

            if operation.status == 'gain':
                # GAIN
                stats[tc_id]['gain_count'] += 1
                stats[tc_id]['duration_gain_sum'] += operation.duration

                stats[tc_id]['last_ended_occurrence'] = operation.started_on
                stats[tc_id]['last_ended_duration'] = operation.duration
                stats[tc_id]['last_was_success'] = True
            elif operation.status == 'loss':
                # LOSS
                stats[tc_id]['loss_count'] += 1
                stats[tc_id]['duration_loss_sum'] += operation.duration

                stats[tc_id]['last_ended_occurrence'] = operation.started_on
                stats[tc_id]['last_ended_duration'] = operation.duration
                stats[tc_id]['last_was_success'] = False
            elif operation.status == 'canceled':
                stats[tc_id]['canceled_count'] += 1

            gain_count = stats[tc_id]['gain_count']
            total_count = stats[tc_id]['gain_count'] + stats[tc_id]['loss_count']
            success_rate = phioon_utils.percentage(gain_count, total_count, decimals=1, if_denominator_is_zero=0)

            # Define if setup will be visible at this point of time
            if operation.is_public is None:
                # is_public hasn't been touched yet

                if (success_rate >= settings.MARKET_MIN_SUCCESS_RATE and
                        operation.last_risk_reward >= settings.MARKET_MIN_REWARD_RISK):
                    # Success probability is good
                    operation.is_public = True
                else:
                    # Success probability is not good enough
                    operation.is_public = False

                operation.save()

        for item in stats.values():
            obj = {
                'asset': self.asset,
                'tc': item['tc'],
                'has_open_position': item['has_open_position'],
                'occurrencies': item['occurrencies'],
                'gain_count': item['gain_count'],
                'loss_count': item['loss_count'],
                'canceled_count': item['canceled_count'],
                'success_rate': 0,
                'avg_duration_gain': None,
                'avg_duration_loss': None,
                'last_ended_occurrence': item['last_ended_occurrence'],
                'last_ended_duration': item['last_ended_duration'],
                'last_was_success': item['last_was_success']
            }

            total_count = item['gain_count'] + item['loss_count']
            duration_gain_sum = item['duration_gain_sum']
            duration_loss_sum = item['duration_loss_sum']

            obj['success_rate'] = phioon_utils.percentage(item['gain_count'],
                                                          total_count,
                                                          decimals=1,
                                                          if_denominator_is_zero=0)

            obj['avg_duration_gain'] = round(duration_gain_sum / obj['gain_count'], 0) if obj['gain_count'] > 0 else None
            obj['avg_duration_loss'] = round(duration_loss_sum / obj['loss_count'], 0) if obj['loss_count'] > 0 else None

            obj = models_d.D_phiStats(**obj)
            objs.append(obj)

        # 3. Send to DB
        models_d.D_phiStats.bulk_update_or_create(objs)
