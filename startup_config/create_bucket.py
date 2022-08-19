import boto3 

s3 = boto3.resource('s3')

response = s3.create_bucket(
    Bucket='pht-data',
    CreateBucketConfiguration={
        'LocationConstraint': 'us-east-2'
    }
)

print(response)