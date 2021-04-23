from market import models as models_market
from django.db import models
from django.forms.models import model_to_dict


class M60_raw(models.Model):
    asset = models.ForeignKey(models_market.Asset, related_name='m60_raws', verbose_name='Asset Symbol', on_delete=models.CASCADE)
    asset_datetime = models.CharField(max_length=64, unique=True, db_index=True)  # (PETR4.SAO_20191231000000)
    datetime = models.CharField(max_length=32, db_index=True)
    m60_open = models.FloatField()
    m60_high = models.FloatField()
    m60_low = models.FloatField()
    m60_close = models.FloatField()
    m60_volume = models.BigIntegerField()

    def __str__(self):
        return self.asset_datetime

    def get_field_list(self, field_type='indicator'):
        # Possible entries for 'field_type': ['indicator']
        fields = []

        if field_type == 'indicator':
            fields = ['m60_open', 'm60_high', 'm60_low', 'm60_close']

        return fields

    @staticmethod
    def bulk_create(objs):
        M60_raw.objects.bulk_create(objs, ignore_conflicts=True)

    @staticmethod
    def bulk_update_or_create(objs):
        for x in range(len(objs)):
            M60_raw.objects.update_or_create(
                asset_datetime=objs[x].asset_datetime,
                defaults={'asset': objs[x].asset,
                          'datetime': objs[x].datetime,
                          'm60_open': objs[x].m60_open,
                          'm60_high': objs[x].m60_high,
                          'm60_low': objs[x].m60_low,
                          'm60_close': objs[x].m60_close,
                          'm60_volume': objs[x].m60_volume})


class M60_pvpc(models.Model):
    raw = models.OneToOneField(M60_raw, on_delete=models.CASCADE)
    asset_datetime = models.CharField(max_length=64, unique=True, db_index=True)  # (PETR4.SA_20191231000000)

    m60_pv_72 = models.FloatField(null=True)
    m60_pv_305 = models.FloatField(null=True)
    m60_pv_1292 = models.FloatField(null=True)

    m60_pc_72 = models.FloatField(null=True)
    m60_pc_305 = models.FloatField(null=True)
    m60_pc_1292 = models.FloatField(null=True)

    def __str__(self):
        return self.asset_datetime

    def get_field_list(self, field_type='indicator'):
        # Possible entries for 'field_type': ['indicator']
        fields = []

        if field_type == 'indicator':
            ignore_fields = ['id', 'raw', 'asset_datetime']
            for field in self._meta.fields:
                if field.name not in ignore_fields:
                    fields.append(field.name)

        return fields

    @staticmethod
    def bulk_create(objs):
        M60_pvpc.objects.bulk_create(objs, ignore_conflicts=True)

    @staticmethod
    def bulk_update_or_create(objs):
        for x in range(len(objs)):
            defaults = model_to_dict(objs[x], exclude=['id', 'asset_datetime'])
            defaults['raw'] = objs[x].raw

            M60_pvpc.objects.update_or_create(
                asset_datetime=objs[x].asset_datetime,
                defaults={**defaults})


