from django.db.models import Q
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics, permissions
from rest_framework import status
from rest_framework.response import Response

from django_engine.functions import generic
from api_engine import serializers
from market.models import StockExchange, Asset, D_raw, TechnicalCondition, D_setup, D_setupSummary
from market.cron import m15, daily, monthly

from datetime import datetime, timedelta
from time import time

from google.cloud import tasks_v2
from concurrent.futures import ThreadPoolExecutor as ThreadPool

__project__ = 'backend-phioon-prd'
__queue__ = 'market-queue'
__location__ = 'southamerica-east1'
# __apiBase__ = 'https://backend.phioon.com/market/api/'
__apiBase__ = 'http://127.0.0.1:8000/api/market/'
__apiKey__ = 'ycjOzOP5loHPPIbfMW6tA7AreqAlq0z4yqxStxk2B8Iwges581rK5V8kIgg4'


# INIT
def market_init(request, apiKey=None):
    if apiKey == __apiKey__:
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
        seList = ['BVMF']

        return StockExchange.objects.filter(pk__in=seList)


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
        ignore_assets = self.request.query_params.get('ignoreAssets')

        if stockExchange:
            if ignore_assets:
                ignore_assets = ignore_assets.split(',')
            return Asset.objects.filter(stockExchange__se_short__exact=stockExchange).exclude(asset_symbol__in=ignore_assets)
        else:
            assets = assets.split(',')

            # Log into DB last_access_time. It is used for deciding which Assets will have realtime data stored.
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
def updateStockExchangeList(request, apiKey=None):
    if apiKey == __apiKey__:
        st = time()
        monthly.updateStockExchangeData()
        duration = str(round(time() - st, 2))
        obj_res = {'message': "Task '%s' took %s seconds to complete."
                              % ('updateStockExchangeList', duration)}
        return Response(obj_res)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


# Cron Job (1st of month at 22:00)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def updateAssetList(request, se_short, apiKey=None):
    if apiKey == __apiKey__:
        st = time()
        monthly.updateAssetData(se_short=se_short)
        duration = str(round(time() - st, 2))
        obj_res = {'message': "Task '%s' for '%s' took %s seconds to complete."
                              % ('updateAssetList', se_short, duration)}
        return Response(obj_res)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


# Cron Job (Daily on weekdays)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def runSymbols_D(request, se_short, lastXrows=5, apiKey=None):
    if apiKey == __apiKey__:
        st = time()
        assets = list(Asset.objects.filter(asset_isException=False, stockExchange=se_short)
                      .values_list('asset_symbol', flat=True))
        if len(assets) == 0:
            return

        client = tasks_v2.CloudTasksClient()
        parent = client.queue_path(__project__, __location__, __queue__)

        with ThreadPool() as t:
            for x in range(len(assets)):
                url = __apiBase__ + 'task/runSymbol/D/'
                url += assets[x] + '/'
                url += str(lastXrows) + '/'
                url += __apiKey__
                task = {
                    'http_request': {
                        'http_method': 'GET',
                        'url': url}}
                t.submit(client.create_task, parent, task)

        duration = str(round(time() - st, 2))
        obj_res = {'message': "Task '%s' for '%s' took %s seconds to complete."
                              % ('runSymbols_D', se_short, duration)}
        return Response(obj_res)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


# Cron Job (every 15min on weekdays)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def updateAssetPrices(request, se_short, apiKey=None):
    if apiKey == __apiKey__:
        st = time()
        m15.updatePrices(se_short)
        duration = str(round(time() - st, 2))

        obj_res = {'message': "Task '%s' for '%s' took %s seconds to complete."
                              % ('updateAssetPrices', se_short, duration)}
        return Response(obj_res)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


# Task Queues
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def runSymbol_D(request, symbol, lastXrows=5, apiKey=None):
    if apiKey == __apiKey__:
        daily.updateRawData(symbol=symbol, lastXrows=lastXrows)

        obj_res = {'message': "success"}
        return Response(obj_res)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def updateAssetPrice(request, symbol, apiKey=None):
    if apiKey == __apiKey__:
        m15.updatePrice(symbol)

        obj_res = {'message': "success."}
        return Response(obj_res)
    else:
        return HttpResponse(status=status.HTTP_403_FORBIDDEN)
