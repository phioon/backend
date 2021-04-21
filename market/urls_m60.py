from django.urls import path
from market import views_m60

urlpatterns = [
    path('raw/', views_m60.RawList.as_view()),
    path('quote/latest/', views_m60.quote_latest_list),
    path('sma/latest/', views_m60.sma_latest_list),
    path('ema/latest/', views_m60.ema_latest_list),
    path('phibo/latest/', views_m60.phibo_latest_list),
    path('roc/latest/', views_m60.roc_latest_list),
    path('setups/', views_m60.SetupList.as_view()),
    path('setup_stats/', views_m60.SetupStatsList.as_view()),
]
