from django.db.models import Q, Max
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics, permissions
from rest_framework import status
from rest_framework.response import Response

from django_engine.functions import generic
from django_engine import settings
from .functions import utils as phioon_utils
from . import serializers
from .models import StockExchange, Asset, TechnicalCondition
from .models import Realtime, D_raw, D_pvpc, D_ema, D_roc, D_setup, D_setupSummary
from .cron import m15, daily, monthly, onDemand

from django.utils import timezone
from datetime import datetime, timedelta
from time import time
import pytz

import re
import copy

from google.cloud import tasks_v2
from concurrent.futures import ThreadPoolExecutor as ThreadPool


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
class AssetList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        detailed = self.request.query_params.get('detailed')
        if str(detailed).lower() == 'true':
            return serializers.AssetDetailSerializer
        else:
            return serializers.AssetBasicSerializer

    def get_queryset(self):
        stockExchange = self.request.query_params.get('stockExchange')
        assets = self.request.query_params.get('assets')

        if stockExchange:
            return Asset.objects.filter(stockExchange__se_short__exact=stockExchange)
        else:
            assets = assets.split(',')

            # Log into DB last_access_time. It is used for tracking usage of assets
            a = Asset()
            a.frontend_access(assets)

            return Asset.objects.filter(asset_symbol__in=assets)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def IndicatorList(request):
    result = []
    consider_fields = {
        'd_raw': ['d_open', 'd_high', 'd_low', 'd_close']
    }
    ignore_fields = {
        'raw': ['id', 'asset_symbol', 'asset_datetime', 'last_trade_time', 'pct_change'],
        'ema': ['id', 'd_raw', 'asset_datetime'],
        'phibo': ['id', 'd_raw', 'asset_datetime'],
        'roc': ['id', 'd_raw', 'asset_datetime', 'd_roc_close2', 'd_roc_close3', 'd_roc_high2', 'd_roc_low2'],
    }
    # Requirements
    d_raw_fields = D_raw._meta.fields
    d_ema_fields = D_ema._meta.fields
    d_pvpc_fields = D_pvpc._meta.fields
    d_roc_fields = D_roc._meta.fields
    generic_time_interval = 'any'

    # 1. Any Interval
    # 1.1 Zero
    category = 'centered_oscillator'
    subcategory = 'zero_line'
    indicator = 'zero_line'
    periods = None
    time_interval = 'any'

    obj = {
        'id': 'zero_line',
        'label_id': 'zero_line',
        'category': category,
        'subcategory': subcategory,
        'indicator': indicator,
        'periods': periods,
        'time_interval': time_interval,
        'relationships': []
    }
    result.append(obj)
    # 2. Daily
    time_interval = 'd'
    # 2.1 Price Lagging: Quote
    for field in d_raw_fields:
        category = 'price_lagging'
        subcategory = 'quote'
        indicator = 'quote'

        if field.name in consider_fields['d_raw']:
            generic_obj = None
            periods = 0
            generic_id = str(field.name)[str(field.name).index('_') + 1:]

            obj = {
                'id': field.name,
                'label_id': generic_id,
                'category': category,
                'subcategory': subcategory,
                'indicator': indicator,
                'periods': periods,
                'time_interval': time_interval,
                'relationships': []
            }

            if not phioon_utils.retrieve_obj_from_obj_list(result, 'id', generic_id):
                generic_obj = copy.deepcopy(obj)
                generic_obj['id'] = generic_id
                generic_obj['time_interval'] = generic_time_interval

            if generic_obj:
                result.append(generic_obj)
            result.append(obj)
    # 2.2 Price Lagging: EMA
    for field in d_ema_fields:
        category = 'price_lagging'
        subcategory = 'moving_average'
        indicator = 'ema'

        if field.name not in ignore_fields['ema']:
            generic_obj = None
            periods = int(re.findall('[0-9]+', field.name)[0])
            generic_id = str(field.name)[str(field.name).index('_') + 1:]

            obj = {
                'id': field.name,
                'label_id': generic_id,
                'category': category,
                'subcategory': subcategory,
                'indicator': indicator,
                'periods': periods,
                'time_interval': time_interval,
                'relationships': []
            }

            generic_roc_id = generic_id.replace('ema_', 'ema')
            generic_roc_id = 'roc_' + generic_roc_id
            roc_id = time_interval + '_' + generic_roc_id

            if not phioon_utils.retrieve_obj_from_obj_list(result, 'id', generic_id):
                generic_obj = copy.deepcopy(obj)
                generic_obj['id'] = generic_id
                generic_obj['time_interval'] = generic_time_interval

            for field in d_roc_fields:
                if roc_id == field.name:
                    obj['relationships'].append({'id': roc_id})

                    if generic_obj:
                        generic_obj['relationships'].append({'id': generic_roc_id})
                    break

            if generic_obj:
                result.append(generic_obj)
            result.append(obj)
    # 2.3 Price Lagging: PHIBO
    for field in d_pvpc_fields:
        category = 'price_lagging'
        subcategory = 'phibo'
        indicator = 'pvpc'

        if field.name not in ignore_fields['phibo']:
            periods = int(re.findall('[0-9]+', field.name)[0])
            generic_id = str(field.name)[str(field.name).index('_') + 1:]

            generic_obj = None
            obj = {
                'id': field.name,
                'label_id': generic_id,
                'category': category,
                'subcategory': subcategory,
                'indicator': indicator,
                'periods': periods,
                'time_interval': time_interval,
                'relationships': []
            }

            if not phioon_utils.retrieve_obj_from_obj_list(result, 'id', generic_id):
                generic_obj = copy.deepcopy(obj)
                generic_obj['id'] = generic_id
                generic_obj['time_interval'] = generic_time_interval

            if generic_obj:
                result.append(generic_obj)
            result.append(obj)
    # 2.4 Centered Oscillator: ROC
    for field in d_roc_fields:
        category = 'centered_oscillator'
        subcategory = 'roc'
        indicator = 'roc'

        if field.name not in ignore_fields['roc']:
            periods = int(re.findall('[0-9]+', field.name)[0])
            generic_id = str(field.name)[str(field.name).index('_') + 1:]

            generic_obj = None
            obj = {
                'id': field.name,
                'label_id': generic_id,
                'category': category,
                'subcategory': subcategory,
                'indicator': indicator,
                'periods': periods,
                'time_interval': time_interval,
                'relationships': []
            }

            if not phioon_utils.retrieve_obj_from_obj_list(result, 'id', generic_id):
                generic_obj = copy.deepcopy(obj)
                generic_obj['id'] = generic_id
                generic_obj['time_interval'] = generic_time_interval

            if generic_obj:
                result.append(generic_obj)
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


