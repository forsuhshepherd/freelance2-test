from email.policy import default
from typing_extensions import Required
from django.db.models import Q  # for queries
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import users, sectors, stocks, orders, market_day, ohlcv, holdings
from django.core.exceptions import ValidationError
from uuid import uuid4


class HoldingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = holdings
        fields = '__all__'


class OhlcvSerializer(serializers.ModelSerializer):
    class Meta:
        model = ohlcv
        fields = '__all__'


class MarketSerializer(serializers.ModelSerializer):
    class Meta:
        model = market_day
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
  class Meta:
    model = orders
    fields = '__all__'


class StockSerializer(serializers.ModelSerializer):
  class Meta:
    model = stocks
    fields = '__all__'


class SectorSerializer(serializers.ModelSerializer):
  class Meta:
    model = sectors
    fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=users.objects.all())]
    )
    name = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=users.objects.all())]
    )
    password = serializers.CharField(max_length=16)


    class Meta:
        model = users
        fields = (
            'name',
            'email',
            'password',
            'blocked_funds',
            'available_funds'
        )
        read_only = ('blocked_funds', 'available_funds',)


class UserLoginSerializer(serializers.ModelSerializer):
    # to accept either name or email
    user_id = serializers.CharField()
    password = serializers.CharField()
    token = serializers.CharField(required=False, read_only=True)

    def validate(self, data):
        # users,email,password validator
        user_id = data.get("user_id", None)
        password = data.get("password", None)
        if not user_id and not password:
            raise ValidationError("Details not entered.")
        user = None
        # if the email has been passed
        if '@' in user_id:
            user = users.objects.filter(
                Q(email=user_id) &
                Q(password=password)
            ).distinct()
            if not user.exists():
                raise ValidationError("users credentials are not correct.")
            user = users.objects.get(email=user_id)
        else:
            user = users.objects.filter(
                Q(name=user_id) &
                Q(password=password)
            ).distinct()
            if not user.exists():
                raise ValidationError("users credentials are not correct.")
            user = users.objects.get(name=user_id)
        if user.ifLogged:
            raise ValidationError("users already logged in.")
        user.ifLogged = True
        data['token'] = uuid4()
        user.token = data['token']
        user.save()
        return data

    class Meta:
        model = users
        fields = (
            'user_id',
            'password',
            'token',
        )

        read_only_fields = (
            'token',
        )


class UserLogoutSerializer(serializers.ModelSerializer):
    token = serializers.CharField()
    status = serializers.CharField(required=False, read_only=True)

    def validate(self, data):
        token = data.get("token", None)
        print(token)
        user = None
        try:
            user = users.objects.get(token=token)
            if not user.ifLogged:
                raise ValidationError("users is not logged in.")
        except Exception as e:
            raise ValidationError(str(e))
        user.ifLogged = False
        user.token = ""
        user.save()
        data['status'] = "users is logged out."
        return data

    class Meta:
        model = users
        fields = (
            'token',
            'status',
        )


