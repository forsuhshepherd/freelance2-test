from django.shortcuts import render
from rest_framework import generics, permissions, viewsets
from .serializers import SectorSerializer
from .models import Sector


class SectorListCreateView(generics.ListCreateAPIView):
  serializer_class = SectorSerializer
  permission_classes = [permissions.IsAuthenticated]


class SectorRetrieveUpdateView(generics.RetrieveUpdateAPIView):
  allowed_methods = ['get', 'patch']
  serializer_class = SectorSerializer
  lookup_fields = 'pk'
  permission_classes = [permissions.IsAuthenticated]
