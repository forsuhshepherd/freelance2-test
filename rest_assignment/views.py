import json
import requests

from unicodedata import name
from wsgiref.util import request_uri

from django.shortcuts import render, redirect
from django.db.models import Q
from django.db.models.query import QuerySet
from django.contrib.auth import login as rest_login, get_user_model
from django.contrib.auth.signals import user_logged_out
from django.http import JsonResponse

from knox import views as knox_views

from rest_framework import status
from rest_framework import generics, viewsets, permissions, views

from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.response import Response

from . import serializers
from .models import User, Stock, Sector, Order, Ohlcv, Holding, Market_Day


User = get_user_model()


# Create your views here.
BaseURL = 'https://virtserver.swaggerhub.com/TU2k22/Wallstreet-APIs/1.0.0'

loginURL = BaseURL + '/api/v1/auth/login/'
registerURL = BaseURL + '/api/v1/auth/signup/'


def login(request):
    return render(request, "loginpage.html")


def base(request):
    return render(request, "base.html")


def loginAuthentication(request):

    if request.method == "POST":
        emailLogin = request.POST.get('loginEmailId')
        passwordLogin = request.POST.get('loginPassword')
        docLogin = {"email": emailLogin, "password": passwordLogin}
        jsonLogin = json.dumps(docLogin)
        postLogin = requests.post(loginURL, jsonLogin)
        responsesLogin = postLogin.text
        response_codeLogin = postLogin.status_code
        if response_codeLogin == 200:
            return render(request, "baseLoggedin.html")
    return render(request, "loginpage.html", {'response': responsesLogin})


def registerpage(request):
    return render(request, "register.html")


def register(request):
    if request.method == "POST":
        regName = request.POST.get('registerName')
        regEmail = request.POST.get('registerEmailId')
        regPassword = request.POST.get('registerPassword')
        docRegister = {'name': regName,
                       "email": regEmail, "password": regPassword}
        jsonRegister = json.dumps(docRegister)
        postRegister = requests.post(registerURL, jsonRegister)
        responsesRegister = postRegister.text
        print(responsesRegister)
        response_codeRegister = postRegister.status_code
        if response_codeRegister == 200:
            return redirect("/login")
    return render(request, "register.html")


class StockHoldingsAPIView(generics.ListAPIView):
    queryset = Holding.objects.all()
    serializer_class = serializers.HoldingsSerializer
    permissions_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        queryset = self.queryset.filter(user_id=self.request.user.id)
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset


# class OhlcvAPIView(generics.ListAPIView):
#     queryset = Ohlcv.objects.all()
#     serializer_class = serializers.OhlcvSerializer
#     lookup_field = 'pk'

#     # get market day object
#     def get_object(self):
#         queryset = market_day.objects.all()
#         # Perform the lookup filtering.
#         lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
#         assert lookup_url_kwarg in self.kwargs, (
#             'Expected view %s to be called with a URL keyword argument '
#             'named "%s". Fix your URL conf, or set the `.lookup_field` '
#             'attribute on the view correctly.' %
#             (self.__class__.__name__, lookup_url_kwarg)
#         )
#         filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
#         obj = get_object_or_404(queryset, **filter_kwargs)
#         # May raise a permission denied
#         self.check_object_permissions(self.request, obj)
#         return obj

#     def list(self, request, *args, **kwargs):
#         instance = self.get_object()
#         queryset = self.filter_queryset(self.get_queryset().filter(marked_id=instance))
#         page = self.paginate_queryset(queryset)
#         if page is not None:
#             serializer = self.get_serialzier(page, many=True)
#             return self.get_paginated_response(serializer.data)
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(seralizer.data)


class OhlcMarketAPIView(generics.ListAPIView):
    queryset = Ohlcv.objects.all()
    serializer_class = serializers.OhlcvSerializer

    def get_queryset(self):
        market_id = self.request.query_params.get('market_id')
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        queryset = self.queryset.filter(market_id=market_id)
        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        return queryset


class MarketAPIView(generics.GenericAPIView):
    serializer_class = serializers.MarketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        return Response(status=HTTP_204_NO_CONTENT)


