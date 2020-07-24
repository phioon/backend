from market.models import D_raw


def run_asset_raw(symbol, lastXrows=5):
    # Tratar logs nesse bloco! Trazer informacao de excecoes via dicionario
    dRaw = D_raw()
    dRaw.updateAsset(symbol=symbol, lastXrows=lastXrows)
