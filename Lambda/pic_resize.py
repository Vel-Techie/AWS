import boto3
from PIL import Image
import io
import os

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Get bucket and object key from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    # Only proceed if the image is in the "original/" folder
    if not key.startswith("original/"):
        print("Not in original folder, skipping...")
        return

    # Download image from S3
    response = s3.get_object(Bucket=bucket, Key=key)
    image_content = response['Body'].read()

    # Open image using PIL
    image = Image.open(io.BytesIO(image_content))
    image.thumbnail((100, 100))  # Resize to thumbnail (max 100x100)

    # Save resized image to bytes buffer
    buffer = io.BytesIO()
    image_format = image.format if image.format else 'JPEG'
    image.save(buffer, format=image_format)
    buffer.seek(0)

    # Define new key for the thumbnail
    thumbnail_key = key.replace("original/", "thumbnails/", 1)

    # Upload thumbnail back to S3
    s3.put_object(Bucket=bucket, Key=thumbnail_key, Body=buffer, ContentType=response['ContentType'])

    return {
        'statusCode': 200,
        'body': f'Thumbnail saved to {thumbnail_key}'
    }
