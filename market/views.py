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
from market import models_d

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
    result = []

    # Requirements
    d_raw_fields = models_d.D_raw().get_field_list(field_type='indicator')
    d_sma_fields = models_d.D_sma().get_field_list(field_type='indicator')
    d_ema_fields = models_d.D_ema().get_field_list(field_type='indicator')
    d_pvpc_fields = models_d.D_pvpc().get_field_list(field_type='indicator')
    d_roc_fields = models_d.D_roc().get_field_list(field_type='indicator')

    # 1. Constant
    # obj = {
    #     'time_interval': 'any',
    #     'category': 'constant',
    #     'subcategory': 'constant',
    #     'indicator': 'constant',
    #     'periods': 0,
    #     'id': 'constant',
    #     'instances': [{}],
    # }

    # 2. Daily
    time_interval = 'd'
    # 2.1 Price Lagging: Quote
    category = 'price_lagging'
    subcategory = 'quote'
    indicator = 'quote'
    related_to = None
    for field_name in d_raw_fields:
        periods = 0
        generic_id = field_name[field_name.index('_') + 1:]

        obj = phioon_utils.retrieve_obj_from_obj_list(result, 'id', generic_id)
        if not obj:
            # Create it
            obj = {
                'id': generic_id,
                'instances': [],
                'category': category,
                'subcategory': subcategory,
                'indicator': indicator,
                'related_to': related_to,
                'periods': periods
            }

        obj['instances'].append({
            'name': field_name,
            'interval': time_interval
        })
        result.append(obj)

    # 2.2 Price Lagging: SMA
    category = 'price_lagging'
    subcategory = 'moving_average'
    indicator = 'sma'
    related_to = None
    for field_name in d_sma_fields:
        periods = int(re.findall('[0-9]+', field_name)[0])
        generic_id = str(field_name)[str(field_name).index('_') + 1:]

        if '_open' in generic_id:
            related_to = 'open'
        elif '_high' in generic_id:
            related_to = 'high'
        elif '_low' in generic_id:
            related_to = 'low'
        elif '_close' in generic_id:
            related_to = 'close'

        obj = phioon_utils.retrieve_obj_from_obj_list(result, 'id', generic_id)
        if not obj:
            # Create it
            obj = {
                'id': generic_id,
                'instances': [],
                'category': category,
                'subcategory': subcategory,
                'indicator': indicator,
                'related_to': related_to,
                'periods': periods
            }

        obj['instances'].append({
            'name': field_name,
            'interval': time_interval
        })
        result.append(obj)

    # 2.3 Price Lagging: EMA
    category = 'price_lagging'
    subcategory = 'moving_average'
    indicator = 'ema'
    related_to = None
    for field_name in d_ema_fields:
        periods = int(re.findall('[0-9]+', field_name)[0])
        generic_id = str(field_name)[str(field_name).index('_') + 1:]

        if '_open' in generic_id:
            related_to = 'open'
        elif '_high' in generic_id:
            related_to = 'high'
        elif '_low' in generic_id:
            related_to = 'low'
        elif '_close' in generic_id:
            related_to = 'close'

        obj = phioon_utils.retrieve_obj_from_obj_list(result, 'id', generic_id)
        if not obj:
            # Create it
            obj = {
                'id': generic_id,
                'instances': [],
                'category': category,
                'subcategory': subcategory,
                'indicator': indicator,
                'related_to': related_to,
                'periods': periods
            }

        obj['instances'].append({
            'name': field_name,
            'interval': time_interval
        })
        result.append(obj)

    # 2.4 Price Lagging: PHIBO
    category = 'price_lagging'
    subcategory = 'phibo'
    indicator = 'phibo'
    related_to = None
    for field_name in d_pvpc_fields:
        periods = int(re.findall('[0-9]+', field_name)[0])
        generic_id = str(field_name)[str(field_name).index('_') + 1:]

        obj = phioon_utils.retrieve_obj_from_obj_list(result, 'id', generic_id)
        if not obj:
            # Create it
            obj = {
                'id': generic_id,
                'instances': [],
                'category': category,
                'subcategory': subcategory,
                'indicator': indicator,
                'related_to': related_to,
                'periods': periods
            }

        obj['instances'].append({
            'name': field_name,
            'interval': time_interval
        })
        result.append(obj)

    # 2.5 Centered Oscillator: ROC
    category = 'centered_oscillator'
    subcategory = 'roc'
    indicator = 'roc'
    related_to = None
    for field_name in d_roc_fields:
        periods = int(re.findall('[0-9]+', field_name)[0])
        generic_id = str(field_name)[str(field_name).index('_') + 1:]

        if '_ema' in generic_id:
            related_to = 'ema'
        elif '_sma' in generic_id:
            related_to = 'sma'

        obj = phioon_utils.retrieve_obj_from_obj_list(result, 'id', generic_id)
        if not obj:
            # Create it
            obj = {
                'id': generic_id,
                'instances': [],
                'category': category,
                'subcategory': subcategory,
                'indicator': indicator,
                'related_to': related_to,
                'periods': periods
            }

        obj['instances'].append({
            'name': field_name,
            'interval': time_interval
        })
        result.append(obj)

    return Response(result)
