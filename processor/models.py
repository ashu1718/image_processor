from django.db import models


class Product(models.Model):
    request_id = models.CharField(max_length=255)
    serial_number = models.CharField(max_length=50)
    product_name = models.CharField(max_length=255)
    input_image_urls = models.TextField()
    output_image_urls = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=50, default='Pending')

    def __str__(self):
        return f'Product {self.product_name}'

