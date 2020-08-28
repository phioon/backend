import json
import requests
import inspect
from django_engine import settings
from market.functions import utils


# Utils
def request_get(request, headers={}):
    try:
        result = requests.get(request, headers=headers)

        if result.status_code in [500, 503]:
            # Try again... Yahoo doesn't have a very good availability (2020-07-25)
            result = requests.get(request, headers=headers)

    except requests.exceptions.Timeout:
        # Try again
        result = requests.get(request)

    return result


def request_get_data(request, headers={}):
    result = request_get(request, headers)
    json_data = {}

    try:
        json_data = json.loads(result.text)
    except json.JSONDecodeError as ex:
        from market.models import Logging
        log = Logging()

        log_level = 'warning'
        context = 'providers.request_get_data'
        msg = str('The following HTTP response could not be parsed to json format: \'%s\'' % ex.doc)
        log.log_into_db(level=log_level, context=context, message=msg)
    return json_data


# Provider Classes
class Phioon:
    id = 'phioon'

    api_stock_exchanges = str(settings.PROVIDER_API_BASE + 'exchanges/<se_short>?'
                              'api_key=<api_key>')
    api_tickers_by_stock_exchange = str(settings.PROVIDER_API_BASE + 'exchanges/<se_short>/tickers/?'
                                                                     'api_key=<api_key>')

    api_eod = str(settings.PROVIDER_API_BASE + 'tickers/<asset_symbol>/eod/?'
                                               'limit=<limit>&'
                                               'api_key=<api_key>')
    api_profile = str(settings.PROVIDER_API_BASE + 'tickers/<asset_symbol>/profile/?'
                                                   'api_key=<api_key>')
    api_realtime = str(settings.PROVIDER_API_BASE + 'tickers/<asset_symbol>/realtime/?'
                                                    'api_key=<api_key>')

    api_key = settings.API_KEY

    # utils
    def get_context(self):
        class_name = self.__class__.__name__
        caller_name = inspect.stack()[1].function
        return str('%s.%s' % (class_name, caller_name))

    def convert_symbol(self, asset_symbol):
        # Once Phioon is the provider, converting is not needed.
        # Function is here just to keep a pattern. Maybe that's not needed, idk...
        return asset_symbol

    def get_asset_label(self, asset_symbol):
        asset_label = asset_symbol
        if '.' in asset_symbol:
            asset_label = asset_symbol[:asset_symbol.rindex('.')]
        return asset_label

    def get_sector_id(self, sector_name):
        sector_id = str(sector_name).lower()
        sector_id = sector_id.replace(' ', '_')
        return sector_id

    # services
    def get_stock_exchange_list(self):
        # Get details for a specific Stock Exchange
        result = {'status': None, 'data': None}

        request = self.api_stock_exchanges
        request = request.replace('<se_short>', '')
        request = request.replace('<api_key>', self.api_key)

        result['rdata'] = request_get_data(request)

        if 'error' in result['rdata']:
            result['status'] = 404
        else:
            result['status'] = 200
            result['data'] = self.prepare_stock_exchange_list(result['rdata']['data'])

        return result

    def get_stock_exchange_data(self, se_short):
        # Get details for a specific Stock Exchange
        result = {'status': None, 'data': None}

        request = self.api_stock_exchanges
        request = request.replace('<se_short>', se_short)
        request = request.replace('<api_key>', self.api_key)

        result['rdata'] = request_get_data(request)

        if 'error' in result['rdata']:
            result['status'] = 404
        else:
            result['status'] = 200
            result['data'] = self.prepare_stock_exchange_data(result['rdata']['data'])

        return result

    def get_tickers_by_stock_exchange(self, se_short):
        # Get details for a specific Stock Exchange
        result = {'status': None, 'data': None}

        request = self.api_tickers_by_stock_exchange
        request = request.replace('<se_short>', se_short)
        request = request.replace('<api_key>', self.api_key)

        result['rdata'] = request_get_data(request)

        if 'error' in result['rdata']:
            result['status'] = 404
        else:
            result['status'] = 200
            result['data'] = self.prepare_tickers_by_stock_exchange(result['rdata']['data']['tickers'])

        return result

    def get_eod_data(self, asset_symbol, last_x_periods):
        # Get EOD data
        result = {'status': None, 'data': None}
        converted_symbol = self.convert_symbol(asset_symbol)

        request = self.api_eod
        request = request.replace('<asset_symbol>', converted_symbol)
        request = request.replace('<api_key>', self.api_key)

        request = request.replace('<limit>', str(last_x_periods))
        result['rdata'] = request_get_data(request)

        if 'message' in result['rdata'] or len(result['rdata']) == 0:
            result['status'] = 404
        else:
            result['status'] = 200
            result['data'] = self.prepare_eod_data(result['rdata']['data']['eod'])

        return result

    def get_profile_data(self, asset_symbol):
        # Get profile data
        result = {'status': None, 'data': None}
        converted_symbol = self.convert_symbol(asset_symbol)

        request = self.api_profile
        request = request.replace('<asset_symbol>', converted_symbol)
        request = request.replace('<api_key>', self.api_key)

        result['rdata'] = request_get_data(request)

        if len(result['rdata']) == 0:
            result['status'] = 404
        else:
            result['status'] = 200
            result['data'] = self.prepare_profile_data(asset_symbol, result['rdata']['data'])

        return result

    def get_realtime_data(self, asset_symbol):
        # Get real-time data
        # Get profile data
        result = {'status': None, 'data': None}
        converted_symbol = self.convert_symbol(asset_symbol)

        request = self.api_realtime
        request = request.replace('<asset_symbol>', converted_symbol)
        request = request.replace('<api_key>', self.api_key)

        result['rdata'] = request_get_data(request)

        if len(result['rdata']) == 0:
            result['status'] = 404
        else:
            result['status'] = 200
            result['data'] = self.prepare_realtime_data(asset_symbol, result['rdata']['data'])

        return result

    # prepares
    def prepare_stock_exchange_list(self, rdata):
        # Prepares data to be recognized as table's fields.
        data = []
        for obj in rdata:
            data.append({
                'se_short': str(obj['symbol']),
                'se_name': str(obj['name']),
                'country_code': str(obj['country_code']),
                'currency_code': str(obj['currency_code']),
                'se_timezone': str(obj['timezone']),
                'se_startTime': str(obj['market_start_time']),
                'se_endTime': str(obj['market_end_time']),
                'website': str(obj['website'])
            })

        return data

    def prepare_stock_exchange_data(self, rdata):
        # Prepares data to be recognized as table's fields.
        data = {
            'se_short': str(rdata['symbol']),
            'se_name': str(rdata['name']),
            'country_code': str(rdata['country_code']),
            'currency_code': str(rdata['currency_code']),
            'se_timezone': str(rdata['timezone']),
            'se_startTime': str(rdata['market_start_time']),
            'se_endTime': str(rdata['market_end_time']),
            'website': str(rdata['website'])
        }

        return data

    def prepare_tickers_by_stock_exchange(self, rdata):
        # Prepares data to be recognized as table's fields.
        data = []
        for obj in rdata:
            asset_symbol = obj['symbol']
            data.append({'asset_symbol': asset_symbol})

        return data

    def prepare_eod_data(self, rdata):
        # Prepares data to be recognized as table's fields.
        data = []

        for obj in rdata:
            adj_pct = 1  # default value

            if obj['adj_close'] and obj['close']:
                adj_pct = utils.division(float(obj['adj_close']),
                                         float(obj['close']),
                                         decimals=5,
                                         if_denominator_is_zero=1)

            data.append({'datetime': str(obj['date']),
                         'adj_pct': adj_pct,
                         'open': obj['open'],
                         'high': obj['high'],
                         'low': obj['low'],
                         'close': obj['adj_close'],
                         'volume': obj['volume']})

        return data

    def prepare_profile_data(self, asset_symbol, rdata):
        # Prepares data to be recognized as table's fields.
        data = {
            'asset_symbol': asset_symbol,
            'asset_label': self.get_asset_label(asset_symbol),
            'asset_name': str(rdata['asset_name']),
            'country_code': str(rdata['country_code']),
            'sector_id': self.get_sector_id(rdata['sector_name']),
            'sector_name': str(rdata['sector_name']),
            'website': str(rdata['website']),
            'business_summary': str(rdata['business_summary'])
        }

        return data

    def prepare_realtime_data(self, asset_symbol, rdata):
        # Prepares data to be recognized as table's fields.
        data = {
            'asset_symbol': asset_symbol,
            'last_trade_time': str(rdata['last_trade_time']),
            'open': float(rdata['open']),
            'high': float(rdata['high']),
            'low': float(rdata['low']),
            'price': float(rdata['price']),
            'volume': float(rdata['volume']),
            'pct_change': float(rdata['pct_change_day'])
        }

        return data


