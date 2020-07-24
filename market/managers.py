import inspect
from . import providers


class ProviderManager:
    # Instances of Providers are ordered by priority
    providers_by_action = {
        'assets_by_stock_exchange': [providers.MarketStack(), ],
        'eod': [providers.MarketStack(),
                providers.AlphaVantage()],
        'profile': [providers.Yahoo(), ],
        'realtime': [providers.Yahoo(), ],
        'stock_exchange': [providers.MarketStack(), ],
    }

    # utils
    def get_context(self):
        class_name = self.__class__.__name__
        caller_name = inspect.stack()[1].function
        return str('%s.%s' % (class_name, caller_name))

    # services
    def get_stock_exchange_list(self):
        for provider in self.providers_by_action['stock_exchange']:
            result = provider.get_stock_exchange_list()

            if result['status'] == 200:
                return result['data']

        # Went through all providers and couldn't get a validated data.
        from market.models import Logging
        log = Logging()

        log_level = 'info'
        context = self.get_context()
        msg = str('No providers could retrieve data for Stock Exchange List')
        log.log_into_db(level=log_level, context=context, message=msg)
        return {}

    def get_stock_exchange_data(self, se_short):
        for provider in self.providers_by_action['stock_exchange']:
            result = provider.get_stock_exchange_data(se_short=se_short)

            if result['status'] == 200:
                return result['data']

        # Went through all providers and couldn't get a validated data.
        from market.models import Logging
        log = Logging()

        log_level = 'info'
        context = self.get_context()
        msg = str('No providers could retrieve data for Stock Exchange List')
        log.log_into_db(level=log_level, context=context, message=msg)
        return {}

    def get_assets_by_stock_exchange(self, se_short=None):
        for provider in self.providers_by_action['assets_by_stock_exchange']:
            result = provider.get_assets_by_stock_exchange(se_short)

            if result['status'] == 200:
                return result['data']

        # Went through all providers and couldn't get a validated data.
        from market.models import Logging
        log = Logging()

        log_level = 'info'
        context = self.get_context()
        msg = str('No providers could retrieve data on symbol \'%s\'' % se_short)
        log.log_into_db(level=log_level, context=context, message=msg)
        return {}

    def get_eod_data(self, asset_symbol, last_x_rows):
        for provider in self.providers_by_action['eod']:
            result = provider.get_eod_data(asset_symbol, last_x_rows)

            if result['status'] == 200:
                return result['data']

        # Went through all providers and couldn't get a validated data.
        from market.models import Logging
        log = Logging()

        log_level = 'info'
        context = self.get_context()
        msg = str('No providers could retrieve data on symbol \'%s\'' % asset_symbol)
        log.log_into_db(level=log_level, context=context, message=msg)
        return {}

    def get_profile_data(self, asset_symbol):
        for provider in self.providers_by_action['profile']:
            result = provider.get_profile_data(asset_symbol)

            if result['status'] == 200:
                return result['data']

        # Went through all providers and couldn't get a validated data.
        from market.models import Logging
        log = Logging()

        log_level = 'info'
        context = self.get_context()
        msg = str('No providers could retrieve data on symbol \'%s\'' % asset_symbol)
        log.log_into_db(level=log_level, context=context, message=msg)
        return {}

    def get_realtime_data(self, asset_symbol):
        for provider in self.providers_by_action['realtime']:
            result = provider.get_realtime_data(asset_symbol)

            if result['status'] == 200:
                return result['data']

        # Went through all providers and couldn't get a validated data.
        from market.models import Logging
        log = Logging()

        log_level = 'info'
        context = self.get_context()
        msg = str('No providers could retrieve data on symbol \'%s\'' % asset_symbol)
        log.log_into_db(level=log_level, context=context, message=msg)
        return {}
