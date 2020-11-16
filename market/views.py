from django.db.models import Q, Max
from django.http import HttpResponse
from django.core import serializers as django_serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework import generics, permissions
from rest_framework import status
from rest_framework.response import Response

from django_engine.functions import generic
from django_engine import settings
from .functions import utils as phioon_utils
from . import serializers
from .models import StockExchange, Asset, TechnicalCondition
from .models import D_raw, D_pvpc, D_sma, D_ema, D_roc, D_setup, D_setupSummary
from .cron import m15, daily, monthly, onDemand

from django.utils import timezone
from datetime import datetime, timedelta
from time import time
import pytz
import json

import re

from google.cloud import tasks_v2


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
    queryset = TechnicalCondition.objects.all()


# Class created to add support to a Stock Exchange in a friendly way (by a human).
# Used only if it's necessary.
class StockExchangeList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.StockExchangeSerializer

    def get_queryset(self):
        return StockExchange.objects.filter(pk__in=settings.MARKET_SE_LIST)


# Integration between Backend and Frontend
class AssetList(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        stockExchange = assets = None

        if 'assets' in request.data:
            assets = request.data['assets']
        if 'stockExchange' in request.data:
            stockExchange = request.data['stockExchange']

        if assets:
            assets = assets.split(',')

            # Log into DB last_access_time. It is used for tracking usage of assets
            a = Asset()
            a.frontend_access(assets)

            assets = Asset.objects.filter(asset_symbol__in=assets)
        else:
            assets = Asset.objects.filter(stockExchange__se_short__exact=stockExchange)

        serializer = serializers.AssetDetailSerializer(assets, many=True)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def IndicatorList(request):
    result = []

    # Requirements
    d_raw_fields = D_raw().get_field_list(field_type='indicator')
    d_sma_fields = D_sma().get_field_list(field_type='indicator')
    d_ema_fields = D_ema().get_field_list(field_type='indicator')
    d_pvpc_fields = D_pvpc().get_field_list(field_type='indicator')
    d_roc_fields = D_roc().get_field_list(field_type='indicator')

    # 2. Daily
    time_interval = 'd'
    # 2.1 Price Lagging: Quote
    category = 'price_lagging'
    subcategory = 'quote'
    indicator = 'quote'
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
    for field_name in d_sma_fields:
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
    for field_name in d_ema_fields:
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
    indicator = 'pvpc'
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
    for field_name in d_roc_fields:
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
                'periods': periods
            }

        obj['instances'].append({
            'name': field_name,
            'interval': time_interval
        })
        result.append(obj)

    return Response(result)


