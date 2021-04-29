from market import models_m60
from rest_framework import serializers


class RawSerializer(serializers.ModelSerializer):
    asset_symbol = serializers.ReadOnlyField(source='asset.asset_symbol')

    class Meta:
        model = models_m60.M60_raw
        fields = ['asset_symbol', 'datetime', 'm60_open', 'm60_high', 'm60_low', 'm60_close', 'm60_volume']


class PhiOperationSerializer(serializers.ModelSerializer):
    se_short = serializers.ReadOnlyField(source='raw.asset.stock_exchange.se_short')
    asset_symbol = serializers.ReadOnlyField(source='raw.asset.asset_symbol')
    asset_label = serializers.ReadOnlyField(source='raw.asset.profile.asset_label')
    tc_id = serializers.ReadOnlyField(source='tc.id')

    class Meta:
        model = models_m60.M60_phiOperation
        fields = ['id', 'se_short', 'asset_symbol', 'asset_label', 'tc_id',
                  'status', 'radar_on', 'started_on', 'ended_on', 'duration',
                  'entry_price', 'target', 'stop_loss', 'gain_percent', 'loss_percent', 'risk_reward',
                  'fibonacci']


class PhiStatsSerializer(serializers.ModelSerializer):
    asset_symbol = serializers.ReadOnlyField(source='asset.asset_symbol')
    tc_id = serializers.ReadOnlyField(source='tc.id')

    class Meta:
        model = models_m60.M60_phiStats
        fields = ['asset_symbol', 'tc_id', 'occurrencies',
                  'success_rate', 'avg_duration_gain',
                  'last_ended_occurrence', 'last_ended_duration', 'last_was_success']