class OrderMatchAPIView(generics.GenericAPIView):
    allowed_methods = ('POST',)
    queryset = Order.objects.all()
    qs_buys = queryset.filter(status='PENDING', type='BUY').order_by('-pk')
    qs_sales = queryset.filter(status='PENDING', type='SELL').order_by('pk')
    serializer_class = serializers.OrderSerializer

    def is_match(self, obj, queryset=False):
        """
        An order for stocks (a stock model instance) matches another(s)
        when its buy bid_price is >= the sell bid_price of any other sell orders.
        args ->
            stock object: Model Instance.Defines the order instance,
            queryset: Boolean. Defines if queryset is returned after execution
        """
        # buy_price = self.qs_buys.filter(stock_id=stock_id).first()
        # sell_price = self.qs_sales.filter(stock_id=stock_id).first()
        if obj.type == 'SELL':
            qs_match = self.qs_buys.order_by(
                '-bid_price').filter(stock_id=stock_id, bid_price__gte=obj.bid_price)
        if obj.type == 'BUY':
            qs_match = self.qs_sales.order_by('bid_price').filter(
                stock_id=stock_id, bid_price__lte=obj.bid_price)
        if qs_match:
            return qs_match if queryset else True
        else:
            return False

    def direct_purchase(self, obj):
        """
        In these cases, where stocks are directly bought from the market/company,
        the new stock price will be the price at which the user bought the stock.
        args ->
            stock object: Model Instance.Defines the order instance
        """
        # buy_bid_price = self.qs_buys.filter(stock_id=obj.stock_id)[0].bid_price
        buy_bid_price = obj.bid_price
        current_price = obj.stock_id.price
        # check if sufficient stocks are available
        if obj.stock_id.total_volume >= obj.bid_volume:
            # check if bid_price matches stock's current price
            if buy_bid_price >= current_price:
                # obj.status = 'COMPLETED'
                # obj.save()
                # update current stock price to price sold at
                Stock.objects.filter(id=obj.stock_id).update(
                    price=buy_bid_price)
                return True
        else:
            return False

    def is_initial(self, stock_id):
        """
        no users are issuing any sell orders or no users own any stocks.
        args ->
            stock object: Model Instance.Defines the order instance
        """
        if not self.qs_sales or not self.qs_sales.filter(stock_id=stock_id):
            return True

    def initial_phase(self):
        """
        In the initial phase, when no users own any stocks and hence can't sell any,
        the buy orders will be fulfilled by looking at the available
        stocks in the respective stock row.
        This will also apply in cases where no sell order is low enough to match any of the buy orders
        """
        for obj in self.get_queryset().filter(status='PENDING'):
            obj_match = self.match(obj)
            if self.is_initial(obj.stock_id) or not obj_match:
                # do direct purchase
                self.direct_purchase(obj)

    def is_partial(self, obj):
        pass

    def partial_transaction(self, obj):
        """
        Partial transactions are allowed, which means a buyer may be buying
        stocks from multiple sellers at different prices and vice versa. Hence a
        buy order can match several sell orders and vice versa.
        """
        highest_buyer = self.qs_buys.filter(stock_id=obj.stock_id)
        lowest_seller = self.qs_sales.filter(
            stock_id=obj.stock_id).order_by('bid_price')
        # highest buyer's matching sellers
        qs = highest_buyer if highest_buyer.first() else lowest_seller[0]
        qs_match = self.is_match(qs, True)

        # buyer is buying from several sellers
        if highest_buyer and qs_match:
            # has_required_volume = qs_match.filter(bid_volume__lte=highest_buyer.bid_volume)
            lowest_seller = qs_match.order_by('bid_price')[0]

        if lowest_seller and qs_match:
            highest_buyer = qs_match.order_by('-pk')[0]

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(status='PENDING')
        if queryset:
            self.initial_phase()
            for obj in queryset:
                qs_match = self.is_match(obj, True)
                # if current order is the latest, its bid_price becomes the match bid_price
                try:
                    if obj.created_on > qs_match[0].created_on:
                        obj.bid_price = qs_match[0].bid_price
                        obj.status = 'COMPLETED'
                        obj.save()
                    success_message = {
                        'message': 'Orders executed Successfully'}
                    return Response(status=status.HTTP_200_OK)
                except:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)


