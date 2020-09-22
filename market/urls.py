from django.urls import path
from . import views

urlpatterns = [
    path('initiator/<apiKey>', views.market_init, name='Market Initiator'),

    path('technicalConditions/', views.TechnicalConditionList.as_view(), name='Technical Conditions'),
    path('stockExchanges/', views.StockExchangeList.as_view(), name='Stock Exchanges'),
    path('assets/', views.AssetList.as_view(), name='Assets'),
    path('indicators/', views.IndicatorList, name='Indicators avaliable'),
    path('d/raw/', views.D_RawList.as_view(), name='D_Raw data'),
    path('d/raw/latest/', views.D_RawLatestList, name='D_raw latest data'),
    path('d/ema/latest/', views.D_EmaLatestList, name='D_ema latest data'),
    path('d/phibo/latest/', views.D_PhiboLatestList, name='D_pvpc latest data'),
    path('d/setups/', views.D_SetupList.as_view(), name='D_Setup data'),
    path('d/setupSummary/', views.D_SetupSummaryList.as_view(), name='D_SetupSummary data'),
]

urlpatterns += [
    # Stock Exchange
    path('task/updateStockExchangeList/<apiKey>', views.update_stock_exchange_list,
         name='Update Stock Exchanges'),
    # Asset
    path('cron/updateAssetList/<se_short>/<apiKey>', views.update_asset_list,
         name='Update Asset List'),
    path('cron/runRaw/D/se_short/<se_short>/<int:last_x_rows>/<apiKey>', views.run_raw_data_se_short,
         name='Run Raw data for SE'),
    # Real-time
    path('cron/updateRealtime/se_short/<se_short>/<apiKey>', views.update_realtime_se_short,
         name='Update Realtime for SE'),

    # GCloud tasks
    path('task/updateProfile/asset/<symbol>/<apiKey>', views.update_asset_profile,
         name='Update Asset Profile'),
    path('task/runRaw/D/asset/<symbol>/<int:last_x_rows>/<apiKey>', views.run_raw_data_asset,
         name='Run Raw data for Asset'),
    path('task/updateRealtime/asset/<symbol>/<apiKey>', views.update_realtime_asset,
         name='Update Realtime for Asset'),
]

# On-demand Offline Requests
# These requests run calculations using only stored data. That means, without requesting data to Providers.
urlpatterns += [
    # Offline
    path('task/offline/runRaw/D/se_short/<se_short>/<apiKey>', views.run_offline_raw_data_se_short,
         name='Run offline Raw data for SE'),
    path('task/offline/runRaw/D/asset/<symbol>/<apiKey>', views.run_offline_raw_data_asset,
         name='Run offline Raw data for Asset'),
    path('task/offline/runSetup/D/se_short/<se_short>/<apiKey>', views.run_offline_setup_se_short,
         name='Run offline Setup for SE'),
    path('task/offline/runSetup/D/asset/<symbol>/<apiKey>', views.run_offline_setup_asset,
         name='Run offline Setup for Asset'),
]
