from rest_framework import viewsets, mixins, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import *
from .serializers import *
from .filters import ProductFilter
from .pagination import StandardResultsSetPagination
from .permissions import IsStaffOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response

# Category & Tag: simple read endpoints
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    pagination_class = None

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None

# Product: list + retrieve + admin write via permission
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.prefetch_related('images','tags','category').all()
    permission_classes = (IsStaffOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_class = ProductFilter
    search_fields = ('name','short_description','description')
    ordering_fields = ('base_price','created_at','is_featured','name')
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer

# Collections
class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Collection.objects.prefetch_related('products').all()
    serializer_class = CollectionSerializer
    permission_classes = (IsStaffOrReadOnly,)
    lookup_field = 'slug'

# Events (Drops)
class EventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Event.objects.prefetch_related('collections').all()
    serializer_class = EventSerializer
    lookup_field = 'slug'


