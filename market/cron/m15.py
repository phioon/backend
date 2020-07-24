from market.models import StockExchange, Asset, Realtime
from datetime import datetime, timedelta


def update_realtime_se_short(se_short):
    stockExchanges = list(StockExchange.objects.values_list('se_short', flat=True).distinct())
    if se_short not in stockExchanges:
        return

    today = datetime.today().date()
    a_month_ago = today - timedelta(days=30)

    realtime = Realtime()
    assets = Asset.objects.filter(last_access_time__gte=a_month_ago)
    for a in assets:
        realtime.update_realtime_data(a.asset_symbol)


def update_realtime_asset(symbol):
    assets = list(Asset.objects.values_list('asset_symbol', flat=True))
    if symbol not in assets:
        return

    realtime = Realtime()
    realtime.update_realtime_data(symbol)
