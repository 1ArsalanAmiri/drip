from rest_framework import serializers
from .models import UserAddress, OTP, User


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = ['id', 'full_name', 'phone_number', 'postal_code', 'address_line', 'city', 'province']
        read_only_fields = ['id']


class RequestOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    code = serializers.CharField(max_length=6)

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()