from django.utils import timezone
from django.db.models import Q

from django_engine import settings
from market import models
from market.managers.ProviderManager import ProviderManager
from market.managers.RealtimeManager import RealtimeManager
from market.managers.playbooks.D_rawData import D_rawData

from google.cloud import tasks_v2
from datetime import datetime, timedelta
import pytz


class RawDataManager:
    task_urls = {
        'profile': settings.MARKET_API_BASE + 'task/update_profile/asset/<asset_symbol>/<api_key>/',
        'raw': settings.MARKET_API_BASE + 'task/run_raw/<interval>/asset/<asset_symbol>/<last_periods>/<api_key>/',
        'raw_offline': settings.MARKET_API_BASE + 'task/offline/run_raw/<interval>/asset/<asset_symbol>/<api_key>/',
        'setup_offline': settings.MARKET_API_BASE + 'task/offline/run_setup/<interval>/asset/<asset_symbol>/<api_key>/',

        # 'raw_d': settings.MARKET_API_BASE + 'task/run_raw/d/asset/',
        # 'raw_d_offline': settings.MARKET_API_BASE + 'task/offline/run_raw/d/asset/',
        # 'setup_d_offline': settings.MARKET_API_BASE + 'task/offline/run_setup/d/asset/',
    }
    playbook = None

    context = None
    interval = 'd'

    def __init__(self, kwargs=None):
        # defaults
        self.interval = 'd'

        if kwargs is None:
            kwargs = {}

        for [k, v] in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)

    # Stock Exchange
    def run_stock_exchange(self, interval, stock_exchange, last_periods=10, only_offline=False, only_phi_trader=False):
        self.interval = str(interval).lower()
        result = {}

        # 2. Executing playbook according to the interval
        if self.interval == 'd':
            if only_offline or only_phi_trader:
                result = self.run_d_stock_exchange_offline(stock_exchange=stock_exchange,
                                                           only_phi_trader=only_phi_trader)
            else:
                result = self.run_d_stock_exchange(stock_exchange=stock_exchange,
                                                   last_periods=last_periods)

        return result

    def run_d_stock_exchange(self, stock_exchange, last_periods):
        tz = pytz.timezone(stock_exchange.timezone)
        today = datetime.today().astimezone(tz)
        a_month_ago = today - timedelta(days=30)

        # Once we got a bigger plan with Providers, switch it to all assets (line bellow)
        # assets = Asset.objects.filter(stock_exchange=stock_exchange)
        sync_list = []
        assets = stock_exchange.assets.filter(
            Q(last_access_time__gte=a_month_ago) | Q(is_considered_for_analysis=True))

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
        else:
            # SUN: Latest EOD data on DB must be Friday's.
            delta_days_tolerance = 3

        for asset in assets:
            draws = asset.draws

            if draws.count() > 0:
                latest_draw = asset.draws.order_by('-d_datetime')[0]
                latest_datetime = datetime.strptime(latest_draw.d_datetime, '%Y-%m-%d %H:%M:%S')
                latest_datetime = timezone.make_aware(latest_datetime, tz)
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
                url = self.task_urls['raw']
                url = url.replace('<interval>', 'd')
                url = url.replace('<asset_symbol>', asset.asset_symbol)
                url = url.replace('<last_periods>', str(last_periods))
                url = url.replace('<api_key>', settings.API_KEY)

                task = {
                    'http_request': {
                        'http_method': 'GET',
                        'url': url}}
                client.create_task(parent=parent, task=task)
        else:
            for asset in sync_list:
                print('Working on %s...' % asset.asset_symbol)
                self.run_asset(interval=self.interval, asset=asset, last_periods=last_periods)

        result = {
            'context': self.context,
            'message': "Assets to be updated: %s" % sync_list}
        return result

    def run_d_stock_exchange_offline(self, stock_exchange, only_phi_trader):
        sync_list = []
        assets = stock_exchange.assets.filter(is_considered_for_analysis=True)
        last_periods = 10000
        only_offline = True

        for asset in assets:
            if asset.draws.count() > 0:
                sync_list.append(asset)

        if settings.ACCESS_PRD_DB:
            client = tasks_v2.CloudTasksClient()
            parent = client.queue_path(settings.GAE_PROJECT,
                                       settings.GAE_QUEUES['market-eod']['location'],
                                       settings.GAE_QUEUES['market-eod']['name'])

            for asset in sync_list:
                if only_phi_trader:
                    url = self.task_urls['setup_offline']
                else:
                    url = self.task_urls['raw_offline']
                url = url.replace('<interval>', 'd')
                url = url.replace('<asset_symbol>', asset.asset_symbol)
                url = url.replace('<api_key>', settings.API_KEY)

                task = {
                    'http_request': {
                        'http_method': 'GET',
                        'url': url}}
                client.create_task(parent=parent, task=task)
        else:
            for asset in sync_list:
                print('Working on %s...' % asset.asset_symbol)
                self.run_asset(interval=self.interval,
                               asset=asset,
                               last_periods=last_periods,
                               only_offline=only_offline,
                               only_phi_trader=only_phi_trader)

        result = {
            'context': self.context,
            'message': "[%s] Assets to be updated: %s" % (stock_exchange, sync_list)}
        return result

    def update_stock_exchange_list(self):
        provider_manager = ProviderManager()
        data = provider_manager.get_stock_exchange_list()

        created_list = []
        updated_list = []

        for obj in data:
            se_short = obj['se_short']

            if models.StockExchange.filter(se_short=se_short).exists():
                updated_list.append(se_short)
            else:
                created_list.append(se_short)

            models.StockExchange.objects.update_or_create(
                se_short=se_short,
                defaults={
                    'name': obj['name'],
                    'timezone': obj['timezone'],
                    'country_code': obj['country_code'],
                    'currency_code': obj['currency_code'],
                    'website': obj['website']
                })

        result = {
            'context': self.context,
            'created': created_list,
            'updated': updated_list}
        return result

    def update_asset_list(self, stock_exchange):
        # 1. Requirements
        provider_manager = ProviderManager()
        data = provider_manager.get_assets_by_stock_exchange(stock_exchange=stock_exchange.se_short)

        client = tasks_v2.CloudTasksClient()
        parent = client.queue_path(settings.GAE_PROJECT,
                                   settings.GAE_QUEUES['market-asset']['location'],
                                   settings.GAE_QUEUES['market-asset']['name'])
        created_list = []
        profile_list = []

        # 2. Iterating over list of Profiles
        for obj in data:
            asset_symbol = obj['asset_symbol']
            asset, created = models.Asset.objects.get_or_create(asset_symbol=asset_symbol,
                                                                stock_exchange=stock_exchange)
            if created:
                created_list.append(asset.asset_symbol)

            try:
                # Try to add asset_symbol into [profile_list], but only if timedelta is greater than 25 days.
                profile_mtime = asset.profile.modified_time

                today = datetime.today().date()
                delta = today - profile_mtime

                if delta >= timedelta(days=25):
                    profile_list.append(asset_symbol)

            except models.Asset.profile.RelatedObjectDoesNotExist:
                # Asset exists, but doesn't have a Profile instance yet
                profile_list.append(asset_symbol)

            # 2.1 Handling assets that need a Profile Update
            if asset.asset_symbol in profile_list:
                # Updating Profile
                if settings.ACCESS_PRD_DB:
                    url = self.task_urls['profile']
                    url = url.replace('<asset_symbol>', asset.asset_symbol)
                    url = url.replace('<api_key>', settings.API_KEY)

                    task = {
                        'http_request': {
                            'http_method': 'GET',
                            'url': url}}
                    client.create_task(parent=parent, task=task)
                else:
                    print('Updating profile for %s...' % asset.asset_symbol)
                    asset.update_profile()

            # 2.2 Handling assets that just got created
            if asset.asset_symbol in created_list:
                # Updating Profile
                if settings.ACCESS_PRD_DB:
                    url = self.task_urls['raw']
                    url = url.replace('<interval>', 'd')
                    url = url.replace('<asset_symbol>', asset.asset_symbol)
                    url = url.replace('<last_periods>', '0')
                    url = url.replace('<api_key>', settings.API_KEY)

                    task = {
                        'http_request': {
                            'http_method': 'GET',
                            'url': url}}
                    client.create_task(parent=parent, task=task)
                else:
                    print('Generating raw data for %s...' % asset.asset_symbol)
                    self.run_asset(interval=self.interval, asset=asset, last_periods=0)

        result = {
            'context': self.context,
            'assets_created': created_list,
            'profiles_updated': profile_list}
        return result

    # Asset
    def run_asset(self, interval, asset, last_periods=10, only_offline=False, only_phi_trader=False):
        self.interval = str(interval).lower()
        result = {'context': self.context}

        # 1. Adjustments
        if only_offline:
            last_periods = 10000

        # 2. Selecting Playbook according to the interval
        if self.interval == 'd':
            kwargs = {'asset': asset, 'last_periods': last_periods}
            self.playbook = D_rawData(kwargs=kwargs)

        # 3. Executing Playbook
        if self.playbook:
            if only_phi_trader:
                self.playbook.run_phi_trader()
            else:
                self.playbook.run(only_offline=only_offline)
            result['message'] = 'Done.'
        else:
            result['message'] = 'No playbook has been found.'

        return result

    def update_last_access_time(self, assets):
        assets = models.Asset.objects.filter(pk__in=assets)
        today = datetime.today().date()
        refresh_access = None

        for asset in assets:
            if (today - asset.last_access_time) >= timedelta(days=30):
                # If Asset hasn't synchronized for 30 days or more,
                # it must sync now before return data to frontend
                refresh_access = True

                # Get latest Realtime data
                realtime_manager = RealtimeManager()
                realtime_manager.run_asset(asset)

                # Run a full sync
                if not asset.is_considered_for_analysis:
                    self.run_asset(interval='d', asset=asset, last_periods=5000)

            elif (today - asset.last_access_time) >= timedelta(days=1):
                refresh_access = True

        if refresh_access:
            assets.update(last_access_time=today)
