from operator import pos
from wsgiref.util import request_uri
from django.shortcuts import render, redirect
import json
import requests
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from .serializers import UserSerializer, UserLoginSerializer, UserLogoutSerializer
from .models import User




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


class Record(generics.ListCreateAPIView):
    # get method handler
    queryset = User.objects.all()
    serializer_class = UserSerializer


class Login(generics.GenericAPIView):
    # get method handler
    queryset = User.objects.all()
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer_class = UserLoginSerializer(data=request.data)
        if serializer_class.is_valid(raise_exception=True):
            return Response(serializer_class.data, status=HTTP_200_OK)
        return Response(serializer_class.errors, status=HTTP_400_BAD_REQUEST)


class Logout(generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserLogoutSerializer

    def post(self, request, *args, **kwargs):
        serializer_class = UserLogoutSerializer(data=request.data)
        if serializer_class.is_valid(raise_exception=True):
            return Response(serializer_class.data, status=HTTP_200_OK)
        return Response(serializer_class.errors, status=HTTP_400_BAD_REQUEST)


def index(request):
    return redirect('/api/login')