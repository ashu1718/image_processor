import requests
from PIL import Image
from io import BytesIO
import os
from django.conf import settings
from .models import Product

"""
function takes single arg request_id and process all the request associated with it.
"""
def process_images(request_id):
    
    products = Product.objects.filter(request_id=request_id, status='Pending').only(
        'product_name', 'input_image_urls'
    )

    processed_path = os.path.join(settings.MEDIA_ROOT, "processed")
    if not os.path.exists(processed_path):
        os.makedirs(processed_path, exist_ok=True)
        os.chmod(processed_path, 0o775)

    for product in products:
        try:
            input_urls = product.input_image_urls.split(',')
            output_urls = []

            for url in input_urls:
                try:
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()

                    img = Image.open(BytesIO(response.content))
                    img = img.resize((int(img.width * 0.5), int(img.height * 0.5)))

                    output_image_path = os.path.join(processed_path, os.path.basename(url))
                    img.save(output_image_path)
                    output_urls.append(output_image_path)

                except Exception as e:
                    print("Error processing URL", url, e)

            product.output_image_urls = ','.join(output_urls)
            product.status = 'Completed'
            product.save()

        except Exception as e:
            product.status = 'Failed'
            product.save()
            print("Error processing product: ", product.product_name, e)
