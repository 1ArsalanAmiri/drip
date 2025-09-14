# accounts/views.py
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .models import *
from .serializers import *
from .utils import send_sms
from datetime import timedelta
from django.utils import timezone
from secrets import randbelow
from django.conf import settings
from django.db import transaction
from django.core.cache import cache

User = get_user_model()

OTP_EXPIRY_MINUTES = 5
OTP_REQUEST_COOLDOWN_MINUTES = 2
OTP_MAX_VERIFY_ATTEMPTS = 5
OTP_VERIFY_BLOCK_MINUTES = 15


class RequestOTPView(generics.GenericAPIView):
    serializer_class = RequestOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone_number']



        two_minutes_ago = timezone.now() - timedelta(minutes=OTP_REQUEST_COOLDOWN_MINUTES)
        if OTP.objects.filter(phone_number=phone, created_at__gte=two_minutes_ago).exists():
            return Response({"detail": "Please wait 2 minutes before requesting a new OTP."},
                            status=status.HTTP_429_TOO_MANY_REQUESTS)

        if settings.DEBUG:
            code = "123456"
        else:
            code = str(randbelow(900000) + 100000)


        OTP.objects.create(phone_number=phone, code=code)


        try:
            sms_result = send_sms(phone, code, test_mode=settings.DEBUG)
        except TypeError:
            sms_result = send_sms(phone, code)

        data = {"message": "OTP sent to the provided number."}
        if settings.DEBUG:
            data["debug_otp"] = code
            data["sms_result"] = sms_result

        return Response(data, status=status.HTTP_201_CREATED)


class VerifyOTPView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone_number']
        code = serializer.validated_data['code']

        block_key = f"otp_block_{phone}"
        if cache.get(block_key):
            return Response({"error": "Too many failed attempts. Try again later."},
                            status=status.HTTP_429_TOO_MANY_REQUESTS)

        try:
            otp = OTP.objects.filter(phone_number=phone, code=code).latest("created_at")

        except OTP.DoesNotExist:
            fail_key = f"otp_fail_{phone}"
            fails = cache.get(fail_key, 0) + 1
            cache.set(fail_key, fails, timeout=OTP_VERIFY_BLOCK_MINUTES * 60)
            if fails >= OTP_MAX_VERIFY_ATTEMPTS:
                cache.set(block_key, True, timeout=OTP_VERIFY_BLOCK_MINUTES * 60)
                cache.delete(fail_key)
                return Response({"error": "Too many failed attempts. Try again later."},status=status.HTTP_429_TOO_MANY_REQUESTS)
            return Response({"error": "Invalid code"}, status=status.HTTP_400_BAD_REQUEST)


        if timezone.now() > otp.created_at + timedelta(minutes=OTP_EXPIRY_MINUTES):
            return Response({"error": "Code expired"}, status=status.HTTP_400_BAD_REQUEST)


        OTP.objects.filter(phone_number=phone).delete()


        with transaction.atomic():
            user, created = User.objects.get_or_create(phone_number=phone)
            refresh = RefreshToken.for_user(user)
            access = str(refresh.access_token)
            refresh_token = str(refresh)

        return Response({
            "refresh": refresh_token,
            "access": access,
            "message": "Login successful"
        }, status=status.HTTP_200_OK)


class AddressListCreateView(generics.ListCreateAPIView):
    serializer_class = UserAddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AddressRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserAddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user)


class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data["refresh"]
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
