from django.urls import path, include
from market import views

urlpatterns = [
    path('d/', include('market.urls_d')),
    path('m60/', include('market.urls_m60')),

    path('technical_conditions/', views.TechnicalConditionList.as_view(), name='Technical Conditions'),
    path('stock_exchanges/', views.StockExchangeList.as_view(), name='Stock Exchanges'),
    path('assets/', views.AssetList.as_view(), name='Assets'),
    path('indicators/', views.IndicatorList, name='List of indicators avaliable'),

    path('task/', include('market.urls_task')),
    path('cron/', include('market.urls_cron')),

    path('initiator/<apiKey>', views.market_init, name='Market Initiator'),
]
