from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .models import OTP, UserAddress
from .serializers import *
from .utils import send_sms
from datetime import timedelta
from django.utils import timezone
import random

User = get_user_model()

# ---------------------------
# OTP Views
# ---------------------------
class RequestOTPView(generics.GenericAPIView):
    serializer_class = RequestOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone_number']

        # جلوگیری از اسپم: فقط هر 2 دقیقه یکبار

        two_minutes_ago = timezone.now() - timedelta(minutes=0)
        if OTP.objects.filter(phone_number=phone, created_at__gte=two_minutes_ago).exists():
            return Response({"detail": "Please wait 2 minutes before requesting a new OTP."},
                            status=status.HTTP_429_TOO_MANY_REQUESTS)

        # code = str(random.randint(1000, 9999))
        code = "1234"


        OTP.objects.create(phone_number=phone, code=code)
        # send_sms(phone, code)

        return Response({"message": f"OTP sent to {phone}"}, status=status.HTTP_200_OK)


class VerifyOTPView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone_number']
        code = serializer.validated_data['code']

        try:
            otp = OTP.objects.filter(phone_number=phone, code=code).latest("created_at")
        except OTP.DoesNotExist:
            return Response({"error": "Invalid code"}, status=status.HTTP_400_BAD_REQUEST)

        if not otp.is_valid():
            return Response({"error": "Code expired"}, status=status.HTTP_400_BAD_REQUEST)

        # ایجاد کاربر جدید در صورت عدم وجود
        user, created = User.objects.get_or_create(phone_number=phone)
        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "message": "Login successful"
        }, status=status.HTTP_200_OK)


# ---------------------------
# User Address Views
# ---------------------------
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
        except Exception as e:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
