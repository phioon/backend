from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response

from django_engine import settings
from market import models
from market.managers.RawDataManager import RawDataManager
from market.managers.RealtimeManager import RealtimeManager


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def update_asset_list(request, stock_exchange, apiKey=None):
    if apiKey == settings.API_KEY:
        stock_exchange = get_object_or_404(models.StockExchange, pk=stock_exchange)

        kwargs = {'context': 'RawDataManager.update_asset_list.%s' % stock_exchange.se_short}
        raw_data_manager = RawDataManager(kwargs)
        result = raw_data_manager.update_asset_list(stock_exchange=stock_exchange)

        return Response(result)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


# Cron Job (Daily on weekdays)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def run_raw_data_stock_exchange(request, interval, stock_exchange, last_periods=5, apiKey=None):
    if apiKey == settings.API_KEY:
        stock_exchange = get_object_or_404(models.StockExchange, pk=stock_exchange)

        kwargs = {'context': 'RawDataManager.run_raw_stock_exchange.%s.%s' % (stock_exchange.se_short, interval)}
        raw_data_manager = RawDataManager(kwargs)
        result = raw_data_manager.run_stock_exchange(interval=interval,
                                                     stock_exchange=stock_exchange,
                                                     last_periods=last_periods)
        return Response(result)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


# Cron Job (every 15min on weekdays)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def update_realtime_stock_exchange(request, stock_exchange, apiKey=None):
    if apiKey == settings.API_KEY:
        stock_exchange = get_object_or_404(models.StockExchange, pk=stock_exchange)

        kwargs = {'context': 'RealtimeManager.run_stock_exchange.%s' % stock_exchange.se_short}
        realtime_manager = RealtimeManager(kwargs)
        result = realtime_manager.run_stock_exchange(stock_exchange=stock_exchange)

        return Response(result)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)
