from market import models, models_d


def run_asset_raw(symbol, lastXrows=5):
    assets = list(models.Asset.objects.values_list('asset_symbol', flat=True))
    if symbol not in assets:
        return

    models_d.D_raw.update_asset(symbol=symbol, lastXrows=lastXrows)
