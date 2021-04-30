from django.db.models import F
from market import models as market_models
from rest_framework import serializers
from . import messages


class ExchangeSerializer(serializers.ModelSerializer):
    symbol = serializers.ReadOnlyField(source='se_short')
    name = serializers.ReadOnlyField(source='name')
    timezone = serializers.ReadOnlyField(source='timezone')
    market_start_time = serializers.ReadOnlyField(source='start_time')
    market_end_time = serializers.ReadOnlyField(source='end_time')

    class Meta:
        model = market_models.StockExchange
        fields = ['symbol', 'name', 'website', 'country_code', 'currency_code',
                  'timezone', 'market_start_time', 'market_end_time']


class TickersByExchangeSerializer(serializers.ModelSerializer):
    exchange = serializers.ReadOnlyField(source='se_short')
    tickers = serializers.SerializerMethodField()

    class Meta:
        model = market_models.StockExchange
        fields = ['exchange', 'tickers']

    def get_tickers(self, obj):
        return market_models.Asset.objects.filter(stock_exchange=obj) \
            .exclude(profile__asset_name=None) \
            .annotate(symbol=F('pk'),
                      name=F('profile__asset_name')) \
            .values('symbol', 'name')


class ProfileSerializer(serializers.ModelSerializer):
    asset_symbol = serializers.ReadOnlyField(source='asset.asset_symbol')

    class Meta:
        model = market_models.Profile
        fields = ['asset_symbol', 'asset_name', 'country_code', 'sector_name', 'website', 'business_summary']


class RealtimeSerializer(serializers.ModelSerializer):
    asset_symbol = serializers.ReadOnlyField(source='asset.asset_symbol')
    pct_change_day = serializers.ReadOnlyField(source='pct_change')

    class Meta:
        model = market_models.Realtime
        fields = ['asset_symbol', 'last_trade_time', 'open', 'high', 'low', 'price', 'volume', 'pct_change_day']


class EodSerializer(serializers.ModelSerializer):
    asset_name = serializers.ReadOnlyField(source='profile.asset_name')
    stock_exchange = serializers.SerializerMethodField()
    eod = serializers.SerializerMethodField()

    class Meta:
        model = market_models.Asset
        fields = ['asset_symbol', 'asset_name', 'stock_exchange', 'eod']

    def get_stock_exchange(self, obj):
        return market_models.StockExchange.objects.filter(pk=obj.stock_exchange) \
            .annotate(symbol=F('pk')) \
            .values('symbol', 'name', 'timezone', 'country_code', 'currency_code')

    def get_eod(self, obj):
        default_limit = 100                 # When not specified, considers this value

        limit = self.context['request'].query_params.get('limit')

        if limit:
            try:
                limit = int(limit)
            except ValueError:
                obj_res = {'message': messages.get_message('enUS', 'eodlist', 'invalid_limit')}
                raise serializers.ValidationError(obj_res)
        else:
            # Limit not specified
            limit = default_limit

        result = obj.d_raws.annotate(stock_exchange=F('asset__stock_exchange'),
                                     open=F('d_open'),
                                     high=F('d_high'),
                                     low=F('d_low'),
                                     close=F('d_close'),
                                     adj_close=F('d_close'),
                                     volume=F('d_volume'),) \
            .values('stock_exchange', 'asset', 'datetime', 'open', 'high', 'low', 'close', 'adj_close', 'volume') \
            .order_by('-datetime')

        if limit > 0:
            result = result[:limit]

        return result


class M60Serializer(serializers.ModelSerializer):
    asset_name = serializers.ReadOnlyField(source='profile.asset_name')
    stock_exchange = serializers.SerializerMethodField()
    m60 = serializers.SerializerMethodField()

    class Meta:
        model = market_models.Asset
        fields = ['asset_symbol', 'asset_name', 'stock_exchange', 'm60']

    def get_stock_exchange(self, obj):
        return market_models.StockExchange.objects.filter(pk=obj.stock_exchange) \
            .annotate(symbol=F('pk')) \
            .values('symbol', 'name', 'timezone', 'country_code', 'currency_code')

    def get_m60(self, obj):
        default_limit = 100                 # When not specified, considers this value

        limit = self.context['request'].query_params.get('limit')

        if limit:
            try:
                limit = int(limit)
            except ValueError:
                obj_res = {'message': messages.get_message('enUS', 'eodlist', 'invalid_limit')}
                raise serializers.ValidationError(obj_res)
        else:
            # Limit not specified
            limit = default_limit

        result = obj.m60_raws.annotate(stock_exchange=F('asset__stock_exchange'),
                                       open=F('m60_open'),
                                       high=F('m60_high'),
                                       low=F('m60_low'),
                                       close=F('m60_close'),
                                       adj_close=F('m60_close'),
                                       volume=F('m60_volume'),) \
            .values('stock_exchange', 'asset', 'datetime', 'open', 'high', 'low', 'close', 'adj_close', 'volume') \
            .order_by('-datetime')

        if limit > 0:
            result = result[:limit]

        return result