class AlphaVantage:
    id = 'alpha_vantage'
    # https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=VALE3.SAO&outputsize=full&apikey=3YQ322UE0X66IU2R
    # https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=VALE3.SAO&apikey=3YQ322UE0X66IU2R

    api_eod = str('https://www.alphavantage.co/query?'
                  'function=TIME_SERIES_DAILY_ADJUSTED&'
                  'apikey=<api_key>&'
                  'symbol=<asset_symbol>&'
                  'outputsize=<outputsize>')
    api_realtime = str('https://www.alphavantage.co/query?'
                       'function=GLOBAL_QUOTE&'
                       'apikey=<api_key>&'
                       'symbol=<asset_symbol>')

    api_key = '3YQ322UE0X66IU2R'

    # utils
    def convert_symbol(self, asset_symbol):
        # Replaces se_short in asset_symbol to a given se_short (ex: from 'VALE3.BVMF' to 'VALE3.SAO')
        # If 'BVMF' suffix is not recognized by this provider, it's converted to a recognized one.
        converted_symbol = asset_symbol
        se_short_map = {
            'BVMF': 'SAO',
            'SAO': 'SAO',
            'SA': 'SAO'
        }

        if '.' in asset_symbol:
            se_short = asset_symbol[asset_symbol.index('.') + 1:]

            if se_short in se_short_map:
                converted_symbol = str(asset_symbol).replace(se_short, se_short_map[se_short])
            else:
                from market.models import Logging
                log = Logging()

                log_level = 'warning'
                context = self.get_context()
                msg = str('\'se_short_map\' does not have \'%s\' mapped' % se_short)
                log.log_into_db(level=log_level, context=context, message=msg)

        return converted_symbol

    def get_context(self):
        class_name = self.__class__.__name__
        caller_name = inspect.stack()[1].function
        return str('%s.%s' % (class_name, caller_name))

    def get_date_isoformat(self, timestamp):
        timestamp = str(timestamp)
        timestamp += ' 00:00:00'

        return timestamp

    # services
    def get_realtime_data(self, asset_symbol):
        # Get real-time data
        result = {'status': None, 'data': None}
        converted_symbol = self.convert_symbol(asset_symbol)

        request = self.api_realtime
        request = request.replace('<api_key>', self.api_key)
        request = request.replace('<asset_symbol>', converted_symbol)

        result['rdata'] = request_get_data(request)
        result['data'] = None

        if result['rdata']['Global Quote']:
            # Symbol found
            result['status'] = 200
            result['rdata']['Global Quote']['10. change percent'] = result['rdata']['Global Quote'][
                '10. change percent'].replace('%', '')
            pct_change = round(float(result['rdata']['Global Quote']['10. change percent']), 2)
            obj = {'symbol': asset_symbol,
                   'price': result['rdata']['Global Quote']['05. price'],
                   'pct_change': pct_change,
                   'last_trade_time': result['rdata']['Global Quote']['07. latest trading day']}

            result['data'] = obj
        else:
            # Symbol not found
            result['status'] = 404

        return result

    def get_eod_data(self, asset_symbol, last_x_periods):
        # Get EOD data
        result = {'status': None, 'data': None}
        converted_symbol = self.convert_symbol(asset_symbol)

        request = self.api_eod
        request = request.replace('<api_key>', self.api_key)
        request = request.replace('<asset_symbol>', converted_symbol)

        if last_x_periods == 0 or last_x_periods > 100:
            request = request.replace('<outputsize>', 'full')
        else:
            request = request.replace('<outputsize>', 'compact')

        result['rdata'] = request_get_data(request)

        if 'Time Series (Daily)' in result['rdata'] and len(result['rdata']['Time Series (Daily)']) > 0:
            result['status'] = 200
            result['data'] = self.prepare_eod_data(result['rdata'])
        else:
            result['status'] = 404

        return result

    # prepares
    def prepare_eod_data(self, rdata):
        # Prepares data to be recognized as table's fields.
        data = []

        for k, v in rdata['Time Series (Daily)'].items():
            adj_pct = 1     # default value

            if v['5. adjusted close'] and v['4. close']:
                adj_pct = utils.division(float(v['5. adjusted close']),
                                         float(v['4. close']),
                                         decimals=5,
                                         if_denominator_is_zero=1)

            data.append({'datetime': self.get_date_isoformat(k),
                         'adj_pct': adj_pct,
                         'open': v['1. open'],
                         'high': v['2. high'],
                         'low': v['3. low'],
                         'close': v['5. adjusted close'],
                         'volume': v['6. volume']
            })

        return data


