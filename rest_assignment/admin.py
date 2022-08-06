from django.contrib import admin
from .models import users, stocks, sectors, market_day, ohlcv, holdings, orders
# Register your models here.
admin.site.register(users)
admin.site.register(stocks)
admin.site.register(sectors)
admin.site.register(market_day)
admin.site.register(ohlcv)
admin.site.register(holdings)
admin.site.register(orders)
