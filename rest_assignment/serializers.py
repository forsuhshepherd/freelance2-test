from django.db.models import Q  # for queries
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import users
from django.core.exceptions import ValidationError
from uuid import uuid4


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
    available_funds = "100.00"
    blocked_funds = "100.00"

    class Meta:
        model = users
        fields = (
            'name',
            'email',
            'password',
            'available_funds',
            'blocked_funds'
        )


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
        users = None
        # if the email has been passed
        if '@' in user_id:
            users = users.objects.filter(
                Q(email=user_id) &
                Q(password=password)
            ).distinct()
            if not users.exists():
                raise ValidationError("users credentials are not correct.")
            users = users.objects.get(email=user_id)
        else:
            users = users.objects.filter(
                Q(name=user_id) &
                Q(password=password)
            ).distinct()
            if not users.exists():
                raise ValidationError("users credentials are not correct.")
            users = users.objects.get(name=user_id)
        if users.ifLogged:
            raise ValidationError("users already logged in.")
        users.ifLogged = True
        data['token'] = uuid4()
        users.token = data['token']
        users.save()
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
        users = None
        try:
            users = users.objects.get(token=token)
            if not users.ifLogged:
                raise ValidationError("users is not logged in.")
        except Exception as e:
            raise ValidationError(str(e))
        users.ifLogged = False
        users.token = ""
        users.save()
        data['status'] = "users is logged out."
        return data

    class Meta:
        model = users
        fields = (
            'token',
            'status',
        )
