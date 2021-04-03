from django_engine.functions import utils
from market import models


class Setup:
    tc = None

    status = 'waiting'      # ['waiting', 'canceled', 'in_progress', 'gain', 'loss']

    radar_on = None
    started_on = None
    ended_on = None
    duration = 0

    entry_price = list()
    target = list()
    stop_loss = list()
    gain_percent = list()
    loss_percent = list()
    risk_reward = list()

    # Projection
    fibonacci = {
        'periods_needed': None,
        'p1': None,
        'p2': None,
        'p3': None,
        'first_wave': None,
        'retracement': None,
        'retracement_pct': None,
        'projection': None,
    }

    def __init__(self):
        self.status = 'waiting'
        self.entry_price = list()
        self.target = list()
        self.stop_loss = list()
        self.gain_percent = list()
        self.loss_percent = list()
        self.risk_reward = list()

    def get_attr_values(self):
        return vars(self)

    def get_last_attr(self, attr):
        field = getattr(self, attr)

        if isinstance(field, list):
            field = field[-1]['value'] if len(field) > 0 else None

        return field

    def set_attr(self, attr, value):
        if not hasattr(self, attr):
            return

        setattr(self, attr, value)

    def set_history_attr(self, attr, datetime, value):
        if not hasattr(self, attr):
            return

        obj_list = getattr(self, attr)
        obj_list.append({
            'datetime': datetime,
            'value': round(value, 2)})
        self.set_attr(attr, obj_list)

        if attr in ['entry_price', 'target', 'stop_loss']:
            if self.entry_price and self.target and self.stop_loss:
                # All 3 objects must be fulfilled
                # If one of these attributes get updated, others must be recalculated
                self.calculate_automatic_fields(datetime=datetime)

    def calculate_automatic_fields(self, datetime):
        entry_price = self.get_last_attr('entry_price')
        target = self.get_last_attr('target')
        stop_loss = self.get_last_attr('stop_loss')

        if self.tc.type == 'long':
            gain_percent = utils.gain_percent_buy(entry_price, target)
            loss_percent = utils.stop_loss_buy(entry_price, stop_loss)
        else:
            gain_percent = utils.gain_percent_sell(entry_price, target)
            loss_percent = utils.stop_loss_sell(entry_price, stop_loss)

        risk_reward = utils.risk_reward(gain_percent, loss_percent)

        self.set_history_attr('gain_percent', datetime, gain_percent)
        self.set_history_attr('loss_percent', datetime, loss_percent)
        self.set_history_attr('risk_reward', datetime, risk_reward)

    def run_simulation(self, datetimes, highs, lows, extras):
        # Run a simulation of the Setup in order to:
        #   . Define its latest status
        #   . Identify what is the current situation for open operations
        # It's used to build up Phi Trader Stats model
        if extras is None:
            extras = {}
        i = 0

        while self.ended_on is None and i < (len(datetimes)):
            high = highs[i]
            low = lows[i]

            if self.tc.type == 'long':
                # LONG
                if self.status == 'waiting':
                    # Setup waiting to be activated
                    if high >= self.get_last_attr('entry_price'):
                        self.status = 'in_progress'
                        self.started_on = datetimes[i]
                    elif low <= self.get_last_attr('stop_loss'):
                        self.status = 'canceled'
                        self.ended_on = datetimes[i]
                    else:
                        # If it's not <in_progress> nor <canceled>, update trailing Entry Price
                        entry_price = extras['get_entry_price'](high=high, low=low)
                        self.set_history_attr('entry_price', datetimes[i], entry_price)

                elif self.status == 'in_progress':
                    # Setup in progress
                    self.duration += 1
                    if high >= self.get_last_attr('target'):
                        # GAIN
                        self.status = 'gain'
                        self.ended_on = datetimes[i]
                    elif low <= self.get_last_attr('stop_loss'):
                        # LOSS
                        self.status = 'loss'
                        self.ended_on = datetimes[i]

            else:
                # SHORT
                if self.status == 'waiting':
                    # Setup waiting to be activated
                    if low <= self.get_last_attr('entry_price'):
                        self.status = 'in_progress'
                        self.started_on = datetimes[i]
                    elif high >= self.get_last_attr('stop_loss'):
                        self.status = 'canceled'
                        self.ended_on = datetimes[i]
                    else:
                        # If it's not <in_progress> nor <canceled>, update trailing Entry Price
                        entry_price = extras['get_entry_price'](high=high, low=low)
                        self.set_history_attr('entry_price', datetimes[i], entry_price)

                elif self.status == 'in_progress':
                    self.duration += 1
                    # Setup in progress
                    if low <= self.get_last_attr('target'):
                        # GAIN
                        self.status = 'gain'
                        self.ended_on = datetimes[i]
                    elif high >= self.get_last_attr('stop_loss'):
                        # LOSS
                        self.status = 'loss'
                        self.ended_on = datetimes[i]
            i += 1


