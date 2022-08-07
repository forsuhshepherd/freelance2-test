from .models import Sector
from rest_framework import serializers


class SectorSerializer(serializers.ModelSerializer):
  class Meta:
    fields = '__all__'
