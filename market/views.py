from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework import generics, permissions
from rest_framework.response import Response

from django_engine.functions import generic, utils as phioon_utils
from django_engine import settings
from market.managers.RawDataManager import RawDataManager
from market import serializers
from market import models as models_market
from market import models_d, models_m60

import re


# INIT
def market_init(request, apiKey=None):
    if apiKey == settings.API_KEY:
        generic.app_initiator()
        return HttpResponse()
    else:
        return HttpResponse(status=403)


class TechnicalConditionList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.TechnicalConditionSerializer
    queryset = models_market.TechnicalCondition.objects.all()


# Class created to add support to a Stock Exchange in a friendly way (by a human).
# Used only if it's necessary.
class StockExchangeList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.StockExchangeSerializer

    def get_queryset(self):
        return models_market.StockExchange.objects.filter(pk__in=settings.MARKET_SE_LIST)


# Integration between Backend and Frontend
class AssetList(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        stock_exchange = assets = detailed = None

        if 'assets' in request.data:
            assets = request.data['assets']
        if 'stockExchange' in request.data:
            stock_exchange = request.data['stockExchange']
        if 'detailed' in request.data:
            detailed = str(request.data['detailed']).lower()

        if assets:
            if detailed == 'true':
                # Log into DB last_access_time. It is used for tracking usage of assets
                raw_data_manager = RawDataManager()
                raw_data_manager.update_last_access_time(assets=assets)

            assets = models_market.Asset.objects.filter(asset_symbol__in=assets)
        else:
            assets = models_market.Asset.objects.filter(stock_exchange__se_short__exact=stock_exchange)

        serializer = serializers.AssetDetailSerializer(assets, many=True)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def IndicatorList(request):
    result = {}

    # 1.  Requirements
    # 1.1 Raw
    d_raw_fields = models_d.D_raw().get_field_list(field_type='indicator')
    m60_raw_fields = models_m60.M60_raw().get_field_list(field_type='indicator')
    raw_fields = d_raw_fields + m60_raw_fields
    # 1.2 SMA
    d_sma_fields = models_d.D_sma().get_field_list(field_type='indicator')
    m60_sma_fields = models_m60.M60_sma().get_field_list(field_type='indicator')
    sma_fields = d_sma_fields + m60_sma_fields
    # 1.3 EMA
    d_ema_fields = models_d.D_ema().get_field_list(field_type='indicator')
    m60_ema_fields = models_m60.M60_ema().get_field_list(field_type='indicator')
    ema_fields = d_ema_fields + m60_ema_fields
    # 1.4 PVPC
    d_pvpc_fields = models_d.D_pvpc().get_field_list(field_type='indicator')
    # 1.5 ROC
    d_roc_fields = models_d.D_roc().get_field_list(field_type='indicator')

    # 2 Price Lagging
    # 2.1 Quote
    category = 'price_lagging'
    subcategory = 'quote'
    indicator = 'quote'
    related_to = None
    for field_name in raw_fields:
        periods = 0
        time_interval, generic_id,  = field_name.split('_', maxsplit=1)

        if generic_id not in result.keys():
            # Create it
            result[generic_id] = {
                'id': generic_id,
                'instances': [],
                'category': category,
                'subcategory': subcategory,
                'indicator': indicator,
                'related_to': related_to,
                'periods': periods
            }

        result[generic_id]['instances'].append({
            'name': field_name,
            'interval': time_interval})

    # 2.2 SMA
    category = 'price_lagging'
    subcategory = 'moving_average'
    indicator = 'sma'
    related_to = None
    for field_name in sma_fields:
        periods = int(re.findall('[0-9]+', field_name)[0])
        time_interval, generic_id, = field_name.split('_', maxsplit=1)

        if '_open' in generic_id:
            related_to = 'open'
        elif '_high' in generic_id:
            related_to = 'high'
        elif '_low' in generic_id:
            related_to = 'low'
        elif '_close' in generic_id:
            related_to = 'close'

        if generic_id not in result.keys():
            # Create it
            result[generic_id] = {
                'id': generic_id,
                'instances': [],
                'category': category,
                'subcategory': subcategory,
                'indicator': indicator,
                'related_to': related_to,
                'periods': periods
            }

        result[generic_id]['instances'].append({
            'name': field_name,
            'interval': time_interval
        })

    # 2.3 EMA
    category = 'price_lagging'
    subcategory = 'moving_average'
    indicator = 'ema'
    related_to = None
    for field_name in ema_fields:
        periods = int(re.findall('[0-9]+', field_name)[0])
        time_interval, generic_id, = field_name.split('_', maxsplit=1)

        if '_open' in generic_id:
            related_to = 'open'
        elif '_high' in generic_id:
            related_to = 'high'
        elif '_low' in generic_id:
            related_to = 'low'
        elif '_close' in generic_id:
            related_to = 'close'

        if generic_id not in result.keys():
            # Create it
            result[generic_id] = {
                'id': generic_id,
                'instances': [],
                'category': category,
                'subcategory': subcategory,
                'indicator': indicator,
                'related_to': related_to,
                'periods': periods
            }

        result[generic_id]['instances'].append({
            'name': field_name,
            'interval': time_interval
        })

    # 2.4 Phibo PVPC
    category = 'price_lagging'
    subcategory = 'phibo'
    indicator = 'phibo'
    related_to = None
    for field_name in d_pvpc_fields:
        periods = int(re.findall('[0-9]+', field_name)[0])
        time_interval, generic_id, = field_name.split('_', maxsplit=1)

        if generic_id not in result.keys():
            # Create it
            result[generic_id] = {
                'id': generic_id,
                'instances': [],
                'category': category,
                'subcategory': subcategory,
                'indicator': indicator,
                'related_to': related_to,
                'periods': periods
            }

        result[generic_id]['instances'].append({
            'name': field_name,
            'interval': time_interval
        })

    # 2.5 Centered Oscillator: ROC
    category = 'centered_oscillator'
    subcategory = 'roc'
    indicator = 'roc'
    related_to = None
    for field_name in d_roc_fields:
        periods = int(re.findall('[0-9]+', field_name)[0])
        time_interval, generic_id, = field_name.split('_', maxsplit=1)

        if '_ema' in generic_id:
            related_to = 'ema'
        elif '_sma' in generic_id:
            related_to = 'sma'

        if generic_id not in result.keys():
            # Create it
            result[generic_id] = {
                'id': generic_id,
                'instances': [],
                'category': category,
                'subcategory': subcategory,
                'indicator': indicator,
                'related_to': related_to,
                'periods': periods
            }

        result[generic_id]['instances'].append({
            'name': field_name,
            'interval': time_interval
        })

    result = result.values()
    return Response(result)