class PhiboPVPC (Setup):

    def __init__(self, datetime, pvpc_test_p0, pvpc_alignment_p0, ema_alignment_p0, raws_p1, raws_p0, emas_p0):
        super().__init__()
        tc_id = None

        d_threshold = 0.0423

        if (pvpc_alignment_p0 in [6, 7] and
                pvpc_test_p0 == 1292 and
                ema_alignment_p0 and ema_alignment_p0 >= 144 and
                raws_p1['high'] > raws_p0['high'] and
                (utils.is_near(emas_p0['ema_close_72'], raws_p0['low'], d_threshold) or
                 utils.is_near(emas_p0['ema_close_144'], raws_p0['low'], d_threshold))):
            tc_id = 'pvpc_1292_long'
        elif (pvpc_alignment_p0 in [6, 7] and
              pvpc_test_p0 == 305 and
              ema_alignment_p0 and ema_alignment_p0 >= 144 and
              raws_p1['high'] > raws_p0['high'] and
              (utils.is_near(emas_p0['ema_close_34'], raws_p0['low'], d_threshold) or
               utils.is_near(emas_p0['ema_close_72'], raws_p0['low'], d_threshold) or
               utils.is_near(emas_p0['ema_close_144'], raws_p0['low'], d_threshold))):
            tc_id = 'pvpc_305_long'
        elif (pvpc_alignment_p0 in [6, 7] and
              pvpc_test_p0 == 72 and
              raws_p1['high'] > raws_p0['high'] and
              (utils.is_near(emas_p0['ema_close_17'], raws_p0['low'], d_threshold) or
               utils.is_near(emas_p0['ema_close_34'], raws_p0['low'], d_threshold) or
               utils.is_near(emas_p0['ema_close_72'], raws_p0['low'], d_threshold))):
            tc_id = 'pvpc_72_long'

        elif (pvpc_alignment_p0 in [0, 1] and
              pvpc_test_p0 == -1292 and
              ema_alignment_p0 and ema_alignment_p0 <= -144 and
              raws_p1['low'] < raws_p0['low'] and
              (utils.is_near(emas_p0['ema_close_72'], raws_p0['high'], d_threshold) or
               utils.is_near(emas_p0['ema_close_144'], raws_p0['high'], d_threshold))):
            tc_id = 'pvpc_1292_short'
        elif (pvpc_alignment_p0 in [0, 1] and
              pvpc_test_p0 == -305 and
              ema_alignment_p0 and ema_alignment_p0 <= -144 and
              raws_p1['low'] < raws_p0['low'] and
              (utils.is_near(emas_p0['ema_close_34'], raws_p0['high'], d_threshold) or
               utils.is_near(emas_p0['ema_close_72'], raws_p0['high'], d_threshold) or
               utils.is_near(emas_p0['ema_close_144'], raws_p0['high'], d_threshold))):
            tc_id = 'pvpc_305_short'
        elif (pvpc_alignment_p0 in [0, 1] and
              pvpc_test_p0 == -72 and
              ema_alignment_p0 and ema_alignment_p0 <= -144 and
              raws_p1['low'] < raws_p0['low'] and
              (utils.is_near(emas_p0['ema_close_17'], raws_p0['high'], d_threshold) or
               utils.is_near(emas_p0['ema_close_34'], raws_p0['high'], d_threshold) or
               utils.is_near(emas_p0['ema_close_72'], raws_p0['high'], d_threshold))):
            tc_id = 'pvpc_72_short'

        # debug
        # if datetime == '2017-11-14 00:00:00':
        #     print('Showing data related to: %s' % datetime)
        #     print('pvpc_alignment_p0: %s' % pvpc_alignment_p0)
        #     print('pvpc_test_p0: %s' % pvpc_test_p0)
        #     print('ema_alignment_p0: %s' % ema_alignment_p0)
        #     print('raws_p1[high]: %s | raws_p0[high]: %s' % (raws_p1['high'], raws_p0['high']))
        #     print('utils.is_near(emas_p0[ema_close_34], raws_p0[low]): %s' % utils.is_near(emas_p0['ema_close_34'],
        #                                                                                    raws_p0['low'],
        #                                                                                    d_threshold))
        #     print('utils.is_near(emas_p0[ema_close_72], raws_p0[low]): %s' % utils.is_near(emas_p0['ema_close_72'],
        #                                                                                    raws_p0['low'],
        #                                                                                    d_threshold))
        #     print(
        #         'utils.is_near(emas_p0[ema_close_144], raws_p0[low]): %s' % utils.is_near(emas_p0['ema_close_144'],
        #                                                                                   raws_p0['low'],
        #                                                                                   d_threshold))
        #     print('tc_id: %s' % tc_id)

        if tc_id:
            self.radar_on = datetime
            self.tc = models.TechnicalCondition.objects.get(pk=tc_id)

    def prepare_and_run(self, datetimes, highs, lows, last_pvpcs):
        i = datetimes.index(self.radar_on)

        # Buy
        if self.tc.id == 'pvpc_1292_long':
            self.prepare_1292_long(highs=highs[:i + 1], lows=lows[:i + 1], last_pvpcs=last_pvpcs)
        elif self.tc.id == 'pvpc_305_long':
            self.prepare_305_long(highs=highs[:i + 1], lows=lows[:i + 1], last_pvpcs=last_pvpcs)
        elif self.tc.id == 'pvpc_72_long':
            self.prepare_72_long(highs=highs[:i + 1], lows=lows[:i + 1], last_pvpcs=last_pvpcs)

        # Sell
        elif self.tc.id == 'pvpc_1292_short':
            self.prepare_1292_short(highs=highs[:i + 1], lows=lows[:i + 1], last_pvpcs=last_pvpcs)
        elif self.tc.id == 'pvpc_305_short':
            self.prepare_305_short(highs=highs[:i + 1], lows=lows[:i + 1], last_pvpcs=last_pvpcs)
        elif self.tc.id == 'pvpc_72_short':
            self.prepare_72_short(highs=highs[:i + 1], lows=lows[:i + 1], last_pvpcs=last_pvpcs)

        if self.target and self.stop_loss:
            # Run Simulation from next day on: [i + 1]
            self.run_simulation(datetimes[i + 1:], highs[i + 1:], lows[i + 1:],
                                extras={'get_entry_price': self.get_entry_price})

    def get_entry_price(self, high=None, low=None):
        if self.tc.type == 'long':
            entry_price = high + 0.01
        else:
            entry_price = low - 0.01

        return entry_price

    # setups
    def prepare_1292_long(self, highs, lows, last_pvpcs):
        last_index = len(highs) - 1

        # Entry Price
        high_today = highs[last_index]
        entry_price = self.get_entry_price(high=high_today)
        self.set_history_attr('entry_price', self.radar_on, entry_price)

        # Target
        fibonacci_obj = utils.fibonacci_projection(type=self.tc.type,
                                                   highs=highs,
                                                   lows=lows,
                                                   projection_percentage='auto',
                                                   min_periods_to_consider=34,
                                                   max_periods_to_consider=144,
                                                   inc_interval=6)
        self.fibonacci = fibonacci_obj
        target = fibonacci_obj['projection']
        self.set_history_attr('target', self.radar_on, target)

        # Stop Loss
        pv_1292 = last_pvpcs['pv_1292']
        stop_loss_pv1292 = round(pv_1292 * 0.98382, 2)
        low_yesterday = lows[last_index - 1]
        stop_loss = low_yesterday if low_yesterday <= stop_loss_pv1292 else stop_loss_pv1292
        self.set_history_attr('stop_loss', self.radar_on, stop_loss)

    def prepare_305_long(self, highs, lows, last_pvpcs):
        last_index = len(highs) - 1

        # Entry Price
        high_today = highs[last_index]
        entry_price = self.get_entry_price(high=high_today)
        self.set_history_attr('entry_price', self.radar_on, entry_price)

        # Target
        fibonacci_obj = utils.fibonacci_projection(type=self.tc.type,
                                                   highs=highs,
                                                   lows=lows,
                                                   projection_percentage='auto',
                                                   min_periods_to_consider=17,
                                                   max_periods_to_consider=72,
                                                   inc_interval=4)
        self.fibonacci = fibonacci_obj
        target = fibonacci_obj['projection']
        self.set_history_attr('target', self.radar_on, target)

        # Stop Loss
        pv_305 = last_pvpcs['pv_305']
        stop_loss_pv305 = round(pv_305 * 0.97382, 2)
        low_yesterday = round(lows[last_index - 1], 2)
        stop_loss = low_yesterday if low_yesterday <= stop_loss_pv305 else stop_loss_pv305
        self.set_history_attr('stop_loss', self.radar_on, stop_loss)

    def prepare_72_long(self, highs, lows, last_pvpcs):
        last_index = len(highs) - 1

        # Entry Price
        high_today = highs[last_index]
        entry_price = self.get_entry_price(high=high_today)
        self.set_history_attr('entry_price', self.radar_on, entry_price)

        # Target
        fibonacci_obj = utils.fibonacci_projection(type=self.tc.type,
                                                   highs=highs,
                                                   lows=lows,
                                                   projection_percentage='auto',
                                                   min_periods_to_consider=8,
                                                   max_periods_to_consider=72,
                                                   inc_interval=4)
        self.fibonacci = fibonacci_obj
        target = fibonacci_obj['projection']
        self.set_history_attr('target', self.radar_on, target)

        # Stop Loss
        pv_72 = last_pvpcs['pv_72']
        stop_loss_pv72 = round(pv_72 * 0.98382, 2)
        low_yesterday = round(lows[last_index - 1], 2)
        stop_loss = low_yesterday if low_yesterday <= stop_loss_pv72 else stop_loss_pv72
        self.set_history_attr('stop_loss', self.radar_on, stop_loss)

    def prepare_1292_short(self, highs, lows, last_pvpcs):
        last_index = len(highs) - 1

        # Entry Price
        low_today = lows[last_index]
        entry_price = self.get_entry_price(low=low_today)
        self.set_history_attr('entry_price', self.radar_on, entry_price)

        # Target
        fibonacci_obj = utils.fibonacci_projection(type=self.tc.type,
                                                   highs=highs,
                                                   lows=lows,
                                                   projection_percentage='auto',
                                                   min_periods_to_consider=34,
                                                   max_periods_to_consider=144,
                                                   inc_interval=6)

        self.fibonacci = fibonacci_obj
        target = fibonacci_obj['projection']
        self.set_history_attr('target', self.radar_on, target)

        # Stop Loss
        pc_1292 = last_pvpcs['pc_1292']
        stop_loss_pc_1292 = round(pc_1292 * 1.02618, 2)
        high_yesterday = round(highs[last_index - 1], 2)
        stop_loss = high_yesterday if high_yesterday >= stop_loss_pc_1292 else stop_loss_pc_1292
        self.set_history_attr('stop_loss', self.radar_on, stop_loss)

    def prepare_305_short(self, highs, lows, last_pvpcs):
        last_index = len(highs) - 1

        # Entry Price
        low_today = lows[last_index]
        entry_price = self.get_entry_price(low=low_today)
        self.set_history_attr('entry_price', self.radar_on, entry_price)

        # Target
        fibonacci_obj = utils.fibonacci_projection(type=self.tc.type,
                                                   highs=highs,
                                                   lows=lows,
                                                   projection_percentage='auto',
                                                   min_periods_to_consider=17,
                                                   max_periods_to_consider=72,
                                                   inc_interval=4)
        self.fibonacci = fibonacci_obj
        target = fibonacci_obj['projection']
        self.set_history_attr('target', self.radar_on, target)

        # Stop Loss
        pc_305 = last_pvpcs['pc_305']
        stop_loss_pc305 = round(pc_305 * 1.02618, 2)
        high_yesterday = round(highs[last_index - 1], 2)
        stop_loss = high_yesterday if high_yesterday >= stop_loss_pc305 else stop_loss_pc305
        self.set_history_attr('stop_loss', self.radar_on, stop_loss)

    def prepare_72_short(self, highs, lows, last_pvpcs):
        last_index = len(highs) - 1

        # Entry Price
        low_today = lows[last_index]
        entry_price = self.get_entry_price(low=low_today)
        self.set_history_attr('entry_price', self.radar_on, entry_price)

        # Target
        fibonacci_obj = utils.fibonacci_projection(type=self.tc.type,
                                                   highs=highs,
                                                   lows=lows,
                                                   projection_percentage='auto',
                                                   min_periods_to_consider=8,
                                                   max_periods_to_consider=72,
                                                   inc_interval=4)
        self.fibonacci = fibonacci_obj
        target = fibonacci_obj['projection']
        self.set_history_attr('target', self.radar_on, target)

        # Stop Loss
        pc_72 = last_pvpcs['pc_72']
        stop_loss_pc_72 = round(pc_72 * 1.02618, 2)
        high_yesterday = round(highs[last_index - 1], 2)
        stop_loss = high_yesterday if high_yesterday >= stop_loss_pc_72 else stop_loss_pc_72
        self.set_history_attr('stop_loss', self.radar_on, stop_loss)
