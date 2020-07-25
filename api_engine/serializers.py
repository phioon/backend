from django.contrib.auth.models import User
from market.models import StockExchange, Asset, D_raw, TechnicalCondition, D_setup, D_setupSummary
from rest_framework import serializers


class TechnicalConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechnicalCondition
        fields = '__all__'


class StockExchangeSerializer(serializers.ModelSerializer):
    assets = serializers.SerializerMethodField()

    class Meta:
        model = StockExchange
        fields = ['se_short', 'se_name', 'se_startTime', 'se_endTime', 'se_timezone',
                  'country_code', 'currency_code', 'assets']

    def get_assets(self, obj):
        return Asset.objects.filter(stockExchange=obj).values_list('pk', flat=True)


class AssetBasicSerializer(serializers.ModelSerializer):
    asset_label = serializers.ReadOnlyField(source='profile.asset_label')
    asset_name = serializers.ReadOnlyField(source='profile.asset_name')

    class Meta:
        model = Asset
        fields = ['stockExchange', 'asset_symbol',
                  'asset_label', 'asset_name']


class AssetDetailSerializer(serializers.ModelSerializer):
    asset_label = serializers.ReadOnlyField(source='profile.asset_label')
    asset_name = serializers.ReadOnlyField(source='profile.asset_name')
    country_code = serializers.ReadOnlyField(source='profile.country_code')
    sector_id = serializers.ReadOnlyField(source='profile.sector_id')

    asset_price = serializers.ReadOnlyField(source='realtime.price')
    asset_lastTradeTime = serializers.ReadOnlyField(source='realtime.last_trade_time')
    asset_pct_change = serializers.ReadOnlyField(source='realtime.pct_change')

    class Meta:
        model = Asset
        fields = ['stockExchange', 'asset_symbol',
                  'asset_label', 'asset_name', 'country_code', 'sector_id',
                  'asset_price', 'asset_lastTradeTime', 'asset_pct_change']


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
    asset_label = serializers.ReadOnlyField(source='d_raw.asset_symbol.profile.asset_label')
    asset_price = serializers.ReadOnlyField(source='d_raw.asset_symbol.realtime.price')
    tc_id = serializers.ReadOnlyField(source='tc.id')

    class Meta:
        model = D_setup
        fields = ['id', 'se_short', 'asset_setup',
                  'asset_symbol', 'asset_label', 'asset_price',
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
