from market.models import Asset, D_raw


def run_asset_raw(symbol, lastXrows=5):
    assets = list(Asset.objects.values_list('asset_symbol', flat=True))
    if symbol not in assets:
        return

    dRaw = D_raw()
    dRaw.updateAsset(symbol=symbol, lastXrows=lastXrows)
