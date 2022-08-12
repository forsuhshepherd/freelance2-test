from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


ORDER_STATUS = [
    ('P', 'Pending'),
    ('C', 'Completed')
]

ORDER_TYPE = [
    ('B', 'Buy'),
    ('S', 'Sell')
]


class User(AbstractUser):
    first_name = None
    last_name = None
    # email and password already present
    name = models.CharField(max_length=50)
    available_funds = models.DecimalField(max_digits=8, decimal_places=2,default="400000.00")
    blocked_funds = models.DecimalField(max_digits=8, decimal_places=2,default="400000.00")

    REQUIRED_FIELDS =['email']

    def __str__(self):
        return "{} -{}".format(self.name, self.email)


class Sector(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)


class Market_Day(models.Model):
    day = models.IntegerField()
    status = models.CharField(max_length=10)


class Stock(models.Model):
    name = models.CharField(max_length=20)
    total_volume = models.IntegerField()
    unallocated = models.IntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    sector_id = models.ForeignKey(Sector, on_delete=models.CASCADE)


class Order(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    stock_id = models.ForeignKey(Stock, on_delete=models.CASCADE)
    bid_price = models.DecimalField(max_digits=8, decimal_places=2)   
    type = models.CharField(max_length=4)
    # type = models.CharField(max_lenghth=2, choices=ORDER_TYPE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20)
    # status = models.CharField(max_lenghth=2, choices=ORDER_STATUS)
    bid_volume = models.IntegerField()
    executed_volume = models.IntegerField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


class Holding(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    stock_id = models.ForeignKey(Stock, on_delete=models.CASCADE)
    volume = models.IntegerField()
    bid_price = models.DecimalField(max_digits=8, decimal_places=2)
    brought_on = models.DateField()


class Ohlcv(models.Model):
    market_id = models.ForeignKey(Market_Day, on_delete=models.CASCADE)
    stock_id = models.ForeignKey(Stock, on_delete=models.CASCADE)
    open = models.DecimalField(max_digits=8, decimal_places=2)
    high = models.DecimalField(max_digits=8, decimal_places=2)
    low = models.DecimalField(max_digits=8, decimal_places=2)
    close = models.DecimalField(max_digits=8, decimal_places=2)
    volume = models.IntegerField()
