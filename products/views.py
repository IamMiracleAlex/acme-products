from django.views import generic
from django.shortcuts import redirect
from django.contrib import messages

from products.models import Product
from products.forms import ProductForm


class IndexView(generic.TemplateView):
    template_name = 'products/index.html'


class ProductCreateView(generic.CreateView):
    model = Product
    template_name = 'products/product_create.html'
    form_class = ProductForm
    success_url = '/products'


class ProductListView(generic.ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'products/product_list.html'


class ProductUpdateView(generic.UpdateView):
    model = Product
    form_class = ProductForm
    success_url = '/products'
    template_name = 'products/product_update.html'


class ProductDeleteView(generic.DeleteView):
    model = Product


def delete_all(request):
    # Make async?
    # Product.objects.delete()
    messages.success(request, 'All products deleted successfully!', extra_tags='alert')

    return redirect('product_list')