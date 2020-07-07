from market.models import D_raw


def updateRawData(symbol, lastXrows=5):
    # Tratar logs nesse bloco! Trazer informacao de excecoes via dicionario
    dRaw = D_raw()
    dRaw.updateAsset(symbol=symbol, lastXrows=lastXrows)