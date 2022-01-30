from django.contrib import admin

from products.models import Product, WebHook


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'is_active', 'created_at', 'updated_at']
    

@admin.register(WebHook)
class WebHookAdmin(admin.ModelAdmin):
    list_display = ['name', 'action', 'url', 'http_method', 'created_at',]
    
