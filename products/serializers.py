from rest_framework import serializers
from .models import Category, Tag, Product, ProductImage, Collection, Event

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug')

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'alt_text', 'order', 'is_main')
        read_only_fields = ('id',)

class ProductListSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()
    price_range = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'slug', 'name', 'short_description', 'thumbnail', 'price_range', 'is_featured', 'category', 'tags')

    def get_thumbnail(self, obj):
        img = obj.images.order_by('order').first()
        return img.image.url if img else None

    def get_price_range(self, obj):
        low, high = obj.get_price_range()
        return {'min': low, 'max': high}

class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ('id','slug','name','short_description','description','category','tags',
                  'base_price','price_range','images','is_featured','metadata')
        read_only_fields = ('id','slug')

    price_range = serializers.SerializerMethodField()
    def get_price_range(self, obj):
        low, high = obj.get_price_range()
        return {'min': low, 'max': high}

class CollectionSerializer(serializers.ModelSerializer):
    teaser = serializers.SerializerMethodField()
    product_count = serializers.IntegerField(source='products.count', read_only=True)

    class Meta:
        model = Collection
        fields = ('id','slug','title','short_description','teaser','product_count','start_at','end_at','is_active')

    def get_teaser(self, obj):
        return obj.teaser_image.url if obj.teaser_image else None

class EventSerializer(serializers.ModelSerializer):
    collections = CollectionSerializer(many=True, read_only=True)
    products = ProductListSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = ('id','slug','title','description','banner','start_at','end_at','is_featured','collections','products')