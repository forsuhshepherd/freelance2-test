from django.urls import path
from .views import StockAPIView, SingleStockAPIView


urlpatterns = [
    path('/stocks', StockAPIView.as_view()),
    path('/stocks/<int:pk>', SingleStockAPIView.as_view()),
]
