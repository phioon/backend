from market.models import StockExchange, Asset, Profile


def update_asset_list(se_short):
    stockExchanges = list(StockExchange.objects.values_list('se_short', flat=True).distinct())
    if se_short not in stockExchanges:
        return

    a = Asset()
    a.update_assets_by_stock_exchange(se_short=se_short)


def update_asset_profile(symbol):
    assets = list(Asset.objects.values_list('asset_symbol', flat=True))
    if symbol not in assets:
        return

    ap = Profile()
    ap.update_asset_profile(symbol)
