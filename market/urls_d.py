from django.urls import path
from market import views_d

urlpatterns = [
    path('raw/', views_d.RawList.as_view()),
    path('quote/latest/', views_d.quote_latest_list),
    path('sma/latest/', views_d.sma_latest_list),
    path('ema/latest/', views_d.ema_latest_list),
    path('phibo/latest/', views_d.phibo_latest_list),
    path('roc/latest/', views_d.roc_latest_list),
    path('setups/', views_d.SetupList.as_view()),
    path('setup_stats/', views_d.SetupStatsList.as_view()),
]