class D_RawLatestList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.D_rawBasicSerializer

    def get_queryset(self):
        stockExchange = self.request.query_params.get('stockExchange')
        assets = self.request.query_params.get('assets')
        result = []

        if stockExchange:
            latest_datetime_by_asset = (D_raw.objects.filter(asset_symbol__stockExchange__exact=stockExchange)
                                        .values('asset_symbol')
                                        .annotate(latest_datetime=Max('d_datetime')))
        else:
            assets = assets.split(',')
            latest_datetime_by_asset = (D_raw.objects.filter(asset_symbol__in=assets)
                                        .values('asset_symbol')
                                        .annotate(latest_datetime=Max('d_datetime')))

        for obj in latest_datetime_by_asset:
            try:
                latest_data = D_raw.objects.get(asset_symbol=obj['asset_symbol'],
                                                d_datetime__exact=obj['latest_datetime'])
            except D_raw.DoesNotExist:
                continue

            result.append(latest_data)

        return result


class D_EmaLatestList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.D_emaSerializer

    def get_queryset(self):
        stockExchange = self.request.query_params.get('stockExchange')
        assets = self.request.query_params.get('assets')
        result = []

        if stockExchange:
            latest_datetime_by_asset = (D_raw.objects.filter(asset_symbol__stockExchange__exact=stockExchange)
                                        .values('asset_symbol')
                                        .annotate(latest_datetime=Max('d_datetime')))
        else:
            assets = assets.split(',')
            latest_datetime_by_asset = (D_raw.objects.filter(asset_symbol__in=assets)
                                        .values('asset_symbol')
                                        .annotate(latest_datetime=Max('d_datetime')))

        for obj in latest_datetime_by_asset:
            try:
                latest_data = D_ema.objects.get(d_raw__asset_symbol=obj['asset_symbol'],
                                                d_raw__d_datetime__exact=obj['latest_datetime'])
            except D_ema.DoesNotExist:
                continue

            result.append(latest_data)

        return result