class D_RawList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        detailed = self.request.query_params.get('detailed')
        if str(detailed).lower() == 'true':
            return serializers.D_rawDetailSerializer
        else:
            return serializers.D_rawBasicSerializer

    def get_queryset(self):
        asset = self.request.query_params.get('asset')
        dateFrom = self.request.query_params.get('dateFrom')
        dateTo = self.request.query_params.get('dateTo')

        if dateFrom is None:
            dateFrom = '2001-01-01'
        if dateTo is None:
            dateTo = str(datetime.today().date())

        return D_raw.objects.filter(asset_symbol=asset,
                                    d_datetime__gte=dateFrom,
                                    d_datetime__lte=dateTo + ' 23:59:59')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def D_SmaLatestList(request):
    stockExchange = request.query_params.get('stockExchange')
    assets = request.query_params.get('assets')
    lastPeriods = int(request.query_params.get('lastPeriods'))
    instances = request.query_params.get('instances')
    instances = instances.split(',')
    result = {
        'latest_datetime': None,
        'data': []
    }

    if lastPeriods is None or lastPeriods <= 0 or lastPeriods >= 5:
        lastPeriods = 1

    dates = D_raw.objects.values('d_datetime').distinct().order_by('-d_datetime')
    dateFrom = dates[lastPeriods - 1]['d_datetime']
    result['latest_datetime'] = dates[0]['d_datetime']

    # Define which assets are selected
    if stockExchange:
        assets = Asset.objects.filter(stockExchange=stockExchange, is_considered_for_analysis=True)
    else:
        assets = assets.split(',')
        assets = Asset.objects.filter(pk__in=assets, is_considered_for_analysis=True)

    # Append data into result
    for asset in assets:
        objs = list(D_sma.objects.filter(d_raw__asset_symbol=asset, d_raw__d_datetime__gte=dateFrom)
                    .order_by('-asset_datetime'))

        if len(objs) != lastPeriods:
            # There is no enough data in database
            continue

        if objs:
            asset_data = {'asset_symbol': asset.asset_symbol}

            for x in range(len(objs)):
                # For each time interval...
                for i in instances:
                    if hasattr(objs[x], i):
                        # Instance exists
                        i_value = getattr(objs[x], i)
                        if i_value:
                            # Instance value is not null nor 0
                            key = str(i) + '__p' + str(x)
                            asset_data[key] = i_value

            result['data'].append(asset_data)

    return Response(result)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def D_EmaLatestList(request):
    stockExchange = request.query_params.get('stockExchange')
    assets = request.query_params.get('assets')
    lastPeriods = int(request.query_params.get('lastPeriods'))
    instances = request.query_params.get('instances')
    instances = instances.split(',')
    result = {
        'latest_datetime': None,
        'data': []
    }

    if lastPeriods is None or lastPeriods <= 0 or lastPeriods >= 5:
        lastPeriods = 1

    dates = D_raw.objects.values('d_datetime').distinct().order_by('-d_datetime')
    dateFrom = dates[lastPeriods - 1]['d_datetime']
    result['latest_datetime'] = dates[0]['d_datetime']

    # Define which assets are selected
    if stockExchange:
        assets = Asset.objects.filter(stockExchange=stockExchange, is_considered_for_analysis=True)
    else:
        assets = assets.split(',')
        assets = Asset.objects.filter(pk__in=assets, is_considered_for_analysis=True)

    # Append data into result
    for asset in assets:
        objs = list(D_ema.objects.filter(d_raw__asset_symbol=asset, d_raw__d_datetime__gte=dateFrom)
                    .order_by('-asset_datetime'))

        if len(objs) != lastPeriods:
            # There is no enough data in database
            continue

        if objs:
            asset_data = {'asset_symbol': asset.asset_symbol}

            for x in range(len(objs)):
                # For each time interval...
                for i in instances:
                    if hasattr(objs[x], i):
                        # Instance exists
                        i_value = getattr(objs[x], i)
                        if i_value:
                            # Instance value is not null nor 0
                            key = str(i) + '__p' + str(x)
                            asset_data[key] = i_value

            result['data'].append(asset_data)

    return Response(result)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def D_QuoteLatestList(request):
    stockExchange = request.query_params.get('stockExchange')
    assets = request.query_params.get('assets')
    lastPeriods = int(request.query_params.get('lastPeriods'))
    instances = request.query_params.get('instances')
    instances = instances.split(',')
    result = {
        'latest_datetime': None,
        'data': []
    }

    if lastPeriods is None or lastPeriods <= 0 or lastPeriods >= 5:
        lastPeriods = 1

    dates = D_raw.objects.values('d_datetime').distinct().order_by('-d_datetime')
    dateFrom = dates[lastPeriods - 1]['d_datetime']
    result['latest_datetime'] = dates[0]['d_datetime']

    # Define which assets are selected
    if stockExchange:
        assets = Asset.objects.filter(stockExchange=stockExchange, is_considered_for_analysis=True)
    else:
        assets = assets.split(',')
        assets = Asset.objects.filter(pk__in=assets, is_considered_for_analysis=True)

    # Append data into result
    for asset in assets:
        raw_objs = list(D_raw.objects.filter(asset_symbol=asset, d_datetime__gte=dateFrom)
                        .order_by('-asset_datetime'))
        raw_objs = json.loads(django_serializers.serialize('json', raw_objs))

        if len(raw_objs) != lastPeriods:
            # There is no enough data in database
            continue

        if raw_objs:
            # 'raw_objs' is valid and the amount of raw objects is the same as 'lastPeriods'
            if hasattr(asset, 'realtime'):
                # Asset has Realtime instance
                last_trade_time = asset.realtime.last_trade_time

                if last_trade_time > raw_objs[0]['fields']['d_datetime']:
                    # Realtime data is newer than raw data...
                    # Inserts new item into position 0
                    raw_objs.insert(0, {
                        'fields': {
                            'd_open': asset.realtime.open,
                            'd_high': asset.realtime.high,
                            'd_low': asset.realtime.low,
                            'd_close': asset.realtime.price,
                        }
                    })
                    # Removes last item
                    raw_objs.pop()

            asset_data = {'asset_symbol': asset.asset_symbol}

            for x in range(len(raw_objs)):
                obj = raw_objs[x]
                # For each time interval...
                for i in instances:
                    # Add instance data into this asset's object, accordingly to its period
                    key = str(i) + '__p' + str(x)
                    if i in obj['fields']:
                        asset_data[key] = obj['fields'][i]

            result['data'].append(asset_data)

    return Response(result)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def D_PhiboLatestList(request):
    stockExchange = request.query_params.get('stockExchange')
    assets = request.query_params.get('assets')
    lastPeriods = int(request.query_params.get('lastPeriods'))
    instances = request.query_params.get('instances')
    instances = instances.split(',')
    result = {
        'latest_datetime': None,
        'data': []
    }

    if lastPeriods is None or lastPeriods <= 0 or lastPeriods >= 5:
        lastPeriods = 1

    dates = D_raw.objects.values('d_datetime').distinct().order_by('-d_datetime')
    dateFrom = dates[lastPeriods - 1]['d_datetime']
    result['latest_datetime'] = dates[0]['d_datetime']

    # Define which assets are selected
    if stockExchange:
        assets = Asset.objects.filter(stockExchange=stockExchange, is_considered_for_analysis=True)
    else:
        assets = assets.split(',')
        assets = Asset.objects.filter(pk__in=assets, is_considered_for_analysis=True)

    # Append data into result
    for asset in assets:
        objs = list(D_pvpc.objects.filter(d_raw__asset_symbol=asset, d_raw__d_datetime__gte=dateFrom)
                    .order_by('-asset_datetime'))

        if len(objs) != lastPeriods:
            # There is no enough data in database
            continue

        if objs:
            asset_data = {'asset_symbol': asset.asset_symbol}

            for x in range(len(objs)):
                # For each time interval...
                for i in instances:
                    if hasattr(objs[x], i):
                        # Instance exists
                        i_value = getattr(objs[x], i)
                        print('%s || %s || %s' % (asset.asset_symbol, i, i_value))
                        if i_value:
                            # Instance value is not null nor 0
                            key = str(i) + '__p' + str(x)
                            asset_data[key] = i_value

            result['data'].append(asset_data)

    return Response(result)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def D_RocLatestList(request):
    stockExchange = request.query_params.get('stockExchange')
    assets = request.query_params.get('assets')
    lastPeriods = int(request.query_params.get('lastPeriods'))
    instances = request.query_params.get('instances')
    instances = instances.split(',')
    result = {
        'latest_datetime': None,
        'data': []
    }

    if lastPeriods is None or lastPeriods <= 0 or lastPeriods >= 5:
        lastPeriods = 1

    dates = D_raw.objects.values('d_datetime').distinct().order_by('-d_datetime')
    dateFrom = dates[lastPeriods - 1]['d_datetime']
    result['latest_datetime'] = dates[0]['d_datetime']

    # Define which assets are selected
    if stockExchange:
        assets = Asset.objects.filter(stockExchange=stockExchange, is_considered_for_analysis=True)
    else:
        assets = assets.split(',')
        assets = Asset.objects.filter(pk__in=assets, is_considered_for_analysis=True)

    # Append data into result
    for asset in assets:
        objs = list(D_roc.objects.filter(d_raw__asset_symbol=asset, d_raw__d_datetime__gte=dateFrom)
                    .order_by('-asset_datetime'))

        if len(objs) != lastPeriods:
            # There is no enough data in database
            continue

        if objs:
            asset_data = {'asset_symbol': asset.asset_symbol}

            for x in range(len(objs)):
                # For each time interval...
                for i in instances:
                    if hasattr(objs[x], i):
                        # Instance exists
                        i_value = getattr(objs[x], i)
                        if i_value:
                            # Instance value is not null or 0
                            key = str(i) + '__p' + str(x)
                            asset_data[key] = i_value

            result['data'].append(asset_data)

    return Response(result)


