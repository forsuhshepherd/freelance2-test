from operator import pos
from unicodedata import name
from wsgiref.util import request_uri
from django.shortcuts import render, redirect
from django.db.models.query import QuerySet
from django.http import JsonResponse
from django.db.models import Q
import json
import requests
from rest_framework import generics, viewsets, permissions, views
from rest_framework.response import Response
from rest_framework import status
from . import serializers
from .models import users, stocks, sectors, orders, ohlcv, holdings, market_day


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
    queryset = holdings.objects.all()
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
#     queryset = ohlcv.objects.all()
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
    queryset = ohlcv.objects.all()
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


class OrderMatchAPIView(generics.GenericAPIView):
    allowed_methods = ('POST',)
    queryset = orders.objects.all()
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
                stocks.objects.filter(id=obj.stock_id).update(
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
                    return Response(success_message, status=status.HTTP_200_OK)
                except:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response({'message':'Successfull'}, status=status.HTTP_200_OK)


class OrderDetailAPIView(generics.RetrieveAPIView):
    queryset = orders.objects.all()
    serializer_class = serializers.OrderSerializer
    # permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'


class OrderCancelAPIView(generics.DestroyAPIView):
    queryset = orders.objects.all()
    serializer_class = serializers.OrderSerializer
    # permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'


class OrderListCreateAPIView(generics.ListCreateAPIView):
    queryset = orders.objects.filter(Q(type='BUY') | Q(type='SELL'))
    serializer_class = serializers.OrderSerializer
    # permission_classes = [permissions.IsAuthenticated]

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
                stock = stocks.objects.filter(
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
    queryset = stocks.objects.all()
    serializer_class = serializers.StockSerializer
    permissions = [permissions.IsAuthenticated]


class SingleStockAPIView(generics.RetrieveAPIView):
    queryset = stocks.objects.all()
    serializer_class = serializers.StockSerializer
    permissions = [permissions.IsAuthenticated]
    lookup_field = 'pk'


class SectorListCreateView(generics.ListCreateAPIView):
    serializer_class = serializers.SectorSerializer
    permission_classes = [permissions.IsAuthenticated]


class SectorRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = sectors.objects.all()
    allowed_methods = ['get', 'patch']
    serializer_class = serializers.SectorSerializer
    lookup_fields = 'pk'
    permission_classes = [permissions.IsAuthenticated]


class Record(generics.ListCreateAPIView):
    # get method handler
    queryset = users.objects.all()
    serializer_class = serializers.UserSerializer

    # users(name= serializer_class.data['username'],email =serializer_class.data['email'],available_funds = "100.00",blocked_funds = "100.00")
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid()
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.ListAPIView):
    queryset = users.objects.all()
    serializer_class = serializers.UserProfileSerializer


class Login(generics.GenericAPIView):
    # get method handler
    queryset = users.objects.all()
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
    queryset = users.objects.all()
    serializer_class = serializers.UserLogoutSerializer

    def post(self, request, *args, **kwargs):
        serializer_class = serializers.UserLogoutSerializer(data=request.data)
        if serializer_class.is_valid(raise_exception=True):
            return Response(serializer_class.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


def index(request):
    return redirect('/api/login')


def getUsersDetails(request, username):
    getUsersDetails = users.objects.get(name=username)
    return render(request, "userDetails.html", {'getDetails': getUsersDetails})


class UserViewSet(viewsets.ModelViewSet):
    queryset = users.objects.all()
    serializer_class = serializers.UserSerializer

    def get_object(self):
        pk = self.kwargs.get('pk')

        if pk == "current":
            return self.request.user

        return super(UserViewSet, self).get_object()
