from django.urls import path

from . import views


urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('create/', views.ProductCreateView.as_view(), name='product_create'),
    path('update/<int:pk>/', views.ProductUpdateView.as_view(), name='product_update'),
    path('delete/<int:pk>/', views.ProductDeleteView.as_view(), name='product_delete'),
    path('delete-all/', views.delete_all, name='product_delete_all'),

]