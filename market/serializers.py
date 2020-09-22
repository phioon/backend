from django.contrib.auth.models import User
from . import models
from .functions import utils as phioon_utils
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

    asset_lastTradeTime = serializers.ReadOnlyField(source='realtime.last_trade_time')
    asset_high = serializers.ReadOnlyField(source='realtime.high')
    asset_low = serializers.ReadOnlyField(source='realtime.low')
    asset_price = serializers.ReadOnlyField(source='realtime.price')

    class Meta:
        model = models.Asset
        fields = ['stockExchange', 'asset_symbol',
                  'asset_label', 'asset_name',
                  'asset_lastTradeTime', 'asset_high', 'asset_low', 'asset_price']


class AssetDetailSerializer(serializers.ModelSerializer):
    asset_label = serializers.ReadOnlyField(source='profile.asset_label')
    asset_name = serializers.ReadOnlyField(source='profile.asset_name')
    country_code = serializers.ReadOnlyField(source='profile.country_code')
    sector_id = serializers.ReadOnlyField(source='profile.sector_id')

    last_trade_time = serializers.SerializerMethodField()
    open = serializers.SerializerMethodField()
    high = serializers.SerializerMethodField()
    low = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    pct_change = serializers.ReadOnlyField(source='realtime.pct_change')

    class Meta:
        model = models.Asset
        fields = ['stockExchange', 'asset_symbol',
                  'asset_label', 'asset_name', 'country_code', 'sector_id',
                  'last_trade_time', 'open', 'high', 'low', 'price', 'pct_change']

    def get_last_trade_time(self, obj):
        if hasattr(obj, 'realtime'):
            # Check if Asset has Realtime instance
            last_trade_time = obj.realtime.last_trade_time
        else:
            # There is no Realtime instance...
            d_datetime = obj.draws.values('d_datetime').distinct().order_by('-d_datetime')[0]['d_datetime']
            d_datetime = str(d_datetime)[0:10]
            last_trade_time = d_datetime + ' ' + str(obj.stockExchange.se_endTime)
            last_trade_time = phioon_utils.convert_naive_to_utc(strDatetime=last_trade_time,
                                                                tz=obj.stockExchange.se_timezone)
            last_trade_time = last_trade_time.strftime("%Y-%m-%d %H:%M:%S")

        return last_trade_time

    def get_open(self, obj):
        if hasattr(obj, 'realtime'):
            # Check if Asset has Realtime instance
            open = obj.realtime.open
        else:
            # There is no Realtime instance...
            open = obj.draws.values('d_open').order_by('-d_datetime')[0]['d_open']

        return open

    def get_high(self, obj):
        if hasattr(obj, 'realtime'):
            # Check if Asset has Realtime instance
            high = obj.realtime.high
        else:
            # There is no Realtime instance...
            high = obj.draws.values('d_high').order_by('-d_datetime')[0]['d_high']

        return high

    def get_low(self, obj):
        if hasattr(obj, 'realtime'):
            # Check if Asset has Realtime instance
            low = obj.realtime.low
        else:
            # There is no Realtime instance...
            low = obj.draws.values('d_low').order_by('-d_datetime')[0]['d_low']

        return low

    def get_price(self, obj):
        if hasattr(obj, 'realtime'):
            # Check if Asset has Realtime instance
            price = obj.realtime.price
        else:
            # There is no Realtime instance...
            price = obj.draws.values('d_close').order_by('-d_datetime')[0]['d_close']

        return price


class D_rawBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.D_raw
        fields = ['asset_symbol', 'd_datetime', 'd_close', 'd_volume']


class D_rawDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.D_raw
        fields = ['asset_symbol', 'd_datetime', 'd_open', 'd_high', 'd_low', 'd_close', 'd_volume']


class D_pvpcSerializer(serializers.ModelSerializer):
    asset_symbol = serializers.ReadOnlyField(source='d_raw.asset_symbol.asset_symbol')
    d_datetime = serializers.ReadOnlyField(source='d_raw.d_datetime')

    class Meta:
        model = models.D_pvpc
        fields = ['asset_symbol', 'd_datetime',
                  'd_pv72', 'd_pv305', 'd_pv1292',
                  'd_pc72', 'd_pc305', 'd_pc1292']


class D_setupSerializer(serializers.ModelSerializer):
    se_short = serializers.ReadOnlyField(source='d_raw.asset_symbol.stockExchange.se_short')
    asset_symbol = serializers.ReadOnlyField(source='d_raw.asset_symbol_id')
    asset_label = serializers.ReadOnlyField(source='d_raw.asset_symbol.profile.asset_label')
    tc_id = serializers.ReadOnlyField(source='tc.id')

    class Meta:
        model = models.D_setup
        fields = ['id', 'se_short', 'asset_setup', 'asset_symbol', 'asset_label',
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
