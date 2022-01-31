import random

from celery import shared_task

from products.models import Product

        


@shared_task(bind=True)
def process_task(self, reader_list, ):
    
    try:
        for row in reader_list:
            is_active = random.choice([True, False])

            print(row[0], row[1], is_active, row[2])
            product = Product.objects.filter(sku=row[1])
            if product:
                product.update(name=row[0], is_active=is_active, description=row[2])
            else:
                product = Product.objects.create(name=row[0], sku=row[1], is_active=is_active, description=row[2])

    except Exception as err:
        self.retry(countdown=3, max_retries=5, exc=err)

    return 'Succeeded'