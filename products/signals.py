import django.dispatch

custom_post_save = django.dispatch.Signal(providing_args=['sender', 'instance', 'created',])
