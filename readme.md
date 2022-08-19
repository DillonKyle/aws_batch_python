## Running the Pile Height Tool Through AWS Batch
---
This will allow you to build a docker image containing a python process, then create resources in AWS Batch that will allow you to push data from an S3 bucket through the docker image and export the results back into the S3 bucket.

You can specify the file names you want to pass through the docker image by changing the values in **"submit_job.py"**

1. Add pile data and loop data to S3 bucket as "piles.csv" and "loops.csv".

2. Build the Docker image using 

    `docker build -f Dockerfile -t [DockerUser]/pht_aws .`

3. Push image to dockerhub using

    `docker push [DockerUser]/pht_aws`

4. Create IAM Role by running **"startup_config/create_iam_user.py"**

5. Configure the AWS Batch resources by running **"startup_config/create_batch_elements.py"**

6. Process the job by running **"submit_job.py"**

The results will appear in the original S3 bucket as **"pile_heights.csv"**