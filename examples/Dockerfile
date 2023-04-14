# set base image (host OS)

FROM python:3.10

# set the working directory in the container
WORKDIR /app

# install dependencies
RUN pip install dxsp
RUN pip install healthchecks_io

# copy the content of the local src directory to the working directory
COPY ./examples .

# command to run on container start
CMD [ "python", "./example.py" ]
