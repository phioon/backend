import inspect
from .functions import utils as phioon_utils
from . import providers


class ProviderManager:
    # Providers instances are ordered by priority
    providers_by_action = {
        'assets_by_stock_exchange': [providers.MarketStack(), ],
        'eod': [providers.MarketStack(),
                providers.AlphaVantage(),
                providers.Yahoo()],
        'profile': [providers.Yahoo(), ],
        'realtime': [providers.Yahoo(), ],
        'stock_exchange': [providers.MarketStack(), ],
    }
    trusted_providers = {
        'eod': [providers.Yahoo(), ]
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
        msg = str('[Stock Exchange List] No providers could retrieve data.')
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
        msg = str('[%s] No providers could retrieve data.' % se_short)
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
        msg = str('[%s] No providers could retrieve data.' % se_short)
        log.log_into_db(level=log_level, context=context, message=msg)
        return {}

    def get_eod_data(self, asset_symbol, last_x_periods):
        for provider in self.providers_by_action['eod']:
            result = provider.get_eod_data(asset_symbol, last_x_periods)

            if result['status'] == 200:
                result['validated_data'] = self.validate_initial_data(asset_symbol,
                                                                      provider.id,
                                                                      result['data'],
                                                                      last_x_periods)
                return result['validated_data']
            else:
                self.log_empty_data(asset_symbol, provider.id)

        # Went through all providers and couldn't get a validated data.
        from market.models import Logging
        log = Logging()

        log_level = 'info'
        context = self.get_context()
        msg = str('[%s] No providers could retrieve data.' % asset_symbol)
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
        msg = str('[%s] No providers could retrieve data.' % asset_symbol)
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
        msg = str('[%s] No providers could retrieve data.' % asset_symbol)
        log.log_into_db(level=log_level, context=context, message=msg)
        return {}

    # validators
    def validate_initial_data(self, asset_symbol, provider_id, data, last_x_periods):
        serializer = {
            'asset_symbol': asset_symbol,
            'last_x_periods': last_x_periods,
            'initial_provider': provider_id,
            'initial_data': phioon_utils.order_by_asc(data, 'datetime'),
            'initial_inconsistencies': [],
            'trusted_data': None,
            'validated_data': None
        }

        if last_x_periods > 0:
            # last_x_periods equals to 0 means client is asking for a compact view.
            serializer['initial_data'] = self.shrink_data(serializer['initial_data'], last_x_periods)

        serializer['initial_inconsistencies'] = self.get_eod_inconsistencies(serializer,
                                                                             provider_id,
                                                                             data_key='initial_data')

        # Join all inconsistent dates into a list
        inconsistent_dates = []
        for dates in serializer['initial_inconsistencies']['result'].values():
            inconsistent_dates.extend(dates)

        if serializer['initial_inconsistencies']['amount'] > 0:
            # There are inconsistencies to be checked
            serializer = self.replace_inconsistencies_with_trusted_data(serializer,
                                                                        inconsistent_dates)
            serializer['validated_data'] = self.validate_trusted_data(serializer)
        else:
            # No inconsistencies were found
            serializer['validated_data'] = serializer['initial_data']

        serializer['validated_data'] = self.standardize_eod_data(serializer['validated_data'])

        return serializer['validated_data']

    def validate_trusted_data(self, serializer):
        validated_data = []
        inconsistencies = self.get_eod_inconsistencies(serializer,
                                                       provider_id=serializer['trusted_provider'],
                                                       data_key='trusted_data')
        if inconsistencies['amount'] > 0:
            for data in serializer['trusted_data']:
                if data['datetime'] not in inconsistencies['result']['empty_fields']:
                    validated_data.append(data)
        else:
            validated_data = serializer['trusted_data']

        # Inconsistencies that should be ignored once data is confirmed with a trusted provider
        amount = len(inconsistencies['result']['roc_too_high'])
        inconsistencies['result']['roc_too_high'] = []
        inconsistencies['amount'] -= amount
        # -----

        self.log_validation_result(serializer['asset_symbol'], inconsistencies)

        return validated_data

    def standardize_eod_data(self, validated_data):
        # Once empty data is already removed by self.fix_eod_inconsistency,
        # we just need to standardize data before sending it to database.

        for data in validated_data:
            data['open'] = round(data['open'] * data['adj_pct'], 2)
            data['high'] = round(data['high'] * data['adj_pct'], 2)
            data['low'] = round(data['low'] * data['adj_pct'], 2)
            data['close'] = round(data['close'] * data['adj_pct'], 2)
            data['volume'] = int(data['volume'])

        return validated_data

    # general functions
    def get_raw_data_from_db(self, asset_symbol, last_x_periods):
        from market.models import D_raw

        data = {}
        d_raws = list(D_raw.objects.filter(asset_symbol=asset_symbol)
                      .values_list('d_datetime', 'd_open', 'd_high', 'd_low', 'd_close', 'd_volume')
                      .order_by('d_datetime'))

        if last_x_periods > 0:
            d_raws = self.shrink_data(d_raws, last_x_periods)

        for values in d_raws:
            data[values[0]] = {
                    'datetime': values[0],
                    'open': values[1],
                    'high': values[2],
                    'low': values[3],
                    'close': values[4],
                    'volume': values[5]
            }

        return data

    def shrink_data(self, data, last_x_periods):
        data = data[len(data) - last_x_periods:]
        return data

    # EOD: lookup functions
    def get_eod_inconsistencies(self, serializer, provider_id, data_key='initial_data'):
        inconsistencies = {
            'amount': 0,
            'result': {
                'empty_fields': [],
                'roc_too_high': []
            }
        }
        data = {}
        d_raws = self.get_raw_data_from_db(serializer['asset_symbol'], serializer['last_x_periods'])

        # Using date as key...
        date_as_key = phioon_utils.get_field_as_unique_key(serializer[data_key], 'datetime')

        # Looking for empty fields...
        inconsistencies['result']['empty_fields'] = self.get_dates_empty_fields(date_as_key, d_raws)
        inconsistencies['amount'] += len(inconsistencies['result']['empty_fields'])
        # Looking for discrepancy on Rate of Change (ROC) values...
        inconsistencies['result']['roc_too_high'] = self.get_dates_roc_too_high(date_as_key, d_raws)
        inconsistencies['amount'] += len(inconsistencies['result']['roc_too_high'])

        # Logging...
        if inconsistencies['result']['empty_fields']:
            self.log_empty_field(serializer['asset_symbol'],
                                 provider_id,
                                 inconsistencies['result']['empty_fields'])
        if inconsistencies['result']['roc_too_high']:
            self.log_roc_too_high(serializer['asset_symbol'],
                                  provider_id,
                                  inconsistencies['result']['roc_too_high'])

        return inconsistencies

    def get_dates_empty_fields(self, data, d_raws):
        result = []
        for k, v in data.items():
            if not v['open'] and k not in d_raws:
                result.append(k)
            elif not v['high'] and k not in d_raws:
                result.append(k)
            elif not v['low'] and k not in d_raws:
                result.append(k)
            elif not v['close'] and k not in d_raws:
                result.append(k)
            elif not v['volume'] and k not in d_raws:
                result.append(k)

        return result

    def get_dates_roc_too_high(self, data, d_raws):
        result = []
        pct_roc_threshold = 50

        first_data = list(data.values())[0]
        yesterday = {
            'datetime': list(data.keys())[0],
            'open': first_data['open'],
            'high': first_data['high'],
            'low': first_data['low'],
            'close': first_data['close']
        }

        for k, v in data.items():
            # open
            if self.is_roc_too_high(yesterday, v, d_raws, pct_roc_threshold, 'open'):
                result.append(k)

            # high
            elif self.is_roc_too_high(yesterday, v, d_raws, pct_roc_threshold, 'high'):
                result.append(k)

            # low
            elif self.is_roc_too_high(yesterday, v, d_raws, pct_roc_threshold, 'low'):
                result.append(k)

            # close
            elif self.is_roc_too_high(yesterday, v, d_raws, pct_roc_threshold, 'close'):
                result.append(k)

            # Update yesterday's data
            if k not in result:
                yesterday = {
                    'datetime': k,
                    'open': v['open'],
                    'high': v['high'],
                    'low': v['low'],
                    'close': v['close']
                }

        return result

    def is_roc_too_high(self, yesterday, today, d_raws, pct_roc_threshold, field):
        roc = phioon_utils.rate_of_change(yesterday[field], today[field])

        if roc > pct_roc_threshold:
            if today['datetime'] in d_raws:
                # We have today's data on d_raws
                if yesterday['datetime'] in d_raws:
                    # We have yesterday's data on d_raws
                    roc = phioon_utils.rate_of_change(d_raws[yesterday['datetime']][field],
                                                      d_raws[today['datetime']][field])
                    if roc > pct_roc_threshold:
                        # d_raws's data must be validated
                        return True
            else:
                # We don't have today's data on d_raws
                return True

    # EOD: trouble fixers
    def replace_inconsistencies_with_trusted_data(self, serializer, inconsistent_dates):
        # It tries to replace inconsistent data with data from main provider.

        date_as_key = phioon_utils.get_field_as_unique_key(serializer['initial_data'], 'datetime')

        for provider in self.trusted_providers['eod']:
            if provider.id == serializer['initial_provider']:
                # Initial provider is the same as current trusted provider
                continue
            else:
                # Initial provider is not the same as current trusted provider
                result = provider.get_eod_data(serializer['asset_symbol'], serializer['last_x_periods'])

                if result['status'] == 200:
                    serializer['trusted_provider'] = provider.id
                    serializer['trusted_data'] = []

                    for date in inconsistent_dates:
                        trusted_obj = phioon_utils.retrieve_obj_from_obj_list(result['data'], 'datetime', date)

                        if date in date_as_key and trusted_obj and not phioon_utils.has_empty_fields(trusted_obj):
                            date_as_key[date] = trusted_obj

                    for raw_data in date_as_key.values():
                        serializer['trusted_data'].append(raw_data)

                else:
                    serializer['trusted_data'] = serializer['initial_data']

                # Once it found a trusted data, quit iteration
                break

        return serializer

    # loggers
    def log_empty_data(self, asset_symbol, provider_id):
        from market.models import Logging
        log = Logging()

        log_level = 'warning'
        context = self.get_context()
        msg = str('[%s] Provider \'%s\' could not retrieve data.' % (asset_symbol, provider_id))
        log.log_into_db(level=log_level, context=context, message=msg)

    def log_empty_field(self, asset_symbol, provider_id, dates):
        from market.models import Logging
        log = Logging()

        log_level = 'info'
        context = self.get_context()
        msg = str('[%s] Provider \'%s\' has at least one empty field for periods: %s.' % (asset_symbol,
                                                                                          provider_id,
                                                                                          dates))
        log.log_into_db(level=log_level, context=context, message=msg)

    def log_roc_too_high(self, asset_symbol, provider_id, dates):
        from market.models import Logging
        log = Logging()

        log_level = 'info'
        context = self.get_context()
        msg = str('[%s] Rate of Change from provider \'%s\' are too high on periods: %s' % (asset_symbol,
                                                                                            provider_id,
                                                                                            dates))
        log.log_into_db(level=log_level, context=context, message=msg)

    def log_validation_result(self, asset_symbol, inconsistencies):
        from market.models import Logging
        log = Logging()

        if inconsistencies['amount'] == 0:
            log_level = 'info'
            msg = str('[%s] All inconsistencies were fixed by trusted data.' % asset_symbol)
        else:
            log_level = 'major'
            msg = str('[%s] The following inconsistencies were not able to be solved: %s' % (asset_symbol,
                                                                                             inconsistencies))

        context = self.get_context()
        log.log_into_db(level=log_level, context=context, message=msg)