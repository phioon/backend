from rest_framework import serializers

from market import models_d


class RawBasicSerializer(serializers.ModelSerializer):
    asset_symbol = serializers.ReadOnlyField(source='asset.asset_symbol')

    class Meta:
        model = models_d.D_raw
        fields = ['asset_symbol', 'datetime', 'd_close']


class RawDetailSerializer(serializers.ModelSerializer):
    asset_symbol = serializers.ReadOnlyField(source='asset.asset_symbol')

    class Meta:
        model = models_d.D_raw
        fields = ['asset_symbol', 'datetime', 'd_open', 'd_high', 'd_low', 'd_close', 'd_volume']


class PhiOperationSerializer(serializers.ModelSerializer):
    se_short = serializers.ReadOnlyField(source='raw.asset.stock_exchange.se_short')
    asset_symbol = serializers.ReadOnlyField(source='raw.asset.asset_symbol')
    asset_label = serializers.ReadOnlyField(source='raw.asset.profile.asset_label')
    tc_id = serializers.ReadOnlyField(source='tc.id')

    class Meta:
        model = models_d.D_phiOperation
        fields = ['id', 'se_short', 'asset_symbol', 'asset_label', 'tc_id',
                  'status', 'radar_on', 'started_on', 'ended_on', 'duration',
                  'entry_price', 'target', 'stop_loss', 'gain_percent', 'loss_percent', 'risk_reward',
                  'fibonacci']


class PhiStatsSerializer(serializers.ModelSerializer):
    asset_symbol = serializers.ReadOnlyField(source='asset.asset_symbol')
    tc_id = serializers.ReadOnlyField(source='tc.id')

    class Meta:
        model = models_d.D_phiStats
        fields = ['asset_symbol', 'tc_id', 'occurrencies',
                  'success_rate', 'avg_duration_gain',
                  'last_ended_occurrence', 'last_ended_duration', 'last_was_success']