class M60_ema(models.Model):
    raw = models.OneToOneField(M60_raw, db_index=True, on_delete=models.CASCADE)
    asset_datetime = models.CharField(max_length=64, unique=True, db_index=True)  # (PETR4.SA_20191231000000)

    m60_ema_close_8 = models.FloatField(null=True)
    m60_ema_close_9 = models.FloatField(null=True)
    m60_ema_close_17 = models.FloatField(null=True)
    m60_ema_close_34 = models.FloatField(null=True)
    m60_ema_close_50 = models.FloatField(null=True)
    m60_ema_close_72 = models.FloatField(null=True)
    m60_ema_close_144 = models.FloatField(null=True)
    m60_ema_close_200 = models.FloatField(null=True)
    m60_ema_close_305 = models.FloatField(null=True)
    m60_ema_close_610 = models.FloatField(null=True)
    m60_ema_close_1292 = models.FloatField(null=True)
    m60_ema_close_2584 = models.FloatField(null=True)

    def __str__(self):
        return self.asset_datetime

    def get_field_list(self, field_type='indicator'):
        # Possible entries for 'field_type': ['indicator']
        fields = []

        if field_type == 'indicator':
            ignore_fields = ['id', 'raw', 'asset_datetime']
            for field in self._meta.fields:
                if field.name not in ignore_fields:
                    fields.append(field.name)

        return fields

    @staticmethod
    def bulk_create(objs):
        M60_ema.objects.bulk_create(objs, ignore_conflicts=True)

    @staticmethod
    def bulk_update_or_create(objs):
        for x in range(len(objs)):
            defaults = model_to_dict(objs[x], exclude=['id', 'asset_datetime'])
            defaults['raw'] = objs[x].raw

            M60_ema.objects.update_or_create(
                asset_datetime=objs[x].asset_datetime,
                defaults={**defaults})


class M60_sma(models.Model):
    raw = models.OneToOneField(M60_raw, db_index=True, on_delete=models.CASCADE)
    asset_datetime = models.CharField(max_length=64, unique=True, db_index=True)  # (PETR4.SA_20191231000000)

    m60_sma_close_7 = models.FloatField(null=True)
    m60_sma_close_10 = models.FloatField(null=True)
    m60_sma_close_20 = models.FloatField(null=True)
    m60_sma_close_21 = models.FloatField(null=True)
    m60_sma_close_30 = models.FloatField(null=True)
    m60_sma_close_50 = models.FloatField(null=True)
    m60_sma_close_55 = models.FloatField(null=True)
    m60_sma_close_100 = models.FloatField(null=True)
    m60_sma_close_200 = models.FloatField(null=True)

    def __str__(self):
        return self.asset_datetime

    def get_field_list(self, field_type='indicator'):
        # Possible entries for 'field_type': ['indicator']
        fields = []

        if field_type == 'indicator':
            ignore_fields = ['id', 'raw', 'asset_datetime']
            for field in self._meta.fields:
                if field.name not in ignore_fields:
                    fields.append(field.name)

        return fields

    @staticmethod
    def bulk_create(objs):
        M60_sma.objects.bulk_create(objs, ignore_conflicts=True)

    @staticmethod
    def bulk_update_or_create(objs):
        for x in range(len(objs)):
            defaults = model_to_dict(objs[x], exclude=['id', 'asset_datetime'])
            defaults['raw'] = objs[x].raw

            M60_sma.objects.update_or_create(
                asset_datetime=objs[x].asset_datetime,
                defaults={**defaults})


class M60_roc(models.Model):
    raw = models.OneToOneField(M60_raw, verbose_name='Asset and Datetime', on_delete=models.CASCADE)
    asset_datetime = models.CharField(max_length=64, unique=True, db_index=True)  # (PETR4.SA_20191231000000)

    m60_roc_sma_close_7 = models.FloatField(null=True)
    m60_roc_sma_close_10 = models.FloatField(null=True)
    m60_roc_sma_close_20 = models.FloatField(null=True)
    m60_roc_sma_close_21 = models.FloatField(null=True)
    m60_roc_sma_close_30 = models.FloatField(null=True)
    m60_roc_sma_close_50 = models.FloatField(null=True)
    m60_roc_sma_close_55 = models.FloatField(null=True)
    m60_roc_sma_close_100 = models.FloatField(null=True)
    m60_roc_sma_close_200 = models.FloatField(null=True)

    m60_roc_ema_close_8 = models.FloatField(null=True)
    m60_roc_ema_close_9 = models.FloatField(null=True)
    m60_roc_ema_close_17 = models.FloatField(null=True)
    m60_roc_ema_close_34 = models.FloatField(null=True)
    m60_roc_ema_close_50 = models.FloatField(null=True)
    m60_roc_ema_close_72 = models.FloatField(null=True)
    m60_roc_ema_close_144 = models.FloatField(null=True)
    m60_roc_ema_close_200 = models.FloatField(null=True)
    m60_roc_ema_close_305 = models.FloatField(null=True)
    m60_roc_ema_close_610 = models.FloatField(null=True)
    m60_roc_ema_close_1292 = models.FloatField(null=True)
    m60_roc_ema_close_2584 = models.FloatField(null=True)

    def __str__(self):
        return self.asset_datetime

    def get_field_list(self, field_type='indicator'):
        # Possible entries for 'field_type': ['indicator']
        fields = []

        if field_type == 'indicator':
            ignore_fields = ['id', 'raw', 'asset_datetime']
            for field in self._meta.fields:
                if field.name not in ignore_fields:
                    fields.append(field.name)

        return fields

    @staticmethod
    def bulk_create(objs):
        M60_roc.objects.bulk_create(objs, ignore_conflicts=True)

    @staticmethod
    def bulk_update_or_create(objs):
        for x in range(len(objs)):
            defaults = model_to_dict(objs[x], exclude=['id', 'asset_datetime'])
            defaults['raw'] = objs[x].raw

            M60_roc.objects.update_or_create(
                asset_datetime=objs[x].asset_datetime,
                defaults={**defaults})


