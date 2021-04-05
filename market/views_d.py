from django.db.models import Q
from django.core import serializers as django_serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics, permissions
from rest_framework.response import Response

from market import serializers, models, models_d

from datetime import datetime, timedelta
import json


class D_RawList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        detailed = str(self.request.query_params.get('detailed')).lower()
        if detailed == 'true':
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

        return models_d.D_raw.objects.filter(asset=asset,
                                             d_datetime__gte=dateFrom,
                                             d_datetime__lte=dateTo + ' 23:59:59')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def d_sma_latest_list(request):
    stock_exchange = request.query_params.get('stockExchange')
    assets = request.query_params.get('assets')
    last_periods = int(request.query_params.get('lastPeriods'))
    instances = request.query_params.get('instances')
    instances = instances.split(',')
    result = {
        'latest_datetime': None,
        'data': []
    }

    if last_periods is None or last_periods <= 0 or last_periods >= 10:
        last_periods = 1

    dates = models_d.D_raw.objects.values('d_datetime').distinct().order_by('-d_datetime')
    date_from = dates[last_periods - 1]['d_datetime']
    result['latest_datetime'] = dates[0]['d_datetime']

    # Define which assets are selected
    if stock_exchange:
        assets = models.Asset.objects.filter(stock_exchange=stock_exchange, is_considered_for_analysis=True)
    else:
        assets = assets.split(',')
        assets = models.Asset.objects.filter(pk__in=assets, is_considered_for_analysis=True)

    # Append data into result
    for asset in assets:
        objs = list(models_d.D_sma.objects.filter(d_raw__asset=asset, d_raw__d_datetime__gte=date_from)
                    .order_by('-asset_datetime'))

        if len(objs) != last_periods:
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
def d_ema_latest_list(request):
    stock_exchange = request.query_params.get('stockExchange')
    assets = request.query_params.get('assets')
    last_periods = int(request.query_params.get('lastPeriods'))
    instances = request.query_params.get('instances')
    instances = instances.split(',')
    result = {
        'latest_datetime': None,
        'data': []
    }

    if last_periods is None or last_periods <= 0 or last_periods >= 10:
        last_periods = 1

    dates = models_d.D_raw.objects.values('d_datetime').distinct().order_by('-d_datetime')
    date_from = dates[last_periods - 1]['d_datetime']
    result['latest_datetime'] = dates[0]['d_datetime']

    # Define which assets are selected
    if stock_exchange:
        assets = models.Asset.objects.filter(stock_exchange=stock_exchange, is_considered_for_analysis=True)
    else:
        assets = assets.split(',')
        assets = models.Asset.objects.filter(pk__in=assets, is_considered_for_analysis=True)

    # Append data into result
    for asset in assets:
        objs = list(models_d.D_ema.objects.filter(d_raw__asset=asset, d_raw__d_datetime__gte=date_from)
                    .order_by('-asset_datetime'))

        if len(objs) != last_periods:
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
def d_quote_latest_list(request):
    stock_exchange = request.query_params.get('stockExchange')
    assets = request.query_params.get('assets')
    last_periods = int(request.query_params.get('lastPeriods'))
    instances = request.query_params.get('instances')
    instances = instances.split(',')
    result = {
        'latest_datetime': None,
        'data': []
    }

    if last_periods is None or last_periods <= 0 or last_periods >= 10:
        last_periods = 1

    dates = models_d.D_raw.objects.values('d_datetime').distinct().order_by('-d_datetime')
    date_from = dates[last_periods - 1]['d_datetime']
    result['latest_datetime'] = dates[0]['d_datetime']

    # Define which assets are selected
    if stock_exchange:
        assets = models.Asset.objects.filter(stock_exchange=stock_exchange, is_considered_for_analysis=True)
    else:
        assets = assets.split(',')
        assets = models.Asset.objects.filter(pk__in=assets, is_considered_for_analysis=True)

    # Append data into result
    for asset in assets:
        raw_objs = list(models_d.D_raw.objects.filter(asset=asset, d_datetime__gte=date_from)
                        .order_by('-asset_datetime'))
        raw_objs = json.loads(django_serializers.serialize('json', raw_objs))

        if len(raw_objs) != last_periods:
            # There is no enough data in database
            continue

        if raw_objs:
            # 'raw_objs' is valid and the amount of raw objects is the same as 'lastPeriods'
            if hasattr(asset, 'realtime'):
                # Asset has Realtime instance
                last_trade_time = asset.realtime.last_trade_time

                if last_trade_time[0:10] > raw_objs[0]['fields']['d_datetime'][0:10]:
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
def d_phibo_latest_list(request):
    stock_exchange = request.query_params.get('stockExchange')
    assets = request.query_params.get('assets')
    last_periods = int(request.query_params.get('lastPeriods'))
    instances = request.query_params.get('instances')
    instances = instances.split(',')
    result = {
        'latest_datetime': None,
        'data': []
    }

    if last_periods is None or last_periods <= 0 or last_periods >= 10:
        last_periods = 1

    dates = models_d.D_raw.objects.values('d_datetime').distinct().order_by('-d_datetime')
    date_from = dates[last_periods - 1]['d_datetime']
    result['latest_datetime'] = dates[0]['d_datetime']

    # Define which assets are selected
    if stock_exchange:
        assets = models.Asset.objects.filter(stock_exchange=stock_exchange, is_considered_for_analysis=True)
    else:
        assets = assets.split(',')
        assets = models.Asset.objects.filter(pk__in=assets, is_considered_for_analysis=True)

    # Append data into result
    for asset in assets:
        objs = list(models_d.D_pvpc.objects.filter(d_raw__asset=asset, d_raw__d_datetime__gte=date_from)
                    .order_by('-asset_datetime'))

        if len(objs) != last_periods:
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
def d_roc_latest_list(request):
    stock_exchange = request.query_params.get('stockExchange')
    assets = request.query_params.get('assets')
    last_periods = int(request.query_params.get('lastPeriods'))
    instances = request.query_params.get('instances')
    instances = instances.split(',')
    result = {
        'latest_datetime': None,
        'data': []
    }

    if last_periods is None or last_periods <= 0 or last_periods >= 10:
        last_periods = 1

    dates = models_d.D_raw.objects.values('d_datetime').distinct().order_by('-d_datetime')
    date_from = dates[last_periods - 1]['d_datetime']
    result['latest_datetime'] = dates[0]['d_datetime']

    # Define which assets are selected
    if stock_exchange:
        assets = models.Asset.objects.filter(stock_exchange=stock_exchange, is_considered_for_analysis=True)
    else:
        assets = assets.split(',')
        assets = models.Asset.objects.filter(pk__in=assets, is_considered_for_analysis=True)

    # Append data into result
    for asset in assets:
        objs = list(models_d.D_roc.objects.filter(d_raw__asset=asset, d_raw__d_datetime__gte=date_from)
                    .order_by('-asset_datetime'))

        if len(objs) != last_periods:
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
    serializer_class = serializers.D_phiOperationSerializer

    def get_queryset(self):
        stock_exchange = self.request.query_params.get('stockExchange')
        date_from = self.request.query_params.get('dateFrom')

        if date_from is None:
            date_from = str(datetime.today().date() - timedelta(days=45))

        setups = models_d.D_phiOperation.objects.filter(
            Q(d_raw__asset__stock_exchange__exact=stock_exchange, is_public=True),
            Q(ended_on__isnull=True) | Q(radar_on__gte=date_from))

        return setups


class D_SetupStatsList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.D_phiStatsSerializer

    def get_queryset(self):
        stock_exchange = self.request.query_params.get('stockExchange')
        date_from = self.request.query_params.get('dateFrom')

        if date_from is None:
            date_from = str(datetime.today().date() - timedelta(days=90))

        phi_operations = models_d.D_phiOperation.objects\
            .filter(Q(d_raw__asset__stock_exchange__exact=stock_exchange, is_public=True),
                    Q(ended_on__isnull=True) | Q(radar_on__gte=date_from))\
            .values('tc_id', 'asset_id')\
            .distinct()

        tc_ids = phi_operations.values_list('tc_id')
        asset_symbols = phi_operations.values_list('asset_id')

        stats_data = models_d.D_phiStats.objects.filter(tc_id__in=tc_ids, asset_id__in=asset_symbols)

        return stats_data
