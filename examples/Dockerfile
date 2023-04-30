FROM python:3.10
WORKDIR /app
COPY ./examples .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 8443 8080
CMD [ "python", "./example.py" ]
