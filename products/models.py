from django.db import models
from django.dispatch import receiver

import requests

from products.signals import custom_post_save

class Product(models.Model):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=200, unique=True)
    is_active = models.BooleanField(default=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def as_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'sku': self.sku,
            'is_active': self.is_active,
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }

class WebHook(models.Model):
    CREATE, UPDATE = 'Create', 'Update'
    POST, GET = 'POST', 'GET'
    ACTION_CHOICES = (
        (CREATE, CREATE),
        (UPDATE, UPDATE),
    )
    HTTP_METHOD_CHOICES = (
        (POST, POST),
        (GET, GET)
    )
    name = models.CharField(max_length=100)
    action = models.CharField(choices=ACTION_CHOICES, max_length=10)
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    http_method = models.CharField(choices=HTTP_METHOD_CHOICES, max_length=10)



# Call Webhook after product creation or update
@receiver(custom_post_save, sender=Product)
def call_webhooks(sender, instance, created, **kwargs):
    print(sender, instance, created)
    webhooks = WebHook.objects.all()
    if created:
        webhooks = WebHook.objects.filter(action=WebHook.CREATE)
        for webhook in webhooks:
            requests.request(
                method=webhook.http_method,
                url=webhook.url,
                data=instance.as_json()
            )
    else:
        webhooks = WebHook.objects.filter(action=WebHook.UPDATE)
        for webhook in webhooks:
            requests.request(
                method=webhook.http_method,
                url=webhook.url,
                data=instance.as_json(),
            )