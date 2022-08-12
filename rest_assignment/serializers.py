from email.policy import default
from typing_extensions import Required
from uuid import uuid4

from django.db.models import Q  # for queries
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, get_user_model

from rest_framework import serializers
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.validators import UniqueValidator

from .models import User, Sector, Stock, Order, Market_Day, Ohlcv, Holding


User = get_user_model()


class HoldingsSerializer(serializers.ModelSerializer):
    errors = None

    class Meta:
        model = Holding
        fields = '__all__'


class OhlcvSerializer(serializers.ModelSerializer):
    errors = None

    class Meta:
        model = Ohlcv
        fields = '__all__'


class MarketSerializer(serializers.ModelSerializer):
    errors = None

    class Meta:
        model = Market_Day
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    errors = None

    class Meta:
        model = Order
        fields = '__all__'


class StockSerializer(serializers.ModelSerializer):
    errors = None

    class Meta:
        model = Stock
        fields = '__all__'


class SectorSerializer(serializers.ModelSerializer):
    errors = None

    class Meta:
        model = Sector
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    name = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(max_length=16)

    class Meta:
        model = User
        fields = (
            'name',
            'email',
            'password',
            'blocked_funds',
            'available_funds'
        )
        read_only_fields = ('id', 'blocked_funds', 'available_funds')


class TokenLoginSerializer(AuthTokenSerializer):
    """
    Login using email or username
    """
    username = serializers.CharField(label=_('Username'), required=False)
    email = serializers.EmailField(label=_('Email'), write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        email = attrs.get('email')

        if username and password:
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        elif email and password:
            user = authenticate(request=self.context.get('request'),
            email=email, password=password)
        else:
            msg = _('Must include "username" or "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True,
                                     required=True, style={'input_type': 'password'})

    # default_error_messages = {
    #     'username': 'The username should only contain alphanumeric characters'}

    class Meta:
        model = User
        read_only_fields = (
            "created_on",
            "id",
        ),
        # Contains the things we want to expose
        fields = (
            'id',
            'username',
            'name',
            'email',
            'password',
        )

    def create(self, validated_data):
        # password = validated_data.pop('password')
        # user = super().create(validated_data)
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            name=validated_data['name'],

            password=validated_data['password']
        )
        try:
            # simple password validator
            # validate_password(validated_data['password'], user=user)
            user.set_password(validated_data['password'])
        except ValidationError as exc:
            raise serializers.ValidationError(
                detail=serializers.as_serializer_error(exc)
            )
        user.save()
        return user


class UserLoginSerializer(serializers.ModelSerializer):
    # to accept either name or email
    user_id = serializers.CharField()
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True)
    token = serializers.CharField(required=False, read_only=True)

    def validate(self, data):
        # User,email,password validator
        user_id = data.get("user_id", None)
        password = data.get("password", None)
        if not user_id and not password:
            raise ValidationError("Details not entered.")
        user = None
        # if the email has been passed
        if '@' in user_id:
            user = User.objects.filter(
                Q(email=user_id) &
                Q(password=password)
            ).distinct()
            if not user.exists():
                raise ValidationError("User credentials are not correct.")
            user = User.objects.get(email=user_id)
        else:
            user = User.objects.filter(
                Q(name=user_id) &
                Q(password=password)
            ).distinct()
            if not user.exists():
                raise ValidationError("User credentials are not correct.")
            user = User.objects.get(name=user_id)
        if user.ifLogged:
            raise ValidationError("User already logged in.")
        user.ifLogged = True
        data['token'] = uuid4()
        user.token = data['token']
        user.save()
        return data

    class Meta:
        model = User
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
            user = User.objects.get(token=token)
            if not user.ifLogged:
                raise ValidationError("User is not logged in.")
        except Exception as e:
            raise ValidationError(str(e))
        user.ifLogged = False
        user.token = ""
        user.save()
        data['status'] = "User is logged out."
        return data

    class Meta:
        model = User
        fields = (
            'token',
            'status',
        )
