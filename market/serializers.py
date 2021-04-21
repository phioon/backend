from django.contrib.auth.models import User
from market import models
from django_engine.functions import utils as phioon_utils
from rest_framework import serializers


class TechnicalConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TechnicalCondition
        fields = '__all__'


class StockExchangeSerializer(serializers.ModelSerializer):
    assets = serializers.SerializerMethodField()

    class Meta:
        model = models.StockExchange
        fields = ['se_short', 'name', 'start_time', 'end_time', 'timezone',
                  'country_code', 'currency_code', 'website', 'assets']

    def get_assets(self, obj):
        return obj.assets.values_list('pk', flat=True)


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
    avg_volume_10d = serializers.ReadOnlyField(source='asset_volume_avg')
    pct_change = serializers.ReadOnlyField(source='realtime.pct_change')

    class Meta:
        model = models.Asset
        fields = ['stock_exchange', 'asset_symbol',
                  'asset_label', 'asset_name', 'country_code', 'sector_id',
                  'last_trade_time', 'open', 'high', 'low', 'price', 'avg_volume_10d', 'pct_change']

    def get_last_trade_time(self, obj):
        d_datetime = obj.d_raws.values('datetime').distinct().order_by('-datetime')[0]['datetime']

        if hasattr(obj, 'realtime') and obj.realtime.last_trade_time >= d_datetime:
            # There is Realtime instance AND it's newer than d_datetime
            last_trade_time = obj.realtime.last_trade_time
        else:
            # There is no Realtime instance OR it's older than d_datetime
            d_datetime = str(d_datetime)[0:10]
            last_trade_time = d_datetime + ' ' + str(obj.stock_exchange.end_time)
            last_trade_time = phioon_utils.convert_naive_to_utc(strDatetime=last_trade_time,
                                                                tz=obj.stock_exchange.timezone)
            last_trade_time = last_trade_time.strftime("%Y-%m-%d %H:%M:%S")

        return last_trade_time

    def get_open(self, obj):
        d_datetime = obj.d_raws.values('datetime').distinct().order_by('-datetime')[0]['datetime']

        if hasattr(obj, 'realtime') and obj.realtime.last_trade_time >= d_datetime:
            # There is Realtime instance AND it's newer than d_datetime
            open = obj.realtime.open
        else:
            # There is no Realtime instance OR it's older than d_datetime
            open = obj.d_raws.values('d_open').order_by('-datetime')[0]['d_open']

        return open

    def get_high(self, obj):
        d_datetime = obj.d_raws.values('datetime').distinct().order_by('-datetime')[0]['datetime']

        if hasattr(obj, 'realtime') and obj.realtime.last_trade_time >= d_datetime:
            # There is Realtime instance AND it's newer than d_datetime
            high = obj.realtime.high
        else:
            # There is no Realtime instance OR it's older than d_datetime
            high = obj.d_raws.values('d_high').order_by('-datetime')[0]['d_high']

        return high

    def get_low(self, obj):
        d_datetime = obj.d_raws.values('datetime').distinct().order_by('-datetime')[0]['datetime']

        if hasattr(obj, 'realtime') and obj.realtime.last_trade_time >= d_datetime:
            # There is Realtime instance AND it's newer than d_datetime
            low = obj.realtime.low
        else:
            # There is no Realtime instance OR it's older than d_datetime
            low = obj.d_raws.values('d_low').order_by('-datetime')[0]['d_low']

        return low

    def get_price(self, obj):
        d_datetime = obj.d_raws.values('datetime').distinct().order_by('-datetime')[0]['datetime']

        if hasattr(obj, 'realtime') and obj.realtime.last_trade_time >= d_datetime:
            # There is Realtime instance AND it's newer than d_datetime
            price = obj.realtime.price
        else:
            # There is no Realtime instance OR it's older than d_datetime
            price = obj.d_raws.values('d_close').order_by('-datetime')[0]['d_close']

        return price


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']
