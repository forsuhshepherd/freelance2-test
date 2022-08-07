from django.db import models
from ws_sectors import Sector


class Stock(models.Model):
  name = models.CharField(max_lenght=100)
  price = models.DecimalField(max_digits=5, decimal_places=2)
  sector = models.ForeignKey(Sector, on_delete=models.CASCADE)
  unallocated = models.Integer()
  total_volume = models.Integer()
