"""ASSIGNMENT4 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from rest_assignment import views
from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    path('', views.base, name="base"),
    # path("login",views.login,name="login"),
    # path("loginform",views.loginAuthentication,name="loginform"),
    # path("registerpage",views.registerpage,name="registerpage"),
    # path("register",views.register,name="register"),
    path('addUser/', views.Record.as_view(), name="register"),
    path('login/', views.Login.as_view(), name="login"),
    path('logout/', views.Logout.as_view(), name="logout"),
    # path('users/',views.UserViewSet.as_view(),name="user"),
    re_path(r'^media/(?P<path>.*)$', serve,
            {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve,
            {'document_root': settings.STATIC_ROOT}),

    path('api/v1/sectors/', views.SectorListCreateView.as_view(), name='sector-list-create'),
    path('api/v1/sectors/<int:pk>/', views.SectorRetrieveUpdateView.as_view(), name='sector-update'),
    path('api/v1/stocks/', views.StockAPIView.as_view(), name='stock-list'),
    path('api/v1/stocks/<int:pk>/', views.SingleStockAPIView.as_view(), name='stock-detail'),
    path('api/v1/orders/', views.OrderListCreateAPIView.as_view(), name='order-list-create'),
    path('api/v1/orders/<int:pk>/', views.OrderDetailAPIView.as_view(), name='order-detail'),
    path('api/v1/orders/<int:pk>/cancel/', views.OrderCancelAPIView.as_view(), name='order-cancel'),
    path('api/v1/market/open/', views.MarketAPIView.as_view(), name='market'),
    path('api/v1/market/ohlc/', views.OhlcMarketAPIView.as_view(), name='ohlc'),     # filter using query_param: market_id
    # path('v1/market/<int:pk>/ohlc/', views.OhlcvAPIView.as_view(), name='ohlc'),
    path('v1/holdings/', views.StockHoldingsAPIView.as_view(), name='holdings'),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
