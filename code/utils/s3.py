import boto3
import os
import dotenv
from botocore.client import Config
dotenv.load_dotenv()

def _get_s3_client() -> boto3.client:
    return boto3.client(
        service_name='s3',
        endpoint_url=os.getenv("AWS_ENDPOINT_URL"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
        config=Config(signature_version='s3v4'),
    )

def list_bucket_files(bucket_name: str, subpath: str) -> list:
    s3_client = _get_s3_client()
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=subpath)
    if 'Contents' in response:
        return [item['Key'] for item in response['Contents']]
    return []

