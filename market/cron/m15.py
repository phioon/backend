from market.models import StockExchange, Asset
from datetime import datetime, timedelta


def updatePrices(se_short):
    stockExchanges = list(StockExchange.objects.values_list('se_short', flat=True).distinct())
    if se_short not in stockExchanges:
        return

    a = Asset()
    today = datetime.today().date()
    a_month_ago = today - timedelta(days=30)

    assets = Asset.objects.filter(last_access_time__gte=a_month_ago)
    for a in assets:
        a.updatePrice(a.asset_symbol)


def updatePrice(symbol):
    assets = list(Asset.objects.values_list('asset_symbol', flat=True))
    if symbol not in assets:
        return

    a = Asset()
    a.updatePrice(symbol)
