from django.db import models

# Create your models here.
class users(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    available_funds = models.DecimalField(max_digits=5,decimal_places=2)
    blocked_funds = models.DecimalField(max_digits=5,decimal_places=2)

class sectors(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)

class market_day(models.Model):
    day = models.IntegerField(max_length=10)
    status = models.CharField(max_length=10)

class stocks(models.Model):
    name = models.CharField(max_length=20)
    total_volume = models.IntegerField(max_length=11)
    unallocated = models.IntegerField(max_length=11)
    price = models.DecimalField(max_digits=5,decimal_places=2)
    sector_id = models.ForeignKey()
