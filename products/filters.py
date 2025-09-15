import django_filters
from django.db.models import Q
from .models import Product

class ProductFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='search', label='search')
    min_price = django_filters.NumberFilter(field_name='base_price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='base_price', lookup_expr='lte')
    category = django_filters.NumberFilter(field_name='category__id')
    tag = django_filters.NumberFilter(method='filter_tag')
    is_featured = django_filters.BooleanFilter(field_name='is_featured')

    class Meta:
        model = Product
        fields = ['q', 'min_price', 'max_price', 'category', 'tag', 'is_featured']

    def search(self, queryset, name, value):
        return queryset.filter(Q(name__icontains=value) | Q(short_description__icontains=value) | Q(description__icontains=value))

    def filter_tag(self, queryset, name, value):
        return queryset.filter(tags__id=value)