class M60_var(models.Model):
    raw = models.OneToOneField(M60_raw, verbose_name='Asset and Datetime', on_delete=models.CASCADE)
    asset_datetime = models.CharField(max_length=64, unique=True, db_index=True)  # (PETR4.SA_20191231000000)

    m60_var_ema_close_8_17 = models.FloatField(null=True, verbose_name='Percent variation between values')
    m60_var_ema_close_17_34 = models.FloatField(null=True, verbose_name='Percent variation between values')
    m60_var_ema_close_34_72 = models.FloatField(null=True, verbose_name='Percent variation between values')
    m60_var_ema_close_72_144 = models.FloatField(null=True, verbose_name='Percent variation between values')
    m60_var_ema_close_144_305 = models.FloatField(null=True, verbose_name='Percent variation between values')
    m60_var_ema_close_305_610 = models.FloatField(null=True, verbose_name='Percent variation between values')

    def __str__(self):
        return self.asset_datetime

    @staticmethod
    def bulk_create(objs):
        M60_var.objects.bulk_create(objs, ignore_conflicts=True)

    @staticmethod
    def bulk_update_or_create(objs):
        for x in range(len(objs)):
            defaults = model_to_dict(objs[x], exclude=['id', 'asset_datetime'])
            defaults['raw'] = objs[x].raw

            M60_var.objects.update_or_create(
                asset_datetime=objs[x].asset_datetime,
                defaults={**defaults})


class M60_tc(models.Model):
    raw = models.OneToOneField(M60_raw, on_delete=models.CASCADE)
    asset_datetime = models.CharField(max_length=64, unique=True, db_index=True)  # (PETR4.SAO_20191231000000)

    pivot = models.IntegerField(null=True)

    ema_btl_high = models.IntegerField(null=True)
    ema_btl_low = models.IntegerField(null=True)
    ema_btl_close = models.IntegerField(null=True)
    ema_alignment = models.IntegerField(null=True)
    ema_test = models.IntegerField(null=True)
    ema_trend = models.IntegerField(null=True)

    sma_test = models.IntegerField(null=True)

    pvpc_alignment = models.IntegerField(null=True)
    pvpc_test = models.IntegerField(null=True)

    def __str__(self):
        return self.asset_datetime

    @staticmethod
    def bulk_create(objs):
        M60_tc.objects.bulk_create(objs, ignore_conflicts=True)

    @staticmethod
    def bulk_update_or_create(objs):
        for x in range(len(objs)):
            defaults = model_to_dict(objs[x], exclude=['id', 'asset_datetime'])
            defaults['raw'] = objs[x].raw

            M60_tc.objects.update_or_create(asset_datetime=objs[x].asset_datetime,
                                            defaults={**defaults})


