from django.shortcuts import render
from rest_framework import generics, permissions
from .serializers import StockSerializer

class StockAPIView(generics.ListCreateAPIView):
  serializer_class = StockSerializer
  permissions = [permissions.IsAuthenticated]


class SingleStockAPIView(generics.RetrieveAPIView):
  serializer_class = StockSerializer
  permissions = [permissions.IsAuthenticated]
  lookup_field = 'pk'
