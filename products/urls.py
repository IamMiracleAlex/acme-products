from django.urls import path

from . import views


urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('create/', views.ProductCreateView.as_view(), name='product_create'),
    path('update/<int:pk>/', views.ProductUpdateView.as_view(), name='product_update'),
    path('delete/<int:pk>/', views.product_delete, name='product_delete'),
    path('delete-all/', views.delete_all, name='product_delete_all'),
    path('bulk-upload/', views.products_bulk_upload, name='products_bulk_upload'),
    path('stream/', views.stream_response, name='stream_response'),

]