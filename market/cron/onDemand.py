from market import models, models_d


def update_stock_exchange_list():
    se = models.StockExchange()
    se.update_stock_exchange_list()


def run_offline_raw_data_asset(symbol):
    d_raw = models_d.D_raw()
    d_raw.updateDependencies(symbol=symbol, lastXrows=5000)


def run_offline_setup_asset(symbol):
    d_setup = models_d.D_phiOperation()
    d_setup.updateAsset(symbol=symbol)
