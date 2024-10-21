from django.contrib import admin
from shop.models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'brand', 'price',
                    'is_available', 'create_at', 'update_at')
    ordering = ['title']
    list_filter = ['is_available', 'create_at']
    prepopulated_fields = {'slug': ('title',)}

