from django.db import models
from ws_sectors.models import Sector


class Stock(models.Model):
  name = models.CharField(max_length=100)
  price = models.DecimalField(max_digits=5, decimal_places=2)
  sector = models.ForeignKey(Sector, on_delete=models.CASCADE)
  unallocated = models.IntegerField()
  total_volume = models.IntegerField()

  def __str__(self):
      return self.name

  