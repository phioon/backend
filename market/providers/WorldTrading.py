# https://api.worldtradingdata.com/api/v1/history?symbol=FRAS3.SA&api_token=ycjOzOP5loHPPIbfMW6tA7AreqAlq0z4yqxStxk2B8Iwges581rK5V8kIgg4
# https://api.worldtradingdata.com/api/v1/stock?symbol=ITUB4.SA,AALR3.SA&api_token=ycjOzOP5loHPPIbfMW6tA7AreqAlq0z4yqxStxk2B8Iwges581rK5V8kIgg4

import json
import requests


class WorldTrading:

    urlRealtime = 'https://api.worldtradingdata.com/api/v1/stock?'
    urlHistoryD = 'https://api.worldtradingdata.com/api/v1/history?'
    urlSearch = 'https://api.worldtradingdata.com/api/v1/stock_search?'
    apiKey = 'ycjOzOP5loHPPIbfMW6tA7AreqAlq0z4yqxStxk2B8Iwges581rK5V8kIgg4'

    def jsonFromRequest(self, request):
        try:
            r = requests.get(request)
        except requests.exceptions.Timeout:
            r = requests.get(request)  # Try again
        except requests.exceptions.RequestException as ex:
            pass
            #log = Logging()
            #log.logIntoDb(log_level='ERROR', log_module='json_from_request', log_msg=ex.response)

        return json.loads(r.text)

    def jsonRealTimePrice(self, strSymbolList):
        url = self.urlRealtime
        url += 'symbol=' + strSymbolList
        url += '&api_token=' + self.apiKey

        return self.jsonFromRequest(url)

    def jsonPriceHistoryFromTo_D(self, symbol, dateFrom, dateTo):
        url = self.urlHistoryD
        url += '&symbol=' + symbol
        url += '&date_from=' + dateFrom
        url += '&date_to=' + dateTo
        url += '&api_token=' + self.apiKey

        return self.jsonFromRequest(url)

    def listAssetsByStockExchange(self, stockExchange):
        # Run once a month. It consumes (1 * total_pages) requests
        list = []

        url = self.urlSearch
        url += 'stock_exchange=' + stockExchange
        url += '&api_token=' + self.apiKey

        json = self.jsonFromRequest(url)

        page = 1
        isLastPage = False

        while not isLastPage:
            url += '&page=' + str(page)
            json = self.jsonFromRequest(url)

            cPage = json['total_pages']
            cReturned = json['total_returned']

            for x in range(cReturned):
                if not (str(json['data'][x]['name']).__contains__('N/AlphaVantage.py') or
                        str(json['data'][x]['price']).__contains__('0.00')):

                    if json['data'][x]['stock_exchange_short'] == 'SAO':
                        json['data'][x]['symbol'] = json['data'][x]['symbol'].replace('.SA', '.SAO')

                    list.append(json['data'][x])

            if page == cPage:
                isLastPage = True
            else:
                page += 1

        return list

    def listRealtimePrice(self, symbolList):
        list = []
        strSymbolList = ''

        # Block to define what is the current limit of SYMBOLS_RETURNED
        for x in range(len(symbolList)):
            strSymbolList += symbolList[x] + ','
        strSymbolList = strSymbolList[:-1]  # Removes last comma

        json = self.jsonRealTimePrice(strSymbolList)

        try:
            reqLimit = json['symbols_returned']
        except KeyError:
            reqLimit = len(json['data'])
        # ---------------------

        strSymbolList = ''
        nextStop = reqLimit - 1

        for x in range(len(symbolList)):
            strSymbolList += symbolList[x] + ','

            if x == nextStop or x == len(symbolList) - 1:
                strSymbolList = strSymbolList[:-1]  # Removes last comma
                json = self.jsonRealTimePrice(strSymbolList)

                for y in range(len(json['data'])):
                    list.append({'symbol': json['data'][y]['symbol'],
                                 'price': json['data'][y]['price'],
                                 'last_trade_time': json['data'][y]['last_trade_time']})

                nextStop += reqLimit
                strSymbolList = ''

        return list

    def listHistoryFromTo_D(self, symbol, dateFrom, dateTo):
        list = []
        json = self.jsonPriceHistoryFromTo_D(symbol, dateFrom, dateTo)
        try:
            for k, v in json['history'].items():
                list.append({'datetime': str(k + ' 00:00:00'),
                             'symbol': symbol,
                             'open': v['open'],
                             'high': v['high'],
                             'low': v['low'],
                             'close': v['close'],
                             'volume': v['volume']})
        except KeyError:
            list.append({'symbol': symbol,
                         'Message': json['Message']})
        return list
