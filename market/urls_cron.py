from django.urls import path
from market import views_cron

urlpatterns = [
    path('update_realtime/stock_exchange/<stock_exchange>/<apiKey>/', views_cron.update_realtime_stock_exchange,
         name='Update Realtime for SE'),
    path('update_asset_list/<stock_exchange>/<apiKey>/', views_cron.update_asset_list,
         name='Update Asset List'),
    path('run_raw/<interval>/stock_exchange/<stock_exchange>/<int:last_periods>/<apiKey>/', views_cron.run_raw_data_stock_exchange,
         name='Run Raw data for SE'),
]
