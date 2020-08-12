from django.urls import path, include


urlpatterns = [
    path('api/market/', include('market.urls')),
    path('api/provider/', include('provider.urls'))
]
