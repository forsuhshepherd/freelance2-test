from django.db import models

# Create your models here.


ORDER_STATUS = [
    ('P', 'Pending'),
    ('C', 'Completed')
]

ORDER_TYPE = [
    ('B', 'Buy'),
    ('S', 'Sell')
]


class users(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    password = models.CharField(max_length=50)
    ifLogged = models.BooleanField(default=False)
    token = models.CharField(max_length=500, null=True, default="")
    available_funds = models.DecimalField(max_digits=5, decimal_places=2,default="100.00")
    blocked_funds = models.DecimalField(max_digits=5, decimal_places=2,default="100.00")

    def __str__(self):
        return "{} -{}".format(self.name, self.email)


class sectors(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)


class market_day(models.Model):
    day = models.IntegerField()
    status = models.CharField(max_length=10)


class stocks(models.Model):
    name = models.CharField(max_length=20)
    total_volume = models.IntegerField()
    unallocated = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    sector_id = models.ForeignKey(sectors, on_delete=models.CASCADE)


class orders(models.Model):
    user_id = models.ForeignKey(users, on_delete=models.CASCADE)
    stock_id = models.ForeignKey(stocks, on_delete=models.CASCADE)
    bid_price = models.DecimalField(max_digits=5, decimal_places=2)   
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


class holdings(models.Model):
    user_id = models.ForeignKey(users, on_delete=models.CASCADE)
    stock_id = models.ForeignKey(stocks, on_delete=models.CASCADE)
    volume = models.IntegerField()
    bid_price = models.DecimalField(max_digits=5, decimal_places=2)
    brought_on = models.DateField()


class ohlcv(models.Model):
    market_id = models.ForeignKey(market_day, on_delete=models.CASCADE)
    stock_id = models.IntegerField()
    open = models.DecimalField(max_digits=5, decimal_places=2)
    high = models.DecimalField(max_digits=5, decimal_places=2)
    low = models.DecimalField(max_digits=5, decimal_places=2)
    close = models.DecimalField(max_digits=5, decimal_places=2)
    volume = models.IntegerField()
