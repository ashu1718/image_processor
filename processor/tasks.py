from celery import shared_task
import requests
from PIL import Image
from io import BytesIO
import os
from django.conf import settings
from .models import Product
from urllib.parse import urlparse

import re
import logging
logger = logging.getLogger(__name__)



def get_valid_filename(filename):
    """
    Converts a string to a valid filename by removing invalid characters
    and trimming any leading/trailing whitespace.
    """
    filename = filename.strip().replace(" ", "_")  # Replace spaces with underscores
    return re.sub(r"[^a-zA-Z0-9._-]", "", filename)  # Remove invalid characters

def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


@shared_task()
def process_images(request_id):
    logger.info("Task started for request_id: %s", request_id)
    print("Task started for request_id: %s", request_id)
    products = Product.objects.filter(request_id=request_id, status='Pending').only(
        'product_name', 'input_image_urls'
    )

    processed_path = os.path.join(settings.MEDIA_ROOT, "processed")
    if not os.path.exists(processed_path):
        os.makedirs(processed_path, exist_ok=True)
        os.chmod(processed_path, 0o775)

    for product in products:
        try:
            logger.info("Processing product: %s", product.product_name)
            input_urls = product.input_image_urls.split(',')
            output_urls = []

            for url in input_urls:
                if not is_valid_url(url):
                    logger.warning("Invalid URL: %s", url)
                    continue

                try:
                    logger.info("Downloading image from URL: %s", url)
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()

                    img = Image.open(BytesIO(response.content))
                    img = img.resize((int(img.width * 0.5), int(img.height * 0.5)))

                    output_filename = get_valid_filename(os.path.basename(url))
                    output_image_path = os.path.join(processed_path, output_filename)
                    img.save(output_image_path)
                    output_urls.append(output_image_path)

                except Exception as e:
                    logger.error("Error processing URL %s: %s", url, e)

            product.output_image_urls = ','.join(output_urls)
            product.status = 'Completed'
            product.save()
            logger.info("Product %s processed successfully", product.product_name)

        except Exception as e:
            product.status = 'Failed'
            product.save()
            logger.error("Error processing product %s: %s", product.product_name, e)
