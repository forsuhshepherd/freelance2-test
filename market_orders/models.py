from django.db import models


ORDER_TYPES = [
  ('B', 'BUY'),
  ('S', 'SELL')
]
ORDER_STATUS = []


class Order(models.Model):
  stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
  user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
  type = models.CharField(max_length=2, choices=ORDER_TYPES, default=ORDER_TYPES[0])
  bid_price = models.DecimalField(decimal_places=2, max_digits=5)
  bid_volume = models.Integer()
  executed_volume = models.Integer()
  status = models.CharField(max_length=2, choices=ORDER_STATUS, default=ORDER_STATUS[0])
  created_on = models.DateTimeField(auto_now_add=True)
  updated_on = models.DateTimeField(auto_now=True)
  
  def __str__(self):
      return self.id
  