# https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=VALE3.SAO&outputsize=full&apikey=3YQ322UE0X66IU2R
# https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=VALE3.SAO&apikey=3YQ322UE0X66IU2R

import json
import requests
from ..functions import utils


class AlphaVantage:
    api_realtime = 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE'
    api_history_daily = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED'
    apiKey = '3YQ322UE0X66IU2R'

    def json_from_request(self, request):
        try:
            r = requests.get(request)
        except requests.exceptions.Timeout:
            r = requests.get(request)  # Try again
        except requests.exceptions.RequestException as ex:
            pass
            #log = Logging()
            #log.logIntoDb(log_level='ERROR', log_module='json_from_request', log_msg=ex.response)

        return json.loads(r.text)

    def json_realtime(self, symbol):
        symbol = self.convert_symbol(symbol)

        url = self.api_realtime
        url += '&symbol=' + symbol
        url += '&apikey=' + self.apiKey

        return self.json_from_request(url)

    def json_history_daily(self, symbol, outputsize='compact'):
        symbol = symbol[: symbol.index('.')]
        symbol += '.SAO'

        url = self.api_history_daily
        url += '&symbol=' + symbol
        url += '&outputsize=' + outputsize
        url += '&apikey=' + self.apiKey

        return self.json_from_request(url)

    # Function to convert non-AlphaVantage symbols, to AV symbols.
    def convert_symbol(self, symbol):
        se_short = symbol[symbol.index('.') + 1:]

        if se_short == 'BVMF':
            symbol = str(symbol).replace(se_short, 'SAO')

        return symbol

    def get_realtime_data(self, symbol):
        json = self.json_realtime(symbol)

        if not json['Global Quote']:
            return json['Global Quote']

        pct_change = round(float(json['Global Quote']['10. change percent'].replace('%', '')), 2)

        obj = {'symbol': symbol,
               'price': json['Global Quote']['05. price'],
               'pct_change': pct_change,
               'last_trade_time': json['Global Quote']['07. latest trading day']}

        return obj

    def get_history_daily(self, symbol, outputsize='compact'):
        list = []
        json = self.json_history_daily(symbol, outputsize)

        try:
            for k, v in json['Time Series (Daily)'].items():
                pct_adjustment = utils.division(float(v['5. adjusted close']),
                                                float(v['4. close']),
                                                decimals=5,
                                                if_denominator_is_zero=1)

                list.append({'datetime': str(k + ' 00:00:00'),
                             'symbol': symbol,
                             'open': float(v['1. open']) * pct_adjustment,
                             'high': float(v['2. high']) * pct_adjustment,
                             'low': float(v['3. low']) * pct_adjustment,
                             'close': float(v['5. adjusted close']),
                             'volume': v['6. volume']})
        except KeyError:
            list.append({'symbol': symbol,
                         'Message': json['Error Message']})

        if len(list) <= 1:
            raise Exception('Alpha Vantage: Empty List')
        return list
