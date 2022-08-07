from django.shortcuts import render
from rest_framework import generics, permissions
from .serializers import OrderSerializer


class OrderListCreateAPIView(generics.ListCreateAPIView):
  serializer_class = OrderSerializer
  permission_classes = [permissions.IsAuthenticated]

  def create(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    self.perform_create(serializer)
    headers = self.get_success_headers(serializer.data)
    return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    