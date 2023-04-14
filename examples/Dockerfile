# set base image (host OS)

FROM python:3.10

# set the working directory in the container
WORKDIR /app

# install dependencies
RUN pip install dxsp
RUN pip install healthchecks_io
RUN pip install fastapi
RUN pip uvicorn

# copy the content of the local src directory to the working directory
COPY ./examples .

EXPOSE 8443 8080
# command to run on container start
CMD [ "python", "./example.py" ]
