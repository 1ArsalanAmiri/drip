from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from rest_framework_nested import routers


router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'collections', CollectionViewSet, basename='collection')
router.register(r'events', EventViewSet, basename='event')

urlpatterns = [
    path('', include(router.urls)),
]