class OrderDetailAPIView(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = serializers.OrderSerializer
    # permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'


class OrderCancelAPIView(generics.DestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = serializers.OrderSerializer
    # permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'


class OrderListCreateAPIView(generics.ListCreateAPIView):
    queryset = Order.objects.filter(Q(type='BUY') | Q(type='SELL'))
    serializer_class = serializers.OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = request.user
            if serializer.validated_data['type'] == 'BUY':
                # making a buy order
                if user.available_funds < serializer.validated_data['bid_price']:
                    # data = {"message":"Insufficient funds", "code": status.HTTP_400_BAD_REQUEST}
                    return Response(status=status.HTTP_400_BAD_REQUEST)
            if serializer.validated_data['type'] == 'SELL':
                # making a sell order
                stock = Stock.objects.filter(
                    serializer.validated_data['stock_id'])
                if stock.total_volume < serializer.data['bid_volume']:
                    # data = {"message":"Insufficient stock", "code": status.HTTP_400_BAD_REQUEST}
                    return Response(status=status.HTTP_400_BAD_REQUEST)

            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class StockAPIView(generics.ListCreateAPIView):
    queryset = Stock.objects.all()
    serializer_class = serializers.StockSerializer
    permissions_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        print(request.headers)
        return super().list(self, request, *args, **kwargs)


class SingleStockAPIView(generics.RetrieveAPIView):
    queryset = Stock.objects.all()
    serializer_class = serializers.StockSerializer
    permissions_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'


class SectorListCreateView(generics.ListCreateAPIView):
    serializer_class = serializers.SectorSerializer
    permission_classes = [permissions.IsAuthenticated]


class SectorRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Sector.objects.all()
    allowed_methods = ['get', 'patch']
    serializer_class = serializers.SectorSerializer
    lookup_fields = 'pk'
    permission_classes = [permissions.IsAuthenticated]


class Record(generics.CreateAPIView):
    # allowed_methods = ('POST',)
    # get method handler
    queryset = User.objects.all().filter(is_superuser=False)
    serializer_class = serializers.UserRegisterSerializer

    # users(name= serializer_class.data['username'],email =serializer_class.data['email'],available_funds = "100.00",blocked_funds = "100.00")
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response({'id': serializer.data['id']}, status=status.HTTP_201_CREATED, headers=headers)
        except:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.ListAPIView):
    queryset = User.objects.all().filter(is_superuser=False)
    serializer_class = serializers.UserSerializer


# login using django-rest-knox
class LoginView(knox_views.LoginView):
    permission_classes = [permissions.AllowAny]
    serializer_class = AuthTokenSerializer

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        rest_login(request, user)
        return super(LoginView, self).post(request, format=None)


class LogoutView(knox_views.LogoutView):
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request, format=None):
        # print(request.headers['Authorization'], 'headers')
        user_logged_out.send(sender=request.user.__class__,
                             request=request, user=request.user)
        print(type(request.headers))
        print(type(request._auth))
        # request._auth.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)



class Login(generics.GenericAPIView):
    # get method handler
    queryset = User.objects.all()
    serializer_class = serializers.UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer_class = serializers.UserLoginSerializer(data=request.data)
        try:
            serializer_class.is_valid(raise_exception=True)
            context = {'token': serializer_class.data['token']}
            return render(request, "baseLoggedin.html", context=context)
        except:
            return Response(serializer_class.data, status=status.HTTP_400_BAD_REQUEST)


class Logout(generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserLogoutSerializer

    def post(self, request, *args, **kwargs):
        serializer_class = serializers.UserLogoutSerializer(data=request.data)
        if serializer_class.is_valid(raise_exception=True):
            return Response(serializer_class.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


def index(request):
    return redirect('/api/login')


def getUsersDetails(request, username):
    getUsersDetails = User.objects.get(name=username)
    return render(request, "userDetails.html", {'getDetails': getUsersDetails})


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer

    def get_object(self):
        pk = self.kwargs.get('pk')

        if pk == "current":
            return self.request.user

        return super(UserViewSet, self).get_object()
