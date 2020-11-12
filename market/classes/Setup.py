from ..functions import utils


class Setup:
    tc = None

    started_on = None
    ended_on = None
    is_success = None
    duration = 0

    max_price = None
    target = None
    stop_loss = None
    gain_percent = None
    loss_percent = None
    risk_reward = None

    # Projection
    fibo_periods_needed = None
    fibo_p1 = fibo_p2 = fibo_p3 = None
    fibo_wave_1 = None
    fibo_retraction = None
    fibo_pct_retraction = None
    fibo_projection = None

    # Phibo
    @staticmethod
    def get_tcId_phibo(phibo_test_3p, phibo_alignment_3p, low_ema_btl_3p, high_ema_btl_3p, pivot, roc_ema8):
        low_ema_btl_yesterday = low_ema_btl_3p[1]
        high_ema_btl_yesterday = high_ema_btl_3p[1]
        phibo_test_yesterday = phibo_test_3p[1]
        phibo_alignment_yesterday = phibo_alignment_3p[1]

        if (phibo_alignment_yesterday in [6, 7] and
                phibo_test_yesterday == 1292 and
                low_ema_btl_yesterday in [4, 6] and
                pivot == 1):
            return 'phibo_1292_up'
        elif (phibo_alignment_yesterday in [6, 7] and
              phibo_test_yesterday == 305 and
              low_ema_btl_yesterday in [6, 7] and
              roc_ema8 > 0 and
              pivot == 1):
            return 'phibo_305_up'
        elif (phibo_alignment_yesterday in [6, 7] and
              phibo_test_yesterday == 72 and
              low_ema_btl_yesterday in [6, 7] and
              roc_ema8 > 0 and
              pivot == 1):
            return 'phibo_72_up'

        elif (phibo_alignment_yesterday in [0, 1] and
                phibo_test_yesterday == -1292 and
                high_ema_btl_yesterday in [1, 3] and
                pivot == -1):
            return 'phibo_1292_down'
        elif (phibo_alignment_yesterday in [0, 1] and
                phibo_test_yesterday == -305 and
                high_ema_btl_yesterday in [0, 1] and
                pivot == -1):
            return 'phibo_305_down'
        elif (phibo_alignment_yesterday in [0, 1] and
              phibo_test_yesterday == -72 and
              high_ema_btl_yesterday in [0, 1] and
              roc_ema8 < 0 and
              pivot == -1):
            return 'phibo_72_down'

    def create_phibo_setup(self, datetimes, highList, lowList, pvList, pcList):
        if self.tc is None:
            return

        i = datetimes.index(self.started_on)

        if self.tc.id == 'phibo_1292_up':
            self.phibo_1292_up(highList[:i + 1], lowList[:i + 1], pvList[:i + 1])
        elif self.tc.id == 'phibo_305_up':
            self.phibo_305_up(highList[:i + 1], lowList[:i + 1], pvList[:i + 1])
        elif self.tc.id == 'phibo_72_up':
            self.phibo_72_up(highList[:i + 1], lowList[:i + 1], pvList[:i + 1])

        elif self.tc.id == 'phibo_1292_down':
            self.phibo_1292_down(highList[:i + 1], lowList[:i + 1], pcList[:i + 1])
        elif self.tc.id == 'phibo_305_down':
            self.phibo_305_down(highList[:i + 1], lowList[:i + 1], pcList[:i + 1])
        elif self.tc.id == 'phibo_72_down':
            self.phibo_72_down(highList[:i + 1], lowList[:i + 1], pcList[:i + 1])

        # if self.tc.id and self.started_on == '2020-11-30 00:00:00':
        #     print('tc_id: %s || started_on: %s || %s || %s' % (self.tc.id, self.started_on, self.target, self.stop_loss))

        if self.target and self.stop_loss:
            self.run_setup(datetimes[i:], highList[i:], lowList[i:])

    # EMA
    @staticmethod
    def get_tcId_ema(ema_test_3p, low_ema_btl_3p, high_ema_btl_3p, pivot, roc_ema8):
        low_ema_btl_yesterday = low_ema_btl_3p[1]
        high_ema_btl_yesterday = high_ema_btl_3p[1]
        ema_test_yesterday = ema_test_3p[1]

        if (ema_test_yesterday == 610 and
                high_ema_btl_yesterday == 4 and
                pivot == 1):
            return 'ema_610_up'
        elif (ema_test_yesterday == 144 and
              high_ema_btl_yesterday == 6 and
              roc_ema8 > 0 and
              pivot == 1):
            return 'ema_144_up'
        if (ema_test_yesterday == -610 and
                low_ema_btl_yesterday == 3 and
                pivot == -1):
            return 'ema_610_down'
        elif (ema_test_yesterday == -144 and
              low_ema_btl_yesterday == 1 and
              roc_ema8 < 0 and
              pivot == -1):
            return 'ema_144_up'

    def create_ema_setup(self, datetimes, highList, lowList, emaList):
        if self.tc is None:
            return

        i = datetimes.index(self.started_on)

        if self.tc.id == 'ema_610_up':
            self.ema_610_up(highList[:i + 1], lowList[:i + 1], emaList[:i + 1])
        elif self.tc.id == 'ema_144_up':
            self.ema_144_up(highList[:i + 1], lowList[:i + 1], emaList[:i + 1])
        #
        # elif self.tc.id == 'ema_610_down':
        #     self.ema_610_down(highList[:i + 1], lowList[:i + 1], emaList[:i + 1])
        # elif self.tc.id == 'ema_144_down':
        #     self.ema_144_down(highList[:i + 1], lowList[:i + 1], emaList[:i + 1])

        # print('tc_id: %s || started_on: %s || %s || %s' % (self.tc.id, self.started_on, self.target, self.stop_loss))

        if self.target and self.stop_loss:
            self.run_setup(datetimes[i:], highList[i:], lowList[i:])

    # HISTORICAL DATA
    def run_setup(self, datetimes, highList, lowList):
        i = 0

        while self.ended_on is None and i < (len(datetimes)):
            self.duration += 1

            high = highList[i]
            low = lowList[i]

            if self.tc.type == 'purchase':
                # It's a PURCHASE setup

                if self.target <= high:
                    # It's a GAIN
                    self.ended_on = datetimes[i]
                    self.is_success = True
                elif self.stop_loss >= low:
                    # It's a LOSS
                    self.ended_on = datetimes[i]
                    self.is_success = False

            else:
                # It's a SALE setup

                if self.target >= low:
                    # It's a GAIN
                    self.ended_on = datetimes[i]
                    self.is_success = True
                elif self.stop_loss <= high:
                    # It's a LOSS
                    self.ended_on = datetimes[i]
                    self.is_success = False

            i += 1

    # PHIBO
    def phibo_1292_up(self, highList, lowList, pvList):
        last_index = len(highList) - 1

        # Max Price
        high_today = highList[last_index]
        low_today = lowList[last_index]

        self.max_price = round((high_today + low_today) / 2, 2)

        # Target
        pv72 = pvList[last_index][0]
        pv1292 = pvList[last_index][2]
        pvTarget = pv72 + (pv72 - pv1292)
        fiboProjection = utils.fibonacci_projection(type='buy',
                                                    highList=highList,
                                                    lowList=lowList,
                                                    projection_percentage=1,
                                                    min_periods_to_consider=34,
                                                    max_periods_to_consider=144,
                                                    inc_interval=4)

        self.store_fibonacci_projection(fiboProjection)
        self.target = round((pvTarget + fiboProjection['projection']) / 2, 2)

        # Stop Loss
        stop_loss_pv1292 = round(pv1292 * 0.97382, 2)
        low_yesterday = round(lowList[last_index - 1], 2)
        self.stop_loss = low_yesterday if low_yesterday <= stop_loss_pv1292 else stop_loss_pv1292

        # Gain Percent
        self.gain_percent = utils.gain_percent_buy(self.max_price, self.target)

        # Loss Percent
        self.loss_percent = utils.stop_loss_buy(self.max_price, self.stop_loss)

        # Risk Gain
        self.risk_reward = utils.risk_reward(self.gain_percent, self.loss_percent)

    def phibo_305_up(self, highList, lowList, pvList):
        last_index = len(highList) - 1

        # Max Price
        high_today = highList[last_index]
        low_today = lowList[last_index]
        self.max_price = round((high_today + low_today) / 2, 2)

        # Target
        fiboProjection = utils.fibonacci_projection(type='buy',
                                                    highList=highList,
                                                    lowList=lowList,
                                                    projection_percentage=1,
                                                    min_periods_to_consider=17,
                                                    max_periods_to_consider=72,
                                                    inc_interval=4)
        self.store_fibonacci_projection(fiboProjection)
        self.target = fiboProjection['projection']

        # Stop Loss
        pv305 = pvList[last_index][1]
        stop_loss_pv305 = round(pv305 * 0.97382, 2)
        low_yesterday = round(lowList[last_index - 1], 2)
        self.stop_loss = low_yesterday if low_yesterday <= stop_loss_pv305 else stop_loss_pv305

        # Gain Percent
        self.gain_percent = utils.gain_percent_buy(self.max_price, self.target)

        # Loss Percent
        self.loss_percent = utils.stop_loss_buy(self.max_price, self.stop_loss)

        # Risk Gain
        self.risk_reward = utils.risk_reward(self.gain_percent, self.loss_percent)

    def phibo_72_up(self, highList, lowList, pvList):
        last_index = len(highList) - 1

        # Max Price
        high_today = highList[last_index]
        low_today = lowList[last_index]
        self.max_price = round((high_today + low_today) / 2, 2)

        # Target
        fiboProjection = utils.fibonacci_projection(type='buy',
                                                    highList=highList,
                                                    lowList=lowList,
                                                    projection_percentage=0.95,
                                                    min_periods_to_consider=8,
                                                    max_periods_to_consider=34,
                                                    inc_interval=2)
        self.store_fibonacci_projection(fiboProjection)
        self.target = fiboProjection['projection']

        # Stop Loss
        pv72 = pvList[last_index][0]
        stop_loss_pv72 = round(pv72 * 0.98382, 2)
        low_yesterday = round(lowList[last_index - 1], 2)
        self.stop_loss = low_yesterday if low_yesterday <= stop_loss_pv72 else stop_loss_pv72

        # Gain Percent
        self.gain_percent = utils.gain_percent_buy(self.max_price, self.target)

        # Loss Percent
        self.loss_percent = utils.stop_loss_buy(self.max_price, self.stop_loss)

        # Risk Gain
        self.risk_reward = utils.risk_reward(self.gain_percent, self.loss_percent)

    def phibo_1292_down(self, highList, lowList, pcList):
        last_index = len(highList) - 1

        # Max Price
        high_today = highList[last_index]
        low_today = lowList[last_index]
        self.max_price = round((high_today + low_today) / 2, 2)

        # Target
        pc72 = pcList[last_index][0]
        pc1292 = pcList[last_index][2]
        pcTarget = pc72 - (pc1292 - pc72)
        fiboProjection = utils.fibonacci_projection(type='sell',
                                                    highList=highList,
                                                    lowList=lowList,
                                                    projection_percentage=0.7,
                                                    min_periods_to_consider=34,
                                                    max_periods_to_consider=144,
                                                    inc_interval=4)

        self.store_fibonacci_projection(fiboProjection)
        self.target = round((pcTarget + fiboProjection['projection']) / 2, 2)

        # Stop Loss
        stop_loss_pc1292 = round(pc1292 * 1.02618, 2)
        high_yesterday = round(highList[last_index - 1], 2)
        self.stop_loss = high_yesterday if high_yesterday >= stop_loss_pc1292 else stop_loss_pc1292

        # Gain Percent
        self.gain_percent = utils.gain_percent_sell(self.max_price, self.target)

        # Loss Percent
        self.loss_percent = utils.stop_loss_sell(self.max_price, self.stop_loss)

        # Risk Gain
        self.risk_reward = utils.risk_reward(self.gain_percent, self.loss_percent)

    def phibo_305_down(self, highList, lowList, pcList):
        last_index = len(highList) - 1

        # Max Price
        high_today = highList[last_index]
        low_today = lowList[last_index]
        self.max_price = round((high_today + low_today) / 2, 2)

        # Target
        fiboProjection = utils.fibonacci_projection(type='sell',
                                                    highList=highList,
                                                    lowList=lowList,
                                                    projection_percentage=0.7,
                                                    min_periods_to_consider=17,
                                                    max_periods_to_consider=72,
                                                    inc_interval=4)
        self.store_fibonacci_projection(fiboProjection)
        self.target = fiboProjection['projection']

        # Stop Loss
        pc305 = pcList[last_index][1]
        stop_loss_pc305 = round(pc305 * 1.02618, 2)
        high_yesterday = round(highList[last_index - 1], 2)
        self.stop_loss = high_yesterday if high_yesterday >= stop_loss_pc305 else stop_loss_pc305

        # Gain Percent
        self.gain_percent = utils.gain_percent_sell(self.max_price, self.target)

        # Loss Percent
        self.loss_percent = utils.stop_loss_sell(self.max_price, self.stop_loss)

        # Risk Gain
        self.risk_reward = utils.risk_reward(self.gain_percent, self.loss_percent)

    def phibo_72_down(self, highList, lowList, pcList):
        last_index = len(highList) - 1

        # Max Price
        high_today = highList[last_index]
        low_today = lowList[last_index]
        self.max_price = round((high_today + low_today) / 2, 2)

        # Target
        fiboProjection = utils.fibonacci_projection(type='sell',
                                                    highList=highList,
                                                    lowList=lowList,
                                                    projection_percentage=0.75,
                                                    min_periods_to_consider=8,
                                                    max_periods_to_consider=34,
                                                    inc_interval=2)
        self.store_fibonacci_projection(fiboProjection)
        self.target = fiboProjection['projection']

        # Stop Loss
        pc72 = pcList[last_index][0]
        stop_loss_pc72 = round(pc72 * 1.02618, 2)
        high_yesterday = round(highList[last_index - 1], 2)
        self.stop_loss = high_yesterday if high_yesterday >= stop_loss_pc72 else stop_loss_pc72

        # Gain Percent
        self.gain_percent = utils.gain_percent_sell(self.max_price, self.target)

        # Loss Percent
        self.loss_percent = utils.stop_loss_sell(self.max_price, self.stop_loss)

        # Risk Gain
        self.risk_reward = utils.risk_reward(self.gain_percent, self.loss_percent)

    # BTL EMA
    def btl_ema_7__trend_ema_144__buy(self, highList, lowList, closeList, pvList, closeEmaList):
        last_index = len(closeList) - 1

        # Max Price
        dayHigh = highList[last_index]
        yesterdayHigh = highList[last_index - 1]
        self.max_price = round((dayHigh + yesterdayHigh) / 2, 2)

        # Target
        fiboProjection = utils.fibonacci_projection('buy', highList, lowList, 1)
        self.store_fibonacci_projection(fiboProjection)
        self.target = fiboProjection['projection']

        # Stop Loss
        stop_loss__pv1292 = round(pvList[last_index][2] * 0.98786, 2) if pvList[last_index][2] is not None else 0.00
        stop_loss__ema34 = round(closeEmaList[last_index][0] * 1.01618, 2)
        stop_loss__pivot = round(closeList[last_index - 1] * 0.98786, 2)

        if stop_loss__pivot <= stop_loss__pv1292:
            self.stop_loss = stop_loss__pivot
        elif stop_loss__ema34 >= stop_loss__pv1292 and stop_loss__pv1292 <= lowList[last_index]:
            self.stop_loss = stop_loss__ema34
        else:
            self.stop_loss = stop_loss__pv1292

        # Gain Percent
        self.gain_percent = utils.gain_percent_buy(self.max_price, self.target)

        # Loss Percent
        self.loss_percent = utils.stop_loss_buy(self.max_price, self.stop_loss)

        # Risk Gain
        self.risk_reward = utils.risk_reward(self.gain_percent, self.loss_percent)

    # Utils
    def store_fibonacci_projection(self, fiboProjection):
        self.fibo_periods_needed = fiboProjection['periods_needed']
        self.fibo_p1 = fiboProjection['p1']
        self.fibo_p2 = fiboProjection['p2']
        self.fibo_p3 = fiboProjection['p3']
        self.fibo_wave_1 = fiboProjection['wave_1']
        self.fibo_retraction = fiboProjection['retraction']
        self.fibo_pct_retraction = fiboProjection['pct_retraction']
        self.fibo_projection = fiboProjection['projection']
