from django.contrib import admin
from .models import Category, Tag, Product, ProductImage, Collection, Event

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0
    fields = ('image','alt_text','order','is_main')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id','name','slug','base_price','is_featured','status','created_at')
    search_fields = ('name','slug')
    list_filter = ('status','is_featured','category')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('id','title','is_active','start_at','end_at')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('products',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id','title','start_at','end_at','is_featured')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('collections','products')
