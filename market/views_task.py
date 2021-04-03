from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response

from django_engine import settings
from market.managers.RawDataManager import RawDataManager
from market.managers.RealtimeManager import RealtimeManager
from market import models


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def update_stock_exchange_list(request, apiKey=None):
    if apiKey == settings.API_KEY:
        kwargs = {
            'context': 'RawDataManager.update_stock_exchange_list'}
        raw_data_manager = RawDataManager(kwargs=kwargs)
        result = raw_data_manager.update_stock_exchange_list()
        return Response(result)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def update_asset_profile(request, symbol, apiKey=None):
    if apiKey == settings.API_KEY:
        asset = get_object_or_404(models.Asset, pk=symbol)

        asset.update_profile()

        result = {'context': 'Asset.update_profile.%s' % symbol,
                  'message': 'Done.'}
        return Response(result)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def run_raw_data_stock_exchange_offline(request, interval, stock_exchange, apiKey=None):
    if apiKey == settings.API_KEY:
        stock_exchange = get_object_or_404(models.StockExchange, pk=stock_exchange)

        kwargs = {'context': 'RawDataManager.run_raw_stock_exchange_offline.%s.%s' % (stock_exchange.se_short, interval)}
        raw_data_manager = RawDataManager(kwargs=kwargs)
        result = raw_data_manager.run_stock_exchange(interval=interval,
                                                     stock_exchange=stock_exchange,
                                                     only_offline=True)
        return Response(result)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def run_raw_data_asset_offline(request, interval, symbol, apiKey=None):
    if apiKey == settings.API_KEY:
        asset = get_object_or_404(models.Asset, pk=symbol)

        kwargs = {'context': 'RawDataManager.run_raw_asset_offline.%s.%s' % (interval, symbol)}
        raw_data_manager = RawDataManager(kwargs)
        result = raw_data_manager.run_asset(interval=interval,
                                            asset=asset,
                                            only_offline=True)

        return Response(result)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def run_setup_stock_exchange_offline(request, interval, stock_exchange, apiKey=None):
    if apiKey == settings.API_KEY:
        stock_exchange = get_object_or_404(models.StockExchange, pk=stock_exchange)

        kwargs = {'context': 'RawDataManager.run_setup_stock_exchange_offline.%s.%s' % (stock_exchange.se_short,
                                                                                        interval)}
        raw_data_manager = RawDataManager(kwargs=kwargs)
        result = raw_data_manager.run_stock_exchange(interval=interval,
                                                     stock_exchange=stock_exchange,
                                                     only_phi_trader=True)
        return Response(result)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def run_setup_asset_offline(request, interval, symbol, apiKey=None):
    if apiKey == settings.API_KEY:
        asset = get_object_or_404(models.Asset, pk=symbol)

        kwargs = {'context': 'RawDataManager.run_setup_asset_offline.%s.%s' % (interval, symbol)}
        raw_data_manager = RawDataManager(kwargs)
        result = raw_data_manager.run_asset(interval=interval, asset=asset, only_phi_trader=True)

        return Response(result)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def run_raw_data_asset(request, interval, symbol, last_periods=5, apiKey=None):
    if apiKey == settings.API_KEY:
        asset = get_object_or_404(models.Asset, asset_symbol=symbol)

        kwargs = {'context': 'RawDataManager.run_raw_asset.%s.%s' % (symbol, interval)}
        raw_data_manager = RawDataManager(kwargs=kwargs)
        result = raw_data_manager.run_asset(interval=interval, asset=asset, last_periods=last_periods)

        return Response(result)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def update_realtime_asset(request, symbol, apiKey=None):
    if apiKey == settings.API_KEY:
        asset = get_object_or_404(models.Asset, asset_symbol=symbol)

        kwargs = {'context': 'RealtimeManager.update_realtime_asset.%s' % symbol}
        realtime_manager = RealtimeManager(kwargs=kwargs)
        result = realtime_manager.run_asset(asset=asset)
        return Response(result)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)