class D_PhiboLatestList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.D_pvpcSerializer

    def get_queryset(self):
        stockExchange = self.request.query_params.get('stockExchange')
        assets = self.request.query_params.get('assets')
        result = []

        if stockExchange:
            latest_datetime_by_asset = (D_raw.objects.filter(asset_symbol__stockExchange__exact=stockExchange)
                                        .values('asset_symbol')
                                        .annotate(latest_datetime=Max('d_datetime')))
        else:
            assets = assets.split(',')
            latest_datetime_by_asset = (D_raw.objects.filter(asset_symbol__in=assets)
                                        .values('asset_symbol')
                                        .annotate(latest_datetime=Max('d_datetime')))

        for obj in latest_datetime_by_asset:
            try:
                latest_data = D_pvpc.objects.get(d_raw__asset_symbol=obj['asset_symbol'],
                                                 d_raw__d_datetime__exact=obj['latest_datetime'])
            except D_pvpc.DoesNotExist:
                continue

            result.append(latest_data)

        return result


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
        client = tasks_v2.CloudTasksClient()
        parent = client.queue_path(settings.GAE_PROJECT,
                                   settings.GAE_QUEUES['market-eod']['location'],
                                   settings.GAE_QUEUES['market-eod']['name'])
        sync_list = []
        assets = Asset.objects.filter(stockExchange=se_short)

        for asset in assets:
            if asset.draws.count() > 0:
                sync_list.append(asset)

        for asset in sync_list:
            url = settings.MARKET_API_BASE + 'task/offline/runRaw/D/asset/'
            url += asset.asset_symbol + '/'
            url += settings.API_KEY
            task = {
                'http_request': {
                    'http_method': 'GET',
                    'url': url}}
            client.create_task(parent, task)

        obj_res = {
            'context': 'apiMarket.run_raw_data_se_short',
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
        client = tasks_v2.CloudTasksClient()
        parent = client.queue_path(settings.GAE_PROJECT,
                                   settings.GAE_QUEUES['market-eod']['location'],
                                   settings.GAE_QUEUES['market-eod']['name'])

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

        if settings.ENVIRONMENT == 'PRD':
            for asset in sync_list:
                url = settings.MARKET_API_BASE + 'task/runRaw/D/asset/'
                url += asset.asset_symbol + '/'
                url += str(last_periods) + '/'
                url += settings.API_KEY
                task = {
                    'http_request': {
                        'http_method': 'GET',
                        'url': url}}
                client.create_task(parent, task)
        elif settings.ENVIRONMENT == 'DEV' and settings.ACCESS_PRD_DB is False:
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

        assets_with_open_suggestion = D_setupSummary.objects \
            .filter(has_position_open=True) \
            .values_list('asset_symbol', flat=True).distinct()

        assets = Asset.objects.filter(
            Q(last_access_time__gte=a_month_ago) | Q(asset_symbol__in=assets_with_open_suggestion))

        client = tasks_v2.CloudTasksClient()
        parent = client.queue_path(settings.GAE_PROJECT,
                                   settings.GAE_QUEUES['market-realtime']['location'],
                                   settings.GAE_QUEUES['market-realtime']['name'])

        with ThreadPool() as t:
            for asset in assets:
                url = settings.MARKET_API_BASE + 'task/updateRealtime/asset/'
                url += asset.asset_symbol + '/'
                url += settings.API_KEY
                task = {
                    'http_request': {
                        'http_method': 'GET',
                        'url': url}}
                t.submit(client.create_task, parent, task)

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
