from rest_framework import serializers
from .models import *
from django.core.validators import RegexValidator


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = ['id', 'phone_number', 'postal_code', 'address_line', 'city', 'province']
        read_only_fields = ['id']


class RequestOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=15,
        validators=[
            RegexValidator(regex=r'^09\d{9}$',message="Please enter a valid phone number")])

class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    code = serializers.CharField(max_length=6)

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

