#Deriving the latest base image
FROM python:3.9


#Labels as key value pair
LABEL Maintainer="dillonkyle"

RUN pip install pandas boto3
# Any working directory can be chosen as per choice like '/' or '/home' etc
# i have chosen /usr/app/src
WORKDIR /usr/app/src

#to COPY the remote file at working directory in container
COPY barebones_pht.py ./
# Now the structure looks like this '/usr/app/src/test.py'


#CMD instruction should be used to run the software
#contained by your image, along with any arguments.

ENTRYPOINT [ "python", "./barebones_pht.py"]