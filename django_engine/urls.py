from django.urls import path, include
from . import views

urlpatterns = [
    path('api/market/', include('market.urls')),
    path('api/provider/', include('provider.urls')),
    path('_ah/warmup/', views.warmup, name='gae_warmup_request')
]
