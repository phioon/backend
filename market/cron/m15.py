from market.models import Asset, Realtime


def update_realtime_asset(symbol):
    assets = list(Asset.objects.values_list('asset_symbol', flat=True))
    if symbol not in assets:
        return

    realtime = Realtime()
    realtime.update_realtime_data(symbol)
