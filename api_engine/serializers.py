from django.contrib.auth.models import User
from market.models import StockExchange, Asset, D_raw, TechnicalCondition, D_setup, D_setupSummary
from rest_framework import serializers


class TechnicalConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechnicalCondition
        fields = '__all__'


class StockExchangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockExchange
        fields = '__all__'


class AssetBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ['stockExchange', 'asset_symbol', 'asset_label', 'asset_name', 'asset_price']


class AssetDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = '__all__'


class D_rawBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = D_raw
        fields = ['id', 'd_datetime', 'asset_symbol', 'd_close']


class D_rawDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = D_raw
        fields = '__all__'


class D_setupSerializer(serializers.ModelSerializer):
    se_short = serializers.ReadOnlyField(source='d_raw.asset_symbol.stockExchange.se_short')
    asset_symbol = serializers.ReadOnlyField(source='d_raw.asset_symbol_id')
    asset_label = serializers.ReadOnlyField(source='d_raw.asset_symbol.asset_label')
    tc_id = serializers.ReadOnlyField(source='tc.id')

    class Meta:
        model = D_setup
        fields = ['id', 'se_short', 'asset_setup', 'asset_symbol', 'asset_label',
                  'started_on', 'ended_on', 'is_success', 'duration', 'tc_id',
                  'max_price', 'target', 'stop_loss', 'gain_percent', 'loss_percent', 'risk_reward',
                  'fibo_pct_retraction']


class D_setupSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = D_setupSummary
        fields = ['asset_setup', 'asset_symbol', 'tc_id',
                  'success_rate', 'avg_duration_gain', 'occurrencies',
                  'last_ended_occurrence', 'last_ended_duration', 'last_was_success']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']