class M60_phiOperation(models.Model):
    raw = models.OneToOneField(M60_raw, on_delete=models.CASCADE)
    asset = models.ForeignKey(models_market.Asset, related_name='m60_phi_operations', on_delete=models.CASCADE)
    tc = models.ForeignKey(models_market.TechnicalCondition, related_name='m60_phi_operations', on_delete=models.CASCADE)

    status = models.CharField(max_length=32)
    is_public = models.BooleanField(null=True, default=None)

    radar_on = models.CharField(max_length=32)
    started_on = models.CharField(max_length=32, null=True)
    ended_on = models.CharField(max_length=32, null=True)
    duration = models.IntegerField(default=0)

    entry_price = models.JSONField(default=list)
    target = models.JSONField(default=list)
    stop_loss = models.JSONField(default=list)
    gain_percent = models.JSONField(default=list)
    loss_percent = models.JSONField(default=list)
    risk_reward = models.JSONField(default=list)

    fibonacci = models.JSONField(default=dict)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['asset', 'radar_on'], name='m60_phioperation__asset_datetime')
        ]

    def __str__(self):
        return str(self.asset.asset_symbol + ' ' + self.tc.id)

    @property
    def last_entry_price(self):
        if len(self.entry_price) > 0:
            value = self.entry_price[-1]['value']
        else:
            value = None

        return value

    @property
    def last_target(self):
        if len(self.target) > 0:
            value = self.target[-1]['value']
        else:
            value = None

        return value

    @property
    def last_stop_loss(self):
        if len(self.stop_loss) > 0:
            value = self.stop_loss[-1]['value']
        else:
            value = None

        return value

    @property
    def last_gain_percent(self):
        if len(self.gain_percent) > 0:
            value = self.gain_percent[-1]['value']
        else:
            value = None

        return value

    @property
    def last_loss_percent(self):
        if len(self.loss_percent) > 0:
            value = self.loss_percent[-1]['value']
        else:
            value = None

        return value

    @property
    def last_risk_reward(self):
        if len(self.risk_reward) > 0:
            value = self.risk_reward[-1]['value']
        else:
            value = None

        return value

    @staticmethod
    def bulk_update_or_create(objs):
        for x in range(len(objs)):
            defaults = model_to_dict(objs[x], exclude=['id', 'asset', 'tc', 'radar_on'])
            defaults['raw'] = objs[x].raw
            defaults['tc'] = objs[x].tc

            M60_phiOperation.objects.update_or_create(asset=objs[x].asset,
                                                      radar_on=objs[x].radar_on,
                                                      defaults={**defaults})


class M60_phiStats(models.Model):
    asset = models.ForeignKey(models_market.Asset, db_index=True, on_delete=models.CASCADE)
    tc = models.ForeignKey(models_market.TechnicalCondition, on_delete=models.CASCADE)

    has_open_position = models.BooleanField(default=False)

    occurrencies = models.IntegerField(default=0)
    gain_count = models.IntegerField(default=0)
    loss_count = models.IntegerField(default=0)
    canceled_count = models.IntegerField(default=0)
    success_rate = models.FloatField(default=0)
    avg_duration_gain = models.IntegerField(null=True)
    avg_duration_loss = models.IntegerField(null=True)

    last_ended_occurrence = models.CharField(max_length=32, null=True)
    last_ended_duration = models.IntegerField(null=True)
    last_was_success = models.BooleanField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['asset', 'tc'], name='m60_phistats__asset_tc')
        ]

    def __str__(self):
        return str(self.asset.asset_symbol + ' ' + self.tc.id)

    @staticmethod
    def bulk_update_or_create(objs):
        for x in range(len(objs)):
            defaults = model_to_dict(objs[x], exclude=['id', 'asset', 'tc'])

            M60_phiStats.objects.update_or_create(asset=objs[x].asset,
                                                  tc=objs[x].tc,
                                                  defaults={**defaults})
