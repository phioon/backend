from django.urls import path, include
from . import views

urlpatterns = [
    path('exchanges/', views.ExchangeList.as_view(), name='Exchange List'),
    path('exchanges/<exchange>/', views.ExchangeDetail.as_view(), name='Exchange Detail'),
    path('exchanges/<exchange>/tickers/', views.TickersByExchange.as_view(), name='Tickers by SE'),

    path('tickers/<ticker>/profile/', views.AssetProfileDetail.as_view(), name='Asset Profile'),
    path('tickers/<ticker>/realtime/', views.AssetRealtimeDetail.as_view(), name='Asset Realtime'),
    path('tickers/<ticker>/eod/', views.EodList.as_view(), name='EOD data'),
    path('tickers/<ticker>/m60/', views.M60List.as_view(), name='M60 data'),
]
