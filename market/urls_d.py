from django.urls import path
from market import views_d

urlpatterns = [
    path('raw/', views_d.D_RawList.as_view()),
    path('quote/latest/', views_d.d_quote_latest_list),
    path('sma/latest/', views_d.d_sma_latest_list),
    path('ema/latest/', views_d.d_ema_latest_list),
    path('phibo/latest/', views_d.d_phibo_latest_list),
    path('roc/latest/', views_d.d_roc_latest_list),
    path('setups/', views_d.D_SetupList.as_view()),
    path('setup_stats/', views_d.D_SetupStatsList.as_view()),
]
