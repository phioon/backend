from django.db.models import Q

from django_engine import settings
from market.managers.ProviderManager import ProviderManager
from market import models

from google.cloud import tasks_v2
from datetime import datetime, timedelta


class RealtimeManager:
    task_urls = {
        'realtime': settings.MARKET_API_BASE + 'task/update_realtime_from_intraday_data/asset/<asset_symbol>/<api_key>/',
    }
    context = None

    def __init__(self, kwargs=None):
        if kwargs is None:
            kwargs = {}

        for [k, v] in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)

    def run_stock_exchange(self, stock_exchange):
        result = {'context': self.context}
        today = datetime.today().date()
        a_month_ago = today - timedelta(days=30)

        if today.weekday() in [5, 6]:
            result['message'] = 'Today is not a weekday.'
            return result

        assets = stock_exchange.assets.filter(
            Q(last_access_time__gte=a_month_ago) | Q(is_considered_for_analysis=True))

        if settings.ACCESS_PRD_DB:
            client = tasks_v2.CloudTasksClient()
            parent = client.queue_path(settings.GAE_PROJECT,
                                       settings.GAE_QUEUES['market-realtime']['location'],
                                       settings.GAE_QUEUES['market-realtime']['name'])

            for asset in assets:
                url = self.task_urls['realtime']
                url = url.replace('<asset_symbol>', asset.asset_symbol)
                url = url.replace('<api_key>', settings.API_KEY)

                task = {
                    'http_request': {
                        'http_method': 'GET',
                        'url': url}}
                client.create_task(parent=parent, task=task)
        else:
            for asset in assets:
                print('Working on %s...' % asset.asset_symbol)
                self.run_asset(asset)

        assets = list(assets.values_list('asset_symbol', flat=True))
        result['message'] = "[%s] Assets to be updated: %s" % (stock_exchange, assets)
        return result

    def run_asset(self, asset):
        provider_manager = ProviderManager()
        data = provider_manager.get_realtime_data(asset_symbol=asset.asset_symbol)

        try:
            realtime = models.Realtime.objects.get(asset=asset)
        except models.Realtime.DoesNotExist:
            realtime = models.Realtime(asset=asset)

        if data:
            realtime.last_trade_time = data['last_trade_time']
            if data['open']:
                realtime.open = data['open']
            if data['high']:
                realtime.high = data['high']
            if data['low']:
                realtime.low = data['low']
            if data['price']:
                realtime.price = data['price']
            if data['volume']:
                realtime.volume = data['volume']
            if data['pct_change']:
                realtime.pct_change = data['pct_change']

            realtime.save()

        result = {
            'context': self.context,
            'message': 'Done.'}
        return result
