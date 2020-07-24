from django.db.models import Q
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics, permissions
from rest_framework import status
from rest_framework.response import Response

from django_engine.functions import generic
from django_engine import settings
from api_engine import serializers
from market.models import StockExchange, Asset, D_raw, TechnicalCondition, D_setup, D_setupSummary
from market.cron import m15, daily, monthly

from datetime import datetime, timedelta
from time import time

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


# Integration between Backend and Frontend
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


# Integration between Backend and Frontend.
# 'min_success_rate' determines which Setups users will receive as Recommendation.
min_success_rate = 60


class D_SetupList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.D_setupSerializer

    def get_queryset(self):
        stockExchange = self.request.query_params.get('stockExchange')
        dateFrom = self.request.query_params.get('dateFrom')

        if dateFrom is None:
            dateFrom = str(datetime.today().date() - timedelta(days=90))

        asset_setup_list = list(D_setupSummary.objects.filter(asset_symbol__stockExchange__exact=stockExchange,
                                                              success_rate__gte=min_success_rate)
                                .values_list('asset_setup', flat=True))

        setups = D_setup.objects.filter(
            Q(asset_setup__in=asset_setup_list),
            Q(ended_on__isnull=True) | Q(started_on__gte=dateFrom))

        return setups


class D_SetupSummaryList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.D_setupSummarySerializer

    def get_queryset(self):
        stockExchange = self.request.query_params.get('stockExchange')

        setup_summary = D_setupSummary.objects.filter(asset_symbol__stockExchange__exact=stockExchange,
                                                      success_rate__gte=min_success_rate)

        return setup_summary


# On-demand
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def update_stock_exchange_list(request, apiKey=None):
    if apiKey == settings.API_KEY:
        st = time()
        monthly.update_stock_exchange_list()
        duration = str(round(time() - st, 2))
        obj_res = {'message': "Task '%s' took %s seconds to complete."
                              % ('update_stock_exchange_list', duration)}
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
        st = time()
        # Here, 'is_considered_for_analysis' is temporary, in order to save licenses...
        # If kept that way, an Asset will never become considered.
        assets = list(Asset.objects.filter(is_considered_for_analysis=True, stockExchange=se_short)
                      .values_list('asset_symbol', flat=True))
        if len(assets) == 0:
            return

        client = tasks_v2.CloudTasksClient()
        parent = client.queue_path(settings.GAE_PROJECT,
                                   settings.GAE_QUEUES['market-eod']['location'],
                                   settings.GAE_QUEUES['market-eod']['name'])

        with ThreadPool() as t:
            for x in range(len(assets)):
                url = settings.MARKET_API_BASE + 'task/runRaw/D/asset/'
                url += assets[x] + '/'
                url += str(last_x_rows) + '/'
                url += settings.API_KEY
                task = {
                    'http_request': {
                        'http_method': 'GET',
                        'url': url}}
                t.submit(client.create_task, parent, task)

        duration = str(round(time() - st, 2))
        obj_res = {'message': "Task '%s' for '%s' took %s seconds to complete."
                              % ('run_raw_data_se_short', se_short, duration)}
        return Response(obj_res)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


# Cron Job (every 15min on weekdays)
# Can be called out of business-hours to check non-considered Assets
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def update_realtime_se_short(request, se_short, apiKey=None):
    if apiKey == settings.API_KEY:
        m15.update_realtime_se_short(se_short)

        obj_res = {'message': "success."}
        return Response(obj_res)
    else:
        return HttpResponse(status=status.HTTP_403_FORBIDDEN)


# Task Queues
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
