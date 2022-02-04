import csv, codecs, json, time
from datetime import timedelta
from zipfile import ZipFile

from django.views import generic
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import StreamingHttpResponse, JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

import boto3

from products.models import Product, WebHook
from products.signals import custom_post_save
from products.forms import ProductForm, WebHookForm
from products.tasks import process_task


class IndexView(generic.TemplateView):
    template_name = 'products/index.html'


def product_create_view(request):
    template_name = 'products/product_create.html'
    form = ProductForm(request.POST)

    if form.is_valid():
        obj = form.save()
        custom_post_save.send(sender=Product, instance=obj, created=True)
        messages.success(request, 'Product added successfully', extra_tags='alert')

        return redirect('product_list')
    return render(request, template_name, {'form': form})


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
        custom_post_save.send(sender=self.model, instance=self.get_object(), created=False)
        messages.success(self.request, 'Product updated successfully', extra_tags='alert')
        return super().get_success_url()


def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, 'Product deleted successfully!', extra_tags='alert')
    return redirect('product_list')


def delete_all(request):
    Product.objects.all().delete()
    messages.success(request, 'All products deleted successfully!', extra_tags='alert')
    return redirect('product_list')

def handle_uploaded_file(f):
    # write files in chunks
    with open(f.name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

        # extract zip file
        ZipFile(destination).extractall("/tmp")
        file_name = destination.name.split('.')[0] + '.csv'

    # process file and send to celery
    file_path = f"/tmp/{file_name}"
    with open(file_path, "r") as new_file:
        reader = csv.reader(new_file)
        next(reader)
        reader_list = list(reader)
        process_task.delay(reader_list)


@csrf_exempt
def products_bulk_upload(request):

    if request.method == 'GET':
        return render(request, 'products/products_bulk_upload.html',)

    #Usage: Upload zip with Ajax, extract and read
    # print('is_ajax', request.is_ajax())

    # ajx_file = request.FILES.get('file')
    # handle_uploaded_file(ajx_file)

    # return JsonResponse({'msg':'<span style="color: white;">Products upload in progress!</span>'})
   
    #Usage: upload zip, extract and then read
    # django_file = request.FILES.get('file')
    # ZipFile(django_file).extractall("/tmp")
    # file_name = django_file.name.split('.')[0] + '.csv'

    # file_path = f"/tmp/{file_name}"
    # with open(file_path, "r") as f:
    #     reader = csv.reader(f)
    #     next(reader)
    #     reader_list = list(reader)
    #     process_task.delay(reader_list)

    # Usage: upload csv and read
    # csv_file = request.FILES.get('file')
    # reader = csv.reader(codecs.iterdecode(csv_file, 'utf-8'))
    # next(reader)
    # reader_list = list(reader)
    # process_task.delay(reader_list)
      
    # messages.success(request, 'Products upload in progress!', extra_tags='alert')

    # return redirect('products_bulk_upload')


def stream_response(request):

    def event_stream():
        
        initial_data = ""
        while True:
            
            last_minute =  timezone.now() - timedelta(minutes=1)

            data = json.dumps(list(Product.objects.filter(updated_at__gte=last_minute).values("name", 
                    "sku", "is_active", "created_at")),
                    cls = DjangoJSONEncoder
                )

            if not initial_data == data:
                yield "\ndata: {}\n\n".format(data) 
                initial_data = data
                
            # time.sleep(0.4)
        

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


def get_uploaded_file(request):

    # Usage: Uploaded file url (Using AWS)
    file_name = request.GET.get('file_name')
    print('file_name:', file_name)

    client = boto3.client('s3',
                aws_access_key_id=settings.AWS_ACCESS_KEY, 
                aws_secret_access_key=settings.AWS_SECRET_KEY,
        )

    file_path = '/tmp/' + file_name

    # Download zipped file and store on `/tmp/`
    print("Downloading the csv file...")
    key = f"{settings.AWS_S3_BUCKET}/{file_name}"
    client.download_file(settings.AWS_S3_BUCKET, key, file_path)

    # zipped_file = request.FILES.get('file')
    ZipFile(file_path).extractall("/tmp")

    unzipped_file = '/tmp/' + file_name.split('.')[0] + '.csv'
    print('unzipped_file:', unzipped_file)

    # read downloaded file
    with open(unzipped_file, "r") as f:
        reader = csv.reader(f)
        next(reader)
        reader_list = list(reader)
        process_task.delay(reader_list)

        # count = len(reader_list)
        # step = 2000
    
        # for i in range(0, count, step):
        #     chunks = reader_list[i:i+step]
        #     # print(chunks)
        #     process_task.delay(chunks)
        #     time.sleep(50)
        # # process_task(reader_list)

    return JsonResponse({'msg': 'Processing your CSV file'})