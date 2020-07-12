from market.models import StockExchange, Asset, TechnicalCondition


def app_initiator():
    # Before execute this function:
    #   1. Create superuser api
    #   2. Create superuser frontend_api

    se = StockExchange()
    a = Asset()
    tc = TechnicalCondition()

    se_short_list = ['BVMF']

    tc.init()
    se.update_stock_exchange_list()

    for se_short in se_short_list:
        a.update_assets_by_stock_exchange(se_short)