class MarketStack:
    id = 'market_stack'
    api_stock_exchanges = str('http://api.marketstack.com/v1/exchanges/<se_short>?'
                              'access_key=<api_key>&'
                              'limit=<limit>')
    api_tickers_by_stock_exchange = str('http://api.marketstack.com/v1/exchanges/<se_short>/tickers?'
                                        'access_key=<api_key>&'
                                        'limit=<limit>')
    api_eod = str('http://api.marketstack.com/v1/tickers/<asset_symbol>/eod?'

                  'access_key=<api_key>&'
                  'limit=<limit>')
    api_realtime = str('http://api.marketstack.com/v1/intraday/latest?'
                       'access_key=<api_key>&'
                       'exchange=<se_short>&'
                       'limit=<limit>')

    api_key = '98e83dc6353ef87710b8b34e8197dedc'
    limit = '1000'

    # utils
    def get_context(self):
        class_name = self.__class__.__name__
        caller_name = inspect.stack()[1].function
        return str('%s.%s' % (class_name, caller_name))

    def convert_symbol(self, asset_symbol):
        # Replaces se_short in asset_symbol to a given se_short (ex: from 'VALE3.BVMF' to 'VALE3.SAO')
        # If 'BVMF' suffix is not recognized by this provider, it's converted to a recognized one.
        converted_symbol = asset_symbol
        se_short_map = {
            'SAO': 'BVMF',
            'SA': 'BVMF',
            'BVMF': 'BVMF'
        }

        if '.' in asset_symbol:
            se_short = asset_symbol[asset_symbol.index('.') + 1:]

            if se_short in se_short_map:
                converted_symbol = str(asset_symbol).replace(se_short, se_short_map[se_short])
            else:
                from market.models import Logging
                log = Logging()

                log_level = 'warning'
                context = self.get_context()
                msg = str('\'se_short_map\' does not have \'%s\' mapped' % se_short)
                log.log_into_db(level=log_level, context=context, message=msg)

        return converted_symbol

    def get_asset_symbol(self, asset_symbol):
        asset_symbol = str(asset_symbol).upper()
        return asset_symbol

    def get_date_isoformat(self, timestamp):
        timestamp = str(timestamp)
        if 'T' in timestamp:
            timestamp = timestamp[: timestamp.index('T')]
        else:
            timestamp = timestamp[: 10]

        timestamp += ' 00:00:00'
        return timestamp

    def get_se_short(self, se_short):
        se_short = str(se_short).upper()
        return se_short

    def get_se_name(self, se_name):
        se_name = utils.remove_special_chars(se_name)
        se_name = se_name.title()
        return se_name

    def is_fractionary_market(self, se_short, asset_symbol):
        if se_short in ['BVMF']:
            # Brazilian Fractionary Market
            if asset_symbol.endswith(str('F.' + se_short)):
                return True

        return False

    # services
    def get_paginated_data(self, request, data_key=None):
        # data_key is the key where data requested is hold under ({data_key: <data requested>}
        data = []

        result = request_get_data(request)
        if result['data']:
            if data_key:
                data.extend(result['data'][data_key])
            else:
                data.extend(result['data'])
        else:
            return data

        count = result['pagination']['count']
        total = result['pagination']['total']
        offset = result['pagination']['offset']

        if offset + count >= total:
            is_last_page = True
        else:
            is_last_page = False

        while not is_last_page:
            offset += count
            result = request_get_data(str(request + '&offset=' + str(offset)))

            if data_key:
                data.extend(result['data'][data_key])
            else:
                data.extend(result['data'])

            count = result['pagination']['count']
            if offset + count >= total:
                is_last_page = True
        return data

    def get_tickers_by_stock_exchange(self, se_short):
        # Get list of assets by a given Stock Exchange
        result = {'status': None, 'data': None}

        request = self.api_tickers_by_stock_exchange
        request = request.replace('<api_key>', self.api_key)
        request = request.replace('<limit>', self.limit)
        request = request.replace('<se_short>', se_short)

        result['rdata'] = self.get_paginated_data(request, data_key='tickers')

        if len(result['rdata']) == 0:
            result['status'] = 404
        else:
            result['status'] = 200
            result['data'] = self.prepare_tickers_by_stock_exchange(se_short, result['rdata'])

        return result

    def get_eod_data(self, asset_symbol, last_x_periods):
        # Get EOD data
        result = {'status': None, 'data': None}
        converted_symbol = self.convert_symbol(asset_symbol)

        request = self.api_eod
        request = request.replace('<asset_symbol>', converted_symbol)
        request = request.replace('<api_key>', self.api_key)

        if last_x_periods == 0 or last_x_periods > int(self.limit):
            # Limit is set to max value supported.
            request = request.replace('<limit>', self.limit)
            result['rdata'] = self.get_paginated_data(request, data_key='eod')

            if len(result['rdata']) == 0:
                result['status'] = 404
            else:
                result['status'] = 200
                result['data'] = self.prepare_eod_data(result['rdata'])
        else:
            # Limit is set as last_x_rows
            request = request.replace('<limit>', str(last_x_periods))
            result['rdata'] = request_get_data(request)

            if 'error' in result['rdata'] or len(result['rdata']) == 0:
                result['status'] = 404
            else:
                result['status'] = 200
                result['data'] = self.prepare_eod_data(result['rdata']['data']['eod'])

        return result

    def get_stock_exchange_data(self, se_short):
        # Get details for a specific Stock Exchange
        result = {'status': None, 'data': None}

        request = self.api_stock_exchanges
        request = request.replace('<se_short>', se_short)
        request = request.replace('<api_key>', self.api_key)
        request = request.replace('<limit>', self.limit)

        result['rdata'] = request_get_data(request)

        if 'error' in result['rdata']:
            result['status'] = 404
        else:
            result['status'] = 200
            result['data'] = self.prepare_stock_exchange_data(result['rdata'])

        return result

    def get_stock_exchange_list(self):
        # Get details for all Stock Exchanges supported by this provider
        result = {'status': None, 'data': None}

        request = self.api_stock_exchanges
        request = request.replace('<se_short>', '')
        request = request.replace('<api_key>', self.api_key)
        request = request.replace('<limit>', self.limit)

        result['rdata'] = self.get_paginated_data(request)

        if len(result['rdata']) == 0:
            result['status'] = 404
        else:
            result['status'] = 200
            result['data'] = self.prepare_stock_exchange_list(result['rdata'])

        return result

    # prepares
    def prepare_stock_exchange_list(self, rdata):
        # Prepares data to be recognized as table's fields.
        data = []
        for obj in rdata:
            data.append({
                'se_short': self.get_se_short(obj['mic']),
                'se_name': self.get_se_name(obj['name']),
                'se_timezone': str(obj['timezone']['timezone']),
                'country_code': str(obj['country_code']),
                'currency_code': str(obj['currency']['code']),
                'website': str(obj['website']),
            })

        return data

    def prepare_stock_exchange_data(self, rdata):
        # Prepares data to be recognized as table's fields.
        data = {
            'se_short': self.get_se_short(rdata['mic']),
            'se_name': self.get_se_name(rdata['name']),
            'se_timezone': str(rdata['timezone']['timezone']),
            'country_code': str(rdata['country_code']),
            'currency_code': str(rdata['currency']['code']),
            'website': str(rdata['website']),
        }

        return data

    def prepare_tickers_by_stock_exchange(self, se_short, rdata):
        # Prepares data to be recognized as table's fields.
        data = []
        for obj in rdata:
            asset_symbol = obj['symbol']

            has_eod = bool(obj['has_eod'])
            is_factionary_market = self.is_fractionary_market(se_short, asset_symbol)
            if not is_factionary_market and has_eod:
                data.append({'asset_symbol': self.get_asset_symbol(asset_symbol)})

        return data

    def prepare_eod_data(self, rdata):
        # Prepares data to be recognized as table's fields.
        data = []

        for obj in rdata:
            adj_pct = 1  # default value

            if obj['adj_close'] and obj['close']:
                adj_pct = utils.division(float(obj['adj_close']),
                                         float(obj['close']),
                                         decimals=5,
                                         if_denominator_is_zero=1)

            data.append({'datetime': self.get_date_isoformat(obj['date']),
                         'adj_pct': adj_pct,
                         'open': obj['open'],
                         'high': obj['high'],
                         'low': obj['low'],
                         'close': obj['adj_close'],
                         'volume': obj['volume']})

        return data


