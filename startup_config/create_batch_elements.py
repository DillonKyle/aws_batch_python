import boto3
from botocore.exceptions import ClientError

session = boto3.Session(profile_name='admin')
iam = session.client('iam')
client = session.client('batch')

compute_env_name = 'pht_process_environment'
job_queue_name = 'pht_process_queue'
job_def_name = 'pht_process_job_definition'

def cce():
    response = client.create_compute_environment(
        computeEnvironmentName=compute_env_name,
        type='MANAGED',
        state='ENABLED',
        computeResources={
            'type': 'EC2',
            'allocationStrategy': 'BEST_FIT',
            'minvCpus': 0,
            'maxvCpus': 256,
            'subnets': [
                'subnet-b0d542fc',
                'subnet-133dcb78',
                'subnet-eaaa8690',
            ],
            'instanceRole': 'ecsInstanceRole',
            'securityGroupIds': [
                'sg-7812dd1e',
            ],
            'instanceTypes': [
                'optimal',
            ]
        }
    )
    print("Created Compute Environment: " + str(response))
    

def cjq():
    while True:
        try:
            response = client.create_job_queue(
                jobQueueName=job_queue_name,
                state='ENABLED',
                priority=1,
                computeEnvironmentOrder=[
                    {
                        'order': 100,
                        'computeEnvironment': compute_env_name
                    },
                ],
            )
            print("Created Job Queue: " + str(response))
        except ClientError:
            print("Waiting for Compute Environment to Establish...")
        else:
            break

def rjq():
    phtProcessRole = iam.get_role(RoleName='phtProcessRole')

    while True:
        try:
            response = client.register_job_definition(
                jobDefinitionName=job_def_name,
                type='container',
                containerProperties={
                    'image': 'dillonkyle/pht_aws:latest',
                    'memory': 256,
                    'vcpus': 16,
                    'jobRoleArn': phtProcessRole['Role']['Arn'],
                    'executionRoleArn': phtProcessRole['Role']['Arn'],
                    'environment': [
                        {
                            'name': 'AWS_DEFAULT_REGION',
                            'value': 'us-east-2',
                        }
                    ]
                },
            )
            print("Registered Job Queue: " + str(response))
        except ClientError:
            print("Waiting for Job Queue to Establish...")
        else:
            break

def configure_resources():
    print("Configuring Resources...")
    cce()
    cjq()
    rjq()
    print("Resources Configured in AWS Batch.")

def delete_resources():
    client.deregister_job_definition(
        jobDefinition=job_def_name,
    )

    client.update_job_queue(
        jobQueue=job_queue_name,
        state='DISABLED',
    )
    while True:
        try:
            client.delete_job_queue(
                jobQueue=job_queue_name,
            )
        except ClientError:
            print("Disabling Job Queue...")
        else:
            client.update_compute_environment(
                    computeEnvironment=compute_env_name,
                    state='DISABLED',
                )
            break

    while True:
        try:
            client.delete_compute_environment(
                computeEnvironment=compute_env_name,
            )
        except ClientError:
            print("Disabling Compute Environment...")
        else:
            print("Resources Deleted")
            break

# configure_resources()
delete_resources()