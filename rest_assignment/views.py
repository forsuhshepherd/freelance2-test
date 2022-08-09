from operator import pos
from unicodedata import name
from wsgiref.util import request_uri
from django.shortcuts import render, redirect
from django.db.models.query import QuerySet
from django.db.models import Q
import json
import requests
from rest_framework import generics, viewsets, permissions
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, UserLoginSerializer, UserLogoutSerializer, \
    SectorSerializer, StockSerializer, OrderSerializer, MarketSerializer, OhlcvSerializer, HoldingsSerializer
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
    serializer_class = HoldingsSerializer
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
#     serializer_class = OhlcvSerializer
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
    serializer_class = OhlcvSerializer

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
    serializer_class = MarketSerializer
    permission_classes = [permissions.IsAuthenticated]


class OrderMatchAPIView(generics.ListAPIView):
    queryset = orders.objects.all().filter(
        Q(type='BUY') | Q(type='SELL')).distinct()
    qs_buys = orders.objects.filter(type='BUY').order_by('-pk')
    qs_sales = orders.objects.filter(type='SELL').order_by('pk')
    serializer_class = OrderSerializer

    def is_match(self, stock_id):
        """
        An order for stocks (a stock model instance) matches another(s) when it buy bid_price is >= the sell bid_price
        of any other sell orders.
        """
        buy_price = self.qs_buys.filter(stock_id=stock_id).first()
        sell_price = self.qs_sells.filter(stock_id=stock_id).first()

        for obj in self.get_querset().filter(status=PENDING):
            if buy_price >= sell_price:
                return True
            else:
                return False

    def direct_purchase(self, obj):
        """
        In these cases, where stocks are directly bought from the market/company, 
        the new stock price will be the price at which the user bought the stock
        """
        buy_bid_price = self.qs_buys.filter(stock_id=obj.stock_id)[0].bid_price
        current_price = obj.stock_id.price
        if buy_bid_price >= current_price:
            stocks.objects.filter(id=obj.stock_id).update(price=buy_bid_price)

    def initial_phase(self):
        """
        In the initial phase, when no users own any stocks and hence can't sell any, 
        the buy orders will be fulfilled by looking at the available 
        stocks in the respective stock row. 
        This will also apply in cases where no sell order is low enough to match any of the buy orders
        """
        for obj in self.get_queryset():
            obj_match = self.match(obj.stock_id)
            if obj.user_id == None and obj.type == 'BUY' or obj.type == 'SELL' and not obj_match:
                obj.bid_price = obj.stock_id.price
                obj.bid_volume = obj.stock_id.total_volume
                obj.save()
            if obj.type == 'BUY' and not obj_match:
                self.direct_purchase(obj)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        response = {}

        for data in serializer.data:
            if serializer.data['type'] == 'BUY':
                response['BUYS'] += data
                sorted(response['BUYS'], key=lambda x: x['name'])
            else:
                sales += data
                sorted(sales, key=lambda x: x['name'], reverse=True)
                response.update(sales)
        return Response(response, status=status.HTTP_200_OK)


class OrderDetailAPIView(generics.RetrieveAPIView):
    queryset = orders.objects.all()
    serializer_class = OrderSerializer
    # permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'


class OrderCancelAPIView(generics.DestroyAPIView):
    queryset = orders.objects.all()
    serializer_class = OrderSerializer
    # permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'


class OrderListCreateAPIView(generics.ListCreateAPIView):
    queryset = orders.objects.filter(Q(type='BUY') | Q(type='SELL'))
    serializer_class = OrderSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = request.user
            if serializer.validated_data['type'] == 'BUY':
                # making a buy order
                if user.available_funds < serializer.validated_data['bid_price']:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
            if serializer.validated_data['type'] == 'SELL':
                # making a sell order
                stock = stocks.objects.filter(
                    serializer.validated_data['stock_id'])
                if stock.total_volume < serializer.data['bid_volume']:
                    return Response(status=status.HTTP_400_BAD_REQUEST)

            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class StockAPIView(generics.ListCreateAPIView):
    queryset = stocks.objects.all()
    serializer_class = StockSerializer
    permissions = [permissions.IsAuthenticated]


class SingleStockAPIView(generics.RetrieveAPIView):
    queryset = stocks.objects.all()
    serializer_class = StockSerializer
    permissions = [permissions.IsAuthenticated]
    lookup_field = 'pk'


class SectorListCreateView(generics.ListCreateAPIView):
    serializer_class = SectorSerializer
    permission_classes = [permissions.IsAuthenticated]


class SectorRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = sectors.objects.all()
    allowed_methods = ['get', 'patch']
    serializer_class = SectorSerializer
    lookup_fields = 'pk'
    permission_classes = [permissions.IsAuthenticated]


class Record(generics.ListCreateAPIView):
    # get method handler
    queryset = users.objects.all()
    serializer_class = UserSerializer
    # users(name= serializer_class.data['username'],email =serializer_class.data['email'],available_funds = "100.00",blocked_funds = "100.00")
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class Login(generics.GenericAPIView):
    # get method handler
    queryset = users.objects.all()
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer_class = UserLoginSerializer(data=request.data)
        if serializer_class.is_valid(raise_exception=True):
            status = HTTP_200_OK
            context = {'data': serializer_class.data, "status": status}
            return render(request, "baseLoggedin.html", context=context)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class Logout(generics.GenericAPIView):
    queryset = users.objects.all()
    serializer_class = UserLogoutSerializer

    def post(self, request, *args, **kwargs):
        serializer_class = UserLogoutSerializer(data=request.data)
        if serializer_class.is_valid(raise_exception=True):
            return Response(serializer_class.data, status=HTTP_200_OK)
        return Response(status=HTTP_400_BAD_REQUEST)


def index(request):
    return redirect('/api/login')


def getUsersDetails(request, username):
    getUsersDetails = users.objects.get(name=username)
    return render(request, "userDetails.html", {'getDetails': getUsersDetails})


class UserViewSet(viewsets.ModelViewSet):
    queryset = users.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        pk = self.kwargs.get('pk')

        if pk == "current":
            return self.request.user

        return super(UserViewSet, self).get_object()
