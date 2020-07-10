from django.contrib.auth.models import User
from market.models import StockExchange, Asset, TechnicalCondition


def app_initiator():
    user = User.objects.get(username='frontend_api')
    if user is None:
        User.objects.create_superuser(
            username='frontend_api',
            password='#P1q2w3e4r$Api',
            email='support.cloud@phioon.com'
        )
    user = User.objects.get(username='api')
    if user is None:
        User.objects.create_superuser(
            username='api',
            password='#P1q2w3e4r$Api',
            email='support.cloud@phioon.com'
        )

    se = StockExchange()
    a = Asset()
    tc = TechnicalCondition()

    se_short_list = ['BVMF']

    tc.init()
    se.update_stock_exchange_list()

    for se_short in se_short_list:
        a.update_assets_by_stock_exchange(se_short)
