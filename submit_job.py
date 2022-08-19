import boto3

session = boto3.Session(profile_name='admin')
client = session.client('batch')

response = client.submit_job(
    jobDefinition='pht_process_job_definition',
    jobName='pht_process_job1',
    jobQueue='pht_process_queue',
    containerOverrides={
        'environment': [
            {
                'name': 'bucket_name',
                'value': 'pht-data',
            },
            {
                'name': 'piles-key',
                'value': 'piles.csv',
            },
            {
                'name': 'loops-key',
                'value': 'loops.csv',
            }
        ]
    },
)

print(response)