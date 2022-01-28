from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=200)
    # sku = models.CharField(max_length=200, unique=True)
    sku = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)