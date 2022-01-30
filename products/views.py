import csv, codecs, json, time
from datetime import timedelta

from django.views import generic
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import StreamingHttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone

from products.models import Product, WebHook
from products.forms import ProductForm, WebHookForm
from products.tasks import process_task


class IndexView(generic.TemplateView):
    template_name = 'products/index.html'


class ProductCreateView(generic.CreateView):
    model = Product
    template_name = 'products/product_create.html'
    form_class = ProductForm
    success_url = '/products'

    def get_success_url(self):
        messages.success(self.request, 'Product added successfully', extra_tags='alert')
        return super().get_success_url()


class ProductListView(generic.ListView):
    queryset = Product.objects.order_by('-created_at')
    context_object_name = 'products'
    template_name = 'products/product_list.html'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        active = self.request.GET.get('active')
        
        if q:
            queryset = queryset.filter(Q(name__iexact=q) | Q(description__icontains=q) | Q(sku__icontains=q))
        if active:
            is_active = True if active == 'true' else False
            queryset = queryset.filter(is_active=is_active)

        return queryset

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        queryset = self.get_queryset()

        paginator = Paginator(queryset, self.paginate_by) 
        page = self.request.GET.get('page')
        try:
            queryset = paginator.page(page)
        except PageNotAnInteger:
            # if page is not an intger deliver the first page
            queryset = paginator.page(1)
        except EmptyPage:
            #  if page is out of range deliver last page of results
            queryset = paginator.page(paginator.num_pages)
        context['products'] = queryset

        return context


class ProductUpdateView(generic.UpdateView):
    model = Product
    form_class = ProductForm
    success_url = '/products'
    template_name = 'products/product_update.html'

    def get_success_url(self):
        messages.success(self.request, 'Product updated successfully', extra_tags='alert')
        return super().get_success_url()


def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, 'Product deleted successfully!', extra_tags='alert')
    return redirect('product_list')


def delete_all(request):
    # Make async?
    Product.objects.all().delete()
    messages.success(request, 'All products deleted successfully!', extra_tags='alert')
    return redirect('product_list')


def products_bulk_upload(request):

    if request.method == 'GET':
        return render(request, 'products/products_bulk_upload.html',)

    csv_file = request.FILES.get('file')
    reader = csv.reader(codecs.iterdecode(csv_file, 'utf-8'))
    next(reader)
    reader_list = list(reader)[:500]
    process_task.delay(reader_list)
      
    messages.success(request, 'Products upload in progress!', extra_tags='alert')

    return redirect('products_bulk_upload')


def stream_response(request):

    def event_stream():
        
        initial_data = ""
        while True:
            
            last_second =  timezone.now() - timedelta(seconds=5)

            data = json.dumps(list(Product.objects.filter(updated_at__gte=last_second).values("name", 
                    "sku", "is_active", "created_at")),
                    cls = DjangoJSONEncoder
                )

            if not initial_data == data:
                yield "\ndata: {}\n\n".format(data) 
                initial_data = data
                
            time.sleep(0.4)
        

    return StreamingHttpResponse(event_stream(), content_type="text/event-stream")


class WebHookListView(generic.ListView):
    queryset = WebHook.objects.order_by('-created_at')
    context_object_name = 'webhooks'
    template_name = 'products/webhook_list.html'
    paginate_by = 20


    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        queryset = self.get_queryset()

        paginator = Paginator(queryset, self.paginate_by) 
        page = self.request.GET.get('page')
        try:
            queryset = paginator.page(page)
        except PageNotAnInteger:
            # if page is not an intger deliver the first page
            queryset = paginator.page(1)
        except EmptyPage:
            #  if page is out of range deliver last page of results
            queryset = paginator.page(paginator.num_pages)
        context['webhooks'] = queryset

        return context

    def get_queryset(self):
            queryset = super().get_queryset()
            q = self.request.GET.get('q')
            
            if q:
                queryset = queryset.filter(name__icontains=q)

            return queryset


def webhook_delete(request, pk):
    webhook = get_object_or_404(WebHook, pk=pk)
    webhook.delete()
    messages.success(request, 'Webhook deleted successfully!', extra_tags='alert')
    return redirect('webhook_list')


class WebHookCreateView(generic.CreateView):
    model = WebHook
    template_name = 'products/webhook_create.html'
    form_class = WebHookForm
    success_url = '/webhooks'

    def get_success_url(self):
        messages.success(self.request, 'Webhook added successfully', extra_tags='alert')
        return super().get_success_url()