class D_SetupList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.D_setupSerializer

    def get_queryset(self):
        stockExchange = self.request.query_params.get('stockExchange')
        dateFrom = self.request.query_params.get('dateFrom')

        if dateFrom is None:
            dateFrom = str(datetime.today().date() - timedelta(days=90))

        setups = D_setup.objects.filter(
            Q(d_raw__asset_symbol__stockExchange__exact=stockExchange, is_public=True),
            Q(ended_on__isnull=True) | Q(started_on__gte=dateFrom))

        return setups


class D_SetupSummaryList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.D_setupSummarySerializer

    def get_queryset(self):
        stockExchange = self.request.query_params.get('stockExchange')
        dateFrom = self.request.query_params.get('dateFrom')

        if dateFrom is None:
            dateFrom = str(datetime.today().date() - timedelta(days=90))

        setups = list(D_setup.objects
                      .filter(Q(d_raw__asset_symbol__stockExchange__exact=stockExchange, is_public=True) |
                              Q(ended_on__isnull=True) | Q(started_on__gte=dateFrom))
                      .values_list('asset_setup', flat=True)
                      .distinct())

        setup_summary = D_setupSummary.objects.filter(asset_setup__in=setups)

        return setup_summary


# On-demand
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def update_stock_exchange_list(request, apiKey=None):
    if apiKey == settings.API_KEY:
        st = time()
        onDemand.update_stock_exchange_list()
        duration = str(round(time() - st, 2))
        obj_res = {'message': "Task '%s' took %s seconds to complete."
                              % ('update_stock_exchange_list', duration)}
        return Response(obj_res)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def run_offline_raw_data_se_short(request, se_short, apiKey=None):
    if apiKey == settings.API_KEY:
        sync_list = []
        stockExchange = StockExchange.objects.get(pk=se_short)
        assets = Asset.objects.filter(stockExchange=stockExchange)

        for asset in assets:
            if asset.draws.count() > 0:
                sync_list.append(asset)

        if settings.ACCESS_PRD_DB:
            client = tasks_v2.CloudTasksClient()
            parent = client.queue_path(settings.GAE_PROJECT,
                                       settings.GAE_QUEUES['market-eod']['location'],
                                       settings.GAE_QUEUES['market-eod']['name'])

            for asset in sync_list:
                url = settings.MARKET_API_BASE + 'task/offline/runRaw/D/asset/'
                url += asset.asset_symbol + '/'
                url += settings.API_KEY
                task = {
                    'http_request': {
                        'http_method': 'GET',
                        'url': url}}
                client.create_task(parent=parent, task=task)
        else:
            for asset in sync_list:
                print('Working on %s...' % asset.asset_symbol)
                onDemand.run_offline_raw_data_asset(symbol=asset.asset_symbol)

        obj_res = {
            'context': 'apiMarket.run_offline_raw_data_se_short',
            'message': "[%s] Assets to be updated: %s" % (se_short, sync_list)}
        return Response(obj_res)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def run_offline_raw_data_asset(request, symbol, apiKey=None):
    if apiKey == settings.API_KEY:
        onDemand.run_offline_raw_data_asset(symbol=symbol)

        obj_res = {'message': "success"}
        return Response(obj_res)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def run_offline_setup_se_short(request, se_short, apiKey=None):
    if apiKey == settings.API_KEY:
        sync_list = []
        stockExchange = StockExchange.objects.get(pk=se_short)
        assets = Asset.objects.filter(stockExchange=stockExchange)

        for asset in assets:
            if asset.draws.count() > 0:
                sync_list.append(asset)

        if settings.ACCESS_PRD_DB:
            client = tasks_v2.CloudTasksClient()
            parent = client.queue_path(settings.GAE_PROJECT,
                                       settings.GAE_QUEUES['market-eod']['location'],
                                       settings.GAE_QUEUES['market-eod']['name'])

            for asset in sync_list:
                url = settings.MARKET_API_BASE + 'task/offline/runSetup/D/asset/'
                url += asset.asset_symbol + '/'
                url += settings.API_KEY
                task = {
                    'http_request': {
                        'http_method': 'GET',
                        'url': url}}
                client.create_task(parent=parent, task=task)
        else:
            for asset in sync_list:
                print('Working on %s...' % asset.asset_symbol)
                onDemand.run_offline_setup_asset(symbol=asset.asset_symbol)

        obj_res = {
            'context': 'apiMarket.run_offline_setup_se_short',
            'message': "[%s] Assets to be updated: %s" % (se_short, sync_list)}
        return Response(obj_res)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def run_offline_setup_asset(request, symbol, apiKey=None):
    if apiKey == settings.API_KEY:
        onDemand.run_offline_setup_asset(symbol=symbol)

        obj_res = {'message': "success"}
        return Response(obj_res)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


