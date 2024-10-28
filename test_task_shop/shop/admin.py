from django.contrib import admin
from shop.models import Category, Product


from django.contrib import admin
from .models import Product, Category


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the Product model.
    """
    list_display = ('title', 'brand', 'price', "discount", 'is_available', 'create_at', 'update_at')
    ordering = ['title']
    list_filter = ['is_available', 'create_at']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the Category model.
    """
    list_display = ['name', 'parent']
    ordering = ['name']
    prepopulated_fields = {'slug': ('name',)}
