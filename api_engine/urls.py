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
    # Stock Exchange
    path('market/task/updateStockExchangeList/<apiKey>', apiMarket.update_stock_exchange_list,
         name='Update Stock Exchanges'),

    # Asset
    path('market/cron/updateAssetList/<se_short>/<apiKey>', apiMarket.update_asset_list,
         name='Update Asset List'),
    path('market/cron/updateAssetProfile/<symbol>/<apiKey>', apiMarket.update_asset_profile,
         name='Update Asset Profile'),

    path('market/cron/runRaw/D/se_short/<se_short>/<int:last_x_rows>/<apiKey>', apiMarket.run_raw_data_se_short,
         name='Run Raw data SE'),

    # Setups
    path('market/task/runOfflineRaw/D/asset/<symbol>/<apiKey>', apiMarket.run_offline_raw_data_asset,
         name='Run Offline Raw data Asset'),

    # Real-time
    path('market/cron/updateRealtime/se_short/<se_short>/<apiKey>', apiMarket.update_realtime_se_short,
         name='Update Realtime SE'),
    path('market/cron/updateRealtime/asset/<symbol>/<apiKey>', apiMarket.update_realtime_asset,
         name='Update Realtime Asset'),

    # GCloud tasks
    path('market/task/runRaw/D/asset/<symbol>/<int:last_x_rows>/<apiKey>', apiMarket.run_raw_data_asset,
         name='Run Raw data Asset'),
]
