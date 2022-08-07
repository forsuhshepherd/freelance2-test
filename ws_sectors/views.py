from django.shortcuts import render
from rest_framework import permissions, viewsets
from .serializers import SectorSerializer
from .models import Sector
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView


class SectorListCreateView(generics.ListCreateAPIView):
  serializer_class = SectorSerializer
  permission_classes = [permissions.IsAuthenticated]


class SectorRetrieveUpdateView(generics.RetrieveUpdateAPIView):
  allowed_methods = ['get', 'patch']
  serializer_class = SectorSerializer
  lookup_fields = 'pk'
  permission_classes = [permissions.IsAuthenticated]
