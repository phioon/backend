from django.urls import path, include
from api_engine import apiMarket


urlpatterns = [
    path('market/technicalConditions/', apiMarket.TechnicalConditionList.as_view(), name='Technical Conditions'),
    path('market/stockExchanges/', apiMarket.StockExchangeList.as_view(), name='StockExchanges'),
    path('market/assets/', apiMarket.AssetList.as_view(), name='Assets'),
    path('market/d/raw/', apiMarket.D_RawList.as_view(), name='D_Raw data'),
    path('market/d/setups/', apiMarket.D_SetupList.as_view(), name='D_Setup data'),
    path('market/d/setupSummary/', apiMarket.D_SetupSummaryList.as_view(), name='D_SetupSummary data'),

    path('market/initiator/<apiKey>', apiMarket.market_init, name='Market Initiator'),
]

urlpatterns += [
    path('market/cron/updateStockExchangeList/<apiKey>', apiMarket.updateStockExchangeList,
         name='Update Stock Exchanges'),
    path('market/cron/updateAssetList/<se_short>/<apiKey>', apiMarket.updateAssetList,
         name='Update Asset List'),
    path('market/cron/runSymbols/D/<se_short>/<int:lastXrows>/<apiKey>', apiMarket.runSymbols_D,
         name='Create Daily Tasks'),
    path('market/cron/updateAssetPrices/<se_short>/<apiKey>', apiMarket.updateAssetPrices,
         name='Update Asset Prices'),

    path('market/task/updateAssetPrice/m15/<symbol>/<apiKey>', apiMarket.updateAssetPrice,
         name='cron_asset_price'),
    path('market/task/runSymbol/D/<symbol>/<int:lastXrows>/<apiKey>', apiMarket.runSymbol_D,
         name='cron_symbol_daily'),
]