class Yahoo:
    id = 'yahoo'
    api_profile = str('https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-profile?'
                      'symbol=<asset_symbol>')
    api_realtime = str('https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-profile?'
                       'symbol=<asset_symbol>')
    api_eod = str('https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-chart?'
                  'symbol=<asset_symbol>&'
                  'interval=<interval>&'
                  'range=<range>')
    api_key = '60d22cc6a5msh3e9ce925473ad87p1f91f1jsn3dfaee312de6'

    # utils
    def convert_symbol(self, asset_symbol):
        # Replaces se_short in asset_symbol to a given se_short (ex: from 'VALE3.BVMF' to 'VALE3.SAO')
        # If 'BVMF' suffix is not recognized by this provider, it's converted to a recognized one.
        converted_symbol = asset_symbol
        se_short_map = {
            'BVMF': 'SA',
            'SAO': 'SA',
            'SA': 'SA'
        }

        if '.' in asset_symbol:
            se_short = asset_symbol[asset_symbol.index('.') + 1:]

            if se_short in se_short_map:
                converted_symbol = str(asset_symbol).replace(se_short, se_short_map[se_short])
            else:
                from market.models import Logging
                log = Logging()

                log_level = 'warning'
                context = self.get_context()
                msg = str('\'se_short_map\' does not have \'%s\' mapped' % se_short)
                log.log_into_db(level=log_level, context=context, message=msg)

        return converted_symbol

    def get_context(self):
        class_name = self.__class__.__name__
        caller_name = inspect.stack()[1].function
        return str('%s.%s' % (class_name, caller_name))

    def get_asset_label(self, asset_symbol):
        asset_label = asset_symbol
        if '.' in asset_symbol:
            asset_label = asset_symbol[:asset_symbol.rindex('.')]
        return asset_label

    def get_country_code(self, country_name):
        country_code = None
        country_code_map = {
            'brazil': 'BR',
            'canada': 'CA',
            'united states': 'US'
        }
        country_name = str(country_name).lower()

        if country_name in country_code_map:
            country_code = country_code_map[country_name]
        else:
            from market.models import Logging
            log = Logging()

            log_level = 'warning'
            context = self.get_context()
            msg = str('\'country_code_map\' does not have \'%s\' mapped' % country_name)
            log.log_into_db(level=log_level, context=context, message=msg)

        return country_code

    def get_date_isoformat(self, timestamp):
        timestamp = str(timestamp)
        if 'T' in timestamp:
            timestamp = timestamp[: timestamp.index('T')]
        else:
            timestamp = timestamp[: 10]

        timestamp += ' 00:00:00'
        return timestamp

    def get_sector_id(self, sector_name):
        sector_id = str(sector_name).lower()
        sector_id = sector_id.replace(' ', '_')
        return sector_id

    def get_pct_change(self, pct_change):
        pct_change = pct_change * 100
        return round(pct_change, 2)

    # services
    def get_eod_data(self, asset_symbol, last_x_periods):
        # Get EOD data
        result = {'status': None, 'data': None}
        converted_symbol = self.convert_symbol(asset_symbol)

        headers = {'X-RapidAPI-Key': self.api_key}
        request = self.api_eod
        request = request.replace('<asset_symbol>', converted_symbol)
        request = request.replace('<interval>', '1d')

        if last_x_periods == 0 or last_x_periods > 250:
            request = request.replace('<range>', '10y')
        elif last_x_periods <= 5:
            request = request.replace('<range>', '5d')
        elif last_x_periods <= 20:
            request = request.replace('<range>', '1mo')
        elif last_x_periods <= 250:
            request = request.replace('<range>', '1y')

        result['rdata'] = request_get_data(request, headers)

        if 'chart' in result['rdata'] and \
                'result' in result['rdata']['chart'] and \
                len(result['rdata']['chart']['result']) > 0:
            result['status'] = 200
            result['data'] = self.prepare_eod_data(result['rdata']['chart']['result'][0])
        else:
            result['status'] = 404

        return result

    def get_profile_data(self, asset_symbol):
        # Get profile data
        result = {'status': None, 'data': None}
        converted_symbol = self.convert_symbol(asset_symbol)

        headers = {'X-RapidAPI-Key': self.api_key}
        request = self.api_profile
        request = request.replace('<asset_symbol>', converted_symbol)

        result['rdata'] = request_get_data(request, headers)

        if len(result['rdata']) == 0:
            result['status'] = 404
        else:
            result['status'] = 200
            result['data'] = self.prepare_profile_data(asset_symbol, result['rdata'])

        return result

    def get_realtime_data(self, asset_symbol):
        # Get real-time data
        # Get profile data
        result = {'status': None, 'data': None}
        converted_symbol = self.convert_symbol(asset_symbol)

        headers = {'X-RapidAPI-Key': self.api_key}
        request = self.api_realtime
        request = request.replace('<asset_symbol>', converted_symbol)

        result['rdata'] = request_get_data(request, headers)

        if len(result['rdata']) == 0:
            result['status'] = 404
        else:
            result['status'] = 200
            result['data'] = self.prepare_realtime_data(asset_symbol, result['rdata'])

        return result

    # prepares
    def prepare_eod_data(self, rdata):
        # Prepares data to be recognized as table's fields.
        data = []

        if 'timestamp' in rdata:
            for x in range(len(rdata['timestamp'])):
                adj_pct = 1         # default value

                datetime = utils.convert_epoch_timestamp(rdata['timestamp'][x])
                datetime = self.get_date_isoformat(datetime)
                open = rdata['indicators']['quote'][0]['open'][x]
                high = rdata['indicators']['quote'][0]['high'][x]
                low = rdata['indicators']['quote'][0]['low'][x]
                close = rdata['indicators']['quote'][0]['close'][x]
                adj_close = rdata['indicators']['adjclose'][0]['adjclose'][x]
                volume = rdata['indicators']['quote'][0]['volume'][x]

                if adj_close and close:
                    adj_pct = utils.division(float(adj_close),
                                             float(close),
                                             decimals=5,
                                             if_denominator_is_zero=1)

                data.append({'datetime': self.get_date_isoformat(datetime),
                             'adj_pct': adj_pct,
                             'open': open,
                             'high': high,
                             'low': low,
                             'close': adj_close,
                             'volume': volume})

        return data

    def prepare_profile_data(self, asset_symbol, rdata):
        # Prepares data to be recognized as table's fields.
        data = {
            'asset_symbol': asset_symbol,
            'asset_label': self.get_asset_label(asset_symbol),
            'asset_name': None,
            'country_code': None,
            'sector_id': None,
            'sector_name': None,
            'website': None,
            'business_summary': None
        }

        # asset_name
        if 'longName' in rdata['quoteType']:
            data['asset_name'] = str(rdata['quoteType']['longName'])
        else:
            data['asset_name'] = str(rdata['quoteType']['shortName'])
        # country_code
        if 'assetProfile' in rdata and 'country' in rdata['assetProfile']:
            data['country_code'] = self.get_country_code(rdata['assetProfile']['country'])
        # sector
        if 'assetProfile' in rdata and 'sector' in rdata['assetProfile']:
            data['sector_id'] = self.get_sector_id(rdata['assetProfile']['sector'])
            data['sector_name'] = str(rdata['assetProfile']['sector'])
        # website
        if 'assetProfile' in rdata and 'website' in rdata['assetProfile']:
            data['website'] = str(rdata['assetProfile']['website'])
        # business_summary
        if 'assetProfile' in rdata and 'longBusinessSummary' in rdata['assetProfile']:
            data['business_summary'] = str(rdata['assetProfile']['longBusinessSummary'])

        return data

    def prepare_realtime_data(self, asset_symbol, rdata):
        # Prepares data to be recognized as table's fields.
        data = {
            'asset_symbol': asset_symbol,
            'last_trade_time': utils.convert_epoch_timestamp(rdata['price']['regularMarketTime']),
            'open': float(rdata['price']['regularMarketOpen']['raw']),
            'high': float(rdata['price']['regularMarketDayHigh']['raw']),
            'low': float(rdata['price']['regularMarketDayLow']['raw']),
            'price': float(rdata['price']['regularMarketPrice']['raw']),
            'volume': float(rdata['price']['regularMarketVolume']['raw']),
            'pct_change': self.get_pct_change(rdata['price']['regularMarketChangePercent']['raw'])
        }

        return data
