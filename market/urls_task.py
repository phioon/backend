from django.urls import path
from market import views_task

urlpatterns = [
    path('update_realtime/asset/<symbol>/<apiKey>', views_task.update_realtime_asset,
         name='Update Realtime for Asset'),

    path('run_raw/<interval>/asset/<symbol>/<int:last_periods>/<apiKey>', views_task.run_raw_data_asset,
         name='Run Quote data for Asset'),

    path('update_profile/asset/<symbol>/<apiKey>', views_task.update_asset_profile,
         name='Update Asset Profile'),
    path('update_stock_exchange_list/<apiKey>', views_task.update_stock_exchange_list,
         name='Update Stock Exchanges'),
]

# [OFFLINE] These requests run calculations using stored data only. That means, without requesting data from Providers.
urlpatterns += [
    path('offline/run_raw/<interval>/stock_exchange/<stock_exchange>/<apiKey>', views_task.run_raw_data_stock_exchange_offline,
         name='Run offline Raw data for SE'),
    path('offline/run_raw/<interval>/asset/<symbol>/<apiKey>', views_task.run_raw_data_asset_offline,
         name='Run offline Raw data for Asset'),
    path('offline/run_setup/<interval>/stock_exchange/<stock_exchange>/<apiKey>', views_task.run_setup_stock_exchange_offline,
         name='Run offline Setup for SE'),
    path('offline/run_setup/<interval>/asset/<symbol>/<apiKey>', views_task.run_setup_asset_offline,
         name='Run offline Setup for Asset'),
]
