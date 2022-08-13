from django.contrib import admin
from .models import User, Stock, Sector, Market_Day, Ohlcv, Holding, Order
# Register your models here.
admin.site.register(User)
admin.site.register(Stock)
admin.site.register(Sector)
admin.site.register(Market_Day)
admin.site.register(Ohlcv)
admin.site.register(Holding)
admin.site.register(Order)
