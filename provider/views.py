from rest_framework import generics, permissions
from rest_framework.response import Response

from django_engine import settings
from . import serializers
from . import messages
from market.models import StockExchange, Asset, Profile, Realtime


class ExchangeDetail(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.ExchangeSerializer

    def get_queryset(self):
        exchange = self.request.parser_context['kwargs']['exchange']
        return StockExchange.objects.get(pk=exchange)

    def get(self, request, *args, **kwargs):
        api_key = self.request.query_params.get('api_key')

        if api_key == settings.API_KEY:
            serializer = self.get_serializer(self.get_queryset())
            obj_res = {'data': serializer.data}
            return Response(obj_res)
        else:
            obj_res = {'message': messages.get_message('enUS', 'generic', 'invalid_api_key')}
            return Response(obj_res)


class ExchangeList(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.ExchangeSerializer
    queryset = StockExchange.objects.all()

    def get(self, request, *args, **kwargs):
        api_key = self.request.query_params.get('api_key')

        if api_key == settings.API_KEY:
            serializer = self.get_serializer(self.get_queryset(), many=True)
            obj_res = {'data': serializer.data}
            return Response(obj_res)
        else:
            obj_res = {'message': messages.get_message('enUS', 'generic', 'invalid_api_key')}
            return Response(obj_res)


class TickersByExchange(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.TickersByExchangeSerializer

    def get_queryset(self):
        exchange = self.request.parser_context['kwargs']['exchange']
        return StockExchange.objects.get(se_short=exchange)

    def get(self, request, *args, **kwargs):
        api_key = self.request.query_params.get('api_key')

        if api_key == settings.API_KEY:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset)

            obj_res = {'data': serializer.data}
            return Response(obj_res)
        else:
            obj_res = {'message': messages.get_message('enUS', 'generic', 'invalid_api_key')}
            return Response(obj_res)


class AssetProfileDetail(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.ProfileSerializer

    def get_queryset(self):
        ticker = self.request.parser_context['kwargs']['ticker']
        return Profile.objects.get(asset_id=ticker)

    def get(self, request, *args, **kwargs):
        api_key = self.request.query_params.get('api_key')

        if api_key == settings.API_KEY:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset)

            obj_res = {'data': serializer.data}
            return Response(obj_res)
        else:
            obj_res = {'message': messages.get_message('enUS', 'generic', 'invalid_api_key')}
            return Response(obj_res)


class AssetRealtimeDetail(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.RealtimeSerializer

    def get_queryset(self):
        ticker = self.request.parser_context['kwargs']['ticker']
        return Realtime.objects.get(asset_id=ticker)

    def get(self, request, *args, **kwargs):
        api_key = self.request.query_params.get('api_key')

        if api_key == settings.API_KEY:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset)

            obj_res = {'data': serializer.data}
            return Response(obj_res)
        else:
            obj_res = {'message': messages.get_message('enUS', 'generic', 'invalid_api_key')}
            return Response(obj_res)


class EodList(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.EodSerializer

    def get_queryset(self):
        ticker = self.request.parser_context['kwargs']['ticker']
        return Asset.objects.get(pk=ticker)

    def get(self, request, *args, **kwargs):
        api_key = self.request.query_params.get('api_key')

        if api_key == settings.API_KEY:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset)

            obj_res = {'data': serializer.data}
            return Response(obj_res)
        else:
            obj_res = {'message': messages.get_message('enUS', 'generic', 'invalid_api_key')}
            return Response(obj_res)
