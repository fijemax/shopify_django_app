from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='root_path'),
    path('create_product', views.create_product, name='shop_create_product'),
    path('create_webhook', views.create_webhook, name='shop_create_webhook'),
    path('destroy_webhook', views.destroy_webhook, name='shop_destroy_webhook'),
    path('logs_webhook', views.logs_webhook, name='shop_logs_webhook'),
]
