from market.models import StockExchange, D_raw, D_setup


def update_stock_exchange_list():
    se = StockExchange()
    se.update_stock_exchange_list()


def run_offline_raw_data_asset(symbol):
    d_raw = D_raw()
    d_raw.updateDependencies(symbol=symbol, lastXrows=5000)


def run_offline_setup_asset(symbol):
    d_setup = D_setup()
    d_setup.updateAsset(symbol=symbol)
