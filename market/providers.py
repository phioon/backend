import json
import requests
import inspect
from market.functions import utils


# Utils
def request_get(request, headers={}):
    try:
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
class AlphaVantage:
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

    def get_eod_data(self, asset_symbol, outputsize='compact'):
        # Get EOD data
        result = {'status': None, 'data': None}
        converted_symbol = self.convert_symbol(asset_symbol)

        request = self.api_realtime
        request = request.replace('<api_key>', self.api_key)
        request = request.replace('<asset_symbol>', converted_symbol)
        request = request.replace('<outputsize>', outputsize)

        result['rdata'] = request_get_data(request)

        if result['data']['Time Series (Daily)']:
            # Symbol found
            result['status'] = 200
            for k, v in result['rdata']['Time Series (Daily)'].items():
                pct_adjustment = utils.division(float(v['5. adjusted close']),
                                                float(v['4. close']),
                                                decimals=5,
                                                if_denominator_is_zero=1)

                result['data'].append({'datetime': str(k + ' 00:00:00'),
                                       'symbol': asset_symbol,
                                       'open': float(v['1. open']) * pct_adjustment,
                                       'high': float(v['2. high']) * pct_adjustment,
                                       'low': float(v['3. low']) * pct_adjustment,
                                       'close': float(v['5. adjusted close']),
                                       'volume': v['6. volume']})
        else:
            # Symbol not found
            result['status'] = 404

        if len(list) <= 1:
            raise Exception('Alpha Vantage: Empty List')
        return result

    # prepares


class MarketStack:
    api_assets_by_stock_exchange = str('http://api.marketstack.com/v1/exchanges/<se_short>/tickers?'
                                       'access_key=<api_key>&'
                                       'limit=<limit>')
    api_eod = str('http://api.marketstack.com/v1/tickers/<asset_symbol>/eod?'
                  'access_key=<api_key>&'
                  'limit=<limit>')
    api_realtime = str('http://api.marketstack.com/v1/intraday/latest?'
                       'access_key=<api_key>&'
                       'exchange=<se_short>&'
                       'limit=<limit>')
    api_stock_exchanges = str('http://api.marketstack.com/v1/exchanges/<se_short>?'
                              'access_key=<api_key>&'
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
        if '+' in timestamp:
            timestamp = timestamp[: timestamp.rindex('+')]
        if 'T' in timestamp:
            timestamp = timestamp.replace('T', ' ')
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

    def get_assets_by_stock_exchange(self, se_short):
        # Get list of assets by a given Stock Exchange
        result = {'status': None, 'data': None}

        request = self.api_assets_by_stock_exchange
        request = request.replace('<api_key>', self.api_key)
        request = request.replace('<limit>', self.limit)
        request = request.replace('<se_short>', se_short)

        result['rdata'] = self.get_paginated_data(request, data_key='tickers')

        if len(result['rdata']) == 0:
            result['status'] = 404
        else:
            result['status'] = 200
            result['data'] = self.prepare_assets_by_stock_exchange(se_short, result['rdata'])

        return result

    def get_eod_data(self, asset_symbol, last_x_rows):
        # Get EOD data
        result = {'status': None, 'data': None}

        request = self.api_eod
        request = request.replace('<asset_symbol>', asset_symbol)
        request = request.replace('<api_key>', self.api_key)

        if last_x_rows == 0 or last_x_rows > int(self.limit):
            # Limit is set to max value supported.
            request = request.replace('<limit>', self.limit)
            result['rdata'] = self.get_paginated_data(request, data_key='eod')

            if len(result['rdata']) == 0:
                result['status'] = 404
            else:
                result['status'] = 200
                result['data'] = self.prepare_eod_data(asset_symbol, result['rdata'])
        else:
            # Limit is set as last_x_rows
            request = request.replace('<limit>', str(last_x_rows))
            result['rdata'] = request_get_data(request)

            if 'error' in result['rdata']:
                result['status'] = 404
            else:
                result['status'] = 200
                result['data'] = self.prepare_eod_data(asset_symbol, result['rdata']['data']['eod'])

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
    def prepare_assets_by_stock_exchange(self, se_short, rdata):
        # Prepares data to be recognized as table's fields.
        data = []
        for obj in rdata:
            asset_symbol = obj['symbol']

            has_eod = bool(obj['has_eod'])
            is_factionary_market = self.is_fractionary_market(se_short, asset_symbol)
            if not is_factionary_market and has_eod:
                data.append({'asset_symbol': self.get_asset_symbol(asset_symbol)})

        return data

    def prepare_eod_data(self, asset_symbol, rdata):
        # Prepares data to be recognized as table's fields.
        data = []

        for obj in rdata:
            adj_pct = utils.division(float(obj['adj_close']),
                                     float(obj['close']),
                                     decimals=5,
                                     if_denominator_is_zero=1)

            data.append({'asset_symbol': asset_symbol,
                         'datetime': self.get_date_isoformat(obj['date']),
                         'open': round(float(obj['open']) * adj_pct, 2),
                         'high': round(float(obj['high']) * adj_pct, 2),
                         'low': round(float(obj['low']) * adj_pct, 2),
                         'close': round(float(obj['adj_close']), 2),
                         'volume': int(obj['volume'])})

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


class Yahoo:
    api_profile = str('https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-profile?'
                      'symbol=<asset_symbol>')
    api_realtime = str('https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-profile?'
                       'symbol=<asset_symbol>')
    api_key = '60d22cc6a5msh3e9ce925473ad87p1f91f1jsn3dfaee312de6'
    limit = '1000'

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

    def get_sector_id(self, sector_name):
        sector_id = str(sector_name).lower()
        sector_id = sector_id.replace(' ', '_')
        return sector_id

    def get_pct_change(self, pct_change):
        pct_change = pct_change * 100
        return round(pct_change, 2)

    # services
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
