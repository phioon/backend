from market.models import StockExchange, Asset


def updateStockExchangeData():
    se = StockExchange()
    se.update_stock_exchange_list()


def updateAssetData(se_short):
    stockExchanges = list(StockExchange.objects.values_list('se_short', flat=True).distinct())
    if se_short not in stockExchanges:
        return

    a = Asset()
    a.update_assets_by_stock_exchange(se_short=se_short)
