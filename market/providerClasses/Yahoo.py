# Profile
#   Includes: real-time (regularMarketPrice), change_pct (regularMarketChangePercent)
#   . https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-profile?symbol=<apiKey>

import json
import requests


class Yahoo:
    api_stockExchanges = 'http://api.marketstack.com/v1/exchanges/<se_short>?access_key=<apiKey>&limit=<limit>'
    api_assets = 'http://api.marketstack.com/v1/exchanges/<se_short>/tickers?access_key=<apiKey>&limit=<limit>'
    api_eod = 'http://api.marketstack.com/v1/tickers/<asset_symbol>/eod?access_key=<apiKey>&limit=<limit>'
    api_realtime = 'http://api.marketstack.com/v1/intraday/latest?access_key=<apiKey>&exchange=<se_short>&limit=<limit>'

    api_key = '98e83dc6353ef87710b8b34e8197dedc'
    limit = '1000'

    def json_realtime(self, strSymbolList):
        url = self.urlRealtime
        url += 'symbol=' + strSymbolList
        url += '&api_token=' + self.api_key

        return self.json_from_request(url)

    def get_paginated_data(self, api, key_list=None):
        # key_list is the object key that has a list as value ({key_list: [{a: 1, b: 2}, {a: 11, b: 12}]}
        data = []

        json = self.json_from_request(api)
        if key_list:
            data.extend(json['data'][key_list])
        else:
            data.extend(json['data'])

        count = json['pagination']['count']
        total = json['pagination']['total']
        offset = json['pagination']['offset']

        if offset + count >= total:
            is_last_page = True
        else:
            is_last_page = False

        while not is_last_page:
            offset += count
            json = self.json_from_request(str(api + '&offset=' + str(offset)))

            if key_list:
                data.extend(json['data'][key_list])
            else:
                data.extend(json['data'])

            count = json['pagination']['count']
            if offset + count >= total:
                is_last_page = True
        return data

    def get_stock_exchange(self, se_short=None):
        # Get Stock Exchange details
        api = self.api_stockExchanges
        api = api.replace('<apiKey>', self.api_key)
        api = api.replace('<limit>', self.limit)

        if se_short:
            api = api.replace('<se_short>', se_short)
            data = self.json_from_request(api)
        else:
            api = api.replace('<se_short>', '')
            data = self.get_paginated_data(api)

        return data

    def get_assets_by_stock_exchange(self, se_short):
        # Get Stock Exchange details
        api = self.api_assets
        api = api.replace('<apiKey>', self.api_key)
        api = api.replace('<limit>', self.limit)
        api = api.replace('<se_short>', se_short)

        data = self.get_paginated_data(api, key_list='tickers')

        return data