from django.urls import path
from .views import *

urlpatterns = [
    path('request-otp/', RequestOTPView.as_view(), name='request-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('addresses/', AddressListCreateView.as_view(), name='address-list-create'),
    path('addresses/<int:pk>/', AddressRetrieveUpdateDestroyView.as_view(), name='address-detail'), # GET_PUT_PATCH_DELETE
    path('login/', RequestOTPView.as_view(), name='request-otp'),
    path('logout/', LogoutView.as_view(), name="logout"),
]
