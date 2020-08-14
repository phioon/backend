from django.contrib.auth.models import User
from . import models
from rest_framework import serializers


class TechnicalConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TechnicalCondition
        fields = '__all__'


class StockExchangeSerializer(serializers.ModelSerializer):
    assets = serializers.SerializerMethodField()

    class Meta:
        model = models.StockExchange
        fields = ['se_short', 'se_name', 'se_startTime', 'se_endTime', 'se_timezone',
                  'country_code', 'currency_code', 'website', 'assets']

    def get_assets(self, obj):
        return models.Asset.objects.filter(stockExchange=obj).values_list('pk', flat=True)


class AssetBasicSerializer(serializers.ModelSerializer):
    asset_label = serializers.ReadOnlyField(source='profile.asset_label')
    asset_name = serializers.ReadOnlyField(source='profile.asset_name')
    asset_price = serializers.ReadOnlyField(source='realtime.price')

    class Meta:
        model = models.Asset
        fields = ['stockExchange', 'asset_symbol',
                  'asset_label', 'asset_name', 'asset_price']


class AssetDetailSerializer(serializers.ModelSerializer):
    asset_label = serializers.ReadOnlyField(source='profile.asset_label')
    asset_name = serializers.ReadOnlyField(source='profile.asset_name')
    country_code = serializers.ReadOnlyField(source='profile.country_code')
    sector_id = serializers.ReadOnlyField(source='profile.sector_id')

    asset_price = serializers.ReadOnlyField(source='realtime.price')
    asset_lastTradeTime = serializers.ReadOnlyField(source='realtime.last_trade_time')
    asset_pct_change = serializers.ReadOnlyField(source='realtime.pct_change')

    class Meta:
        model = models.Asset
        fields = ['stockExchange', 'asset_symbol',
                  'asset_label', 'asset_name', 'country_code', 'sector_id',
                  'asset_price', 'asset_lastTradeTime', 'asset_pct_change']


class D_rawBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.D_raw
        fields = ['asset_symbol', 'd_datetime', 'd_close', 'd_volume']


class D_rawDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.D_raw
        fields = '__all__'


class D_pvpcSerializer(serializers.ModelSerializer):
    asset_symbol = serializers.ReadOnlyField(source='d_raw.asset_symbol.asset_symbol')
    d_datetime = serializers.ReadOnlyField(source='d_raw.d_datetime')

    class Meta:
        model = models.D_pvpc
        fields = ['asset_symbol', 'd_datetime',
                  'd_pv72', 'd_pv305', 'd_pv1292',
                  'd_pc72', 'd_pc305', 'd_pc1292']


class D_emaSerializer(serializers.ModelSerializer):
    asset_symbol = serializers.ReadOnlyField(source='d_raw.asset_symbol.asset_symbol')
    d_datetime = serializers.ReadOnlyField(source='d_raw.d_datetime')

    class Meta:
        model = models.D_ema
        fields = ['asset_symbol', 'd_datetime',
                  'd_ema_close17', 'd_ema_close34', 'd_ema_close72',
                  'd_ema_close144', 'd_ema_close305', 'd_ema_close610']


class D_setupSerializer(serializers.ModelSerializer):
    se_short = serializers.ReadOnlyField(source='d_raw.asset_symbol.stockExchange.se_short')
    asset_symbol = serializers.ReadOnlyField(source='d_raw.asset_symbol_id')
    tc_id = serializers.ReadOnlyField(source='tc.id')

    class Meta:
        model = models.D_setup
        fields = ['id', 'se_short', 'asset_setup', 'asset_symbol',
                  'started_on', 'ended_on', 'is_success', 'duration', 'tc_id',
                  'max_price', 'target', 'stop_loss', 'gain_percent', 'loss_percent', 'risk_reward',
                  'fibo_pct_retraction']


class D_setupSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.D_setupSummary
        fields = ['asset_setup', 'asset_symbol', 'tc_id',
                  'success_rate', 'avg_duration_gain', 'occurrencies',
                  'last_ended_occurrence', 'last_ended_duration', 'last_was_success']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']