# Cron Job (1st of month at 22:00)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def update_asset_list(request, se_short, apiKey=None):
    if apiKey == settings.API_KEY:
        st = time()
        monthly.update_asset_list(se_short=se_short)
        duration = str(round(time() - st, 2))
        obj_res = {'message': "Task '%s' for '%s' took %s seconds to complete."
                              % ('update_asset_list', se_short, duration)}
        return Response(obj_res)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


# Cron Job (1st of month at 22:00)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def update_asset_profile(request, symbol, apiKey=None):
    if apiKey == settings.API_KEY:
        st = time()
        monthly.update_asset_profile(symbol=symbol)
        duration = str(round(time() - st, 2))
        obj_res = {'message': "Task '%s' for '%s' took %s seconds to complete."
                              % ('update_asset_profile', symbol, duration)}
        return Response(obj_res)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


# Cron Job (Daily on weekdays)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def run_raw_data_se_short(request, se_short, last_x_rows=5, apiKey=None):
    if apiKey == settings.API_KEY:
        stockExchange = StockExchange.objects.get(pk=se_short)

        se_tzinfo = pytz.timezone(stockExchange.se_timezone)
        today = datetime.today().astimezone(se_tzinfo)
        a_month_ago = today - timedelta(days=30)

        # Once we got a bigger plan with Providers, switch it to all assets (line bellow)
        # assets = Asset.objects.filter(stockExchange=se_short)
        sync_list = []
        assets = Asset.objects.filter(
            Q(last_access_time__gte=a_month_ago) | Q(is_considered_for_analysis=True),
            stockExchange=se_short
        )

        if today.weekday() in [0]:
            # MON
            if today.hour <= 12:
                # Latest EOD data on DB must be Friday's.
                delta_days_tolerance = 4
            else:
                # Latest EOD data on DB must be today's.
                delta_days_tolerance = 1
        elif today.weekday() in [1, 2, 3, 4]:
            # TUS, WED, THU, SEX
            if today.hour <= 12:
                # Latest EOD data on DB must be yesterday's.
                delta_days_tolerance = 2
            else:
                # Latest EOD data on DB must be today's.
                delta_days_tolerance = 1
        elif today.weekday() in [5]:
            # SAT: Latest EOD data on DB must be Friday's.
            delta_days_tolerance = 2
        elif today.weekday() in [6]:
            # SUN: Latest EOD data on DB must be Friday's.
            delta_days_tolerance = 3

        for asset in assets:
            draws = asset.draws
            last_periods = last_x_rows

            if draws.count() > 0:
                latest_draw = asset.draws.order_by('-d_datetime')[0]
                latest_datetime = datetime.strptime(latest_draw.d_datetime, '%Y-%m-%d %H:%M:%S')
                latest_datetime = timezone.make_aware(latest_datetime,
                                                      se_tzinfo)
                delta = today - latest_datetime

                if delta > timedelta(days=delta_days_tolerance):
                    # Sync only assets that really need to be synchronized
                    sync_list.append(asset)
            else:
                sync_list.append(asset)
                last_periods = 0

        if settings.ACCESS_PRD_DB:
            client = tasks_v2.CloudTasksClient()
            parent = client.queue_path(settings.GAE_PROJECT,
                                       settings.GAE_QUEUES['market-eod']['location'],
                                       settings.GAE_QUEUES['market-eod']['name'])
            for asset in sync_list:
                url = settings.MARKET_API_BASE + 'task/runRaw/D/asset/'
                url += asset.asset_symbol + '/'
                url += str(last_periods) + '/'
                url += settings.API_KEY
                task = {
                    'http_request': {
                        'http_method': 'GET',
                        'url': url}}
                client.create_task(parent=parent, task=task)
        else:
            for asset in sync_list:
                print('Working on %s...' % asset.asset_symbol)
                daily.run_asset_raw(symbol=asset.asset_symbol, lastXrows=last_x_rows)

        obj_res = {
            'context': 'apiMarket.run_raw_data_se_short',
            'message': "[%s] Assets to be updated: %s" % (se_short, sync_list)}
        return Response(obj_res)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


