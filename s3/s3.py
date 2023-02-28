import boto3
from botocore.exceptions import ClientError
import logging
import os
import dotenv


dotenv.load_dotenv(override=True)  # use .env file

AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
BUCKET_NAME = os.environ.get('AWS_BUCKET_NAME')


def get_client():
    return boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY,
                        aws_secret_access_key=AWS_SECRET_KEY)


def upload_to_s3(s3_client, file_name, bucket, object_name=None):
    """
    :param s3_client: Boto s3 client
    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    try:
        response = s3_client.upload_fileobj(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


if __name__ == "__main__":
    s3 = get_client()
    upload_to_s3(s3, "./test.parquet", BUCKET_NAME)
