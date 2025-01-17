from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
import uuid
from .models import Product
from .tasks import process_images

@csrf_exempt
def upload_csv(request):
    print(request.FILES)
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        
        try:
            df = pd.read_csv(file)
            if not all(col in df.columns for col in ['Serial Number', 'Product Name', 'Input Image Urls']):
                return JsonResponse({"error": "Invalid CSV format"}, status=400)

            request_id = str(uuid.uuid4())
            for _, row in df.iterrows():
                if pd.notnull(row['Serial Number']) and pd.notnull(row['Product Name'])  and pd.notnull(row['Input Image Urls']) :
                    print(row['Serial Number'],row['Product Name'])
                    product = Product(
                        request_id=request_id,
                        serial_number=row['Serial Number'],
                        product_name=row['Product Name'],
                        input_image_urls=row['Input Image Urls'],
                        status='Pending'
                    )
                    product.save()

            # Asynchronously process the images
            print("process started")
            process_images.apply_async(args=[request_id])
            print("process dont know")
            return JsonResponse({"request_id": request_id}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

def check_status(request, request_id):
    try:
        products = Product.objects.filter(request_id=request_id)
        if not products:
            return JsonResponse({"error": "Request ID not found"}, status=404)

        status = 'Completed' if all(p.status == 'Completed' for p in products) else 'In Progress'
        
        result = [{
            "serial_number": p.serial_number,
            "product_name": p.product_name,
            "input_image_urls": p.input_image_urls,
            "output_image_urls": p.output_image_urls
        } for p in products]

        return JsonResponse({"status": status, "processed_data": result}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
