from rest_framework import serializers
from .models import Stock


class StockSerializer(serializers.ModelSerialzer):
  class Meta:
    fields = '__all__'