# Cron Job (every 15min on weekdays)
# Can be called out of business-hours to check non-considered Assets
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def update_realtime_se_short(request, se_short, apiKey=None):
    if apiKey == settings.API_KEY:
        st = time()
        today = datetime.today().date()
        a_month_ago = today - timedelta(days=30)

        if today.weekday() in [5, 6]:
            obj_res = {'message': "Today is not a weekday."}
            return Response(obj_res)

        assets = Asset.objects.filter(
            Q(last_access_time__gte=a_month_ago) | Q(is_considered_for_analysis=True),
            stockExchange=se_short
        )

        if settings.ACCESS_PRD_DB:
            client = tasks_v2.CloudTasksClient()
            parent = client.queue_path(settings.GAE_PROJECT,
                                       settings.GAE_QUEUES['market-realtime']['location'],
                                       settings.GAE_QUEUES['market-realtime']['name'])

            for asset in assets:
                url = settings.MARKET_API_BASE + 'task/updateRealtime/asset/'
                url += asset.asset_symbol + '/'
                url += settings.API_KEY
                task = {
                    'http_request': {
                        'http_method': 'GET',
                        'url': url}}
                client.create_task(parent=parent, task=task)
        else:
            for asset in assets:
                print('Working on %s...' % asset.asset_symbol)
                m15.update_realtime_asset(asset.asset_symbol)

        duration = str(round(time() - st, 2))
        obj_res = {'message': "Task '%s' for '%s' took %s seconds to complete."
                              % ('update_realtime_se_short', se_short, duration)}
        return Response(obj_res)
    else:
        return HttpResponse(status=status.HTTP_403_FORBIDDEN)


# Task used by GCloud queues
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def run_raw_data_asset(request, symbol, last_x_rows=5, apiKey=None):
    if apiKey == settings.API_KEY:
        daily.run_asset_raw(symbol=symbol, lastXrows=last_x_rows)

        obj_res = {'message': "success"}
        return Response(obj_res)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def update_realtime_asset(request, symbol, apiKey=None):
    if apiKey == settings.API_KEY:
        m15.update_realtime_asset(symbol)

        obj_res = {'message': "success."}
        return Response(obj_res)
    else:
        return HttpResponse(status=status.HTTP_403_FORBIDDEN)
