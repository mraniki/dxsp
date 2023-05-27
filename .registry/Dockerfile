FROM python:3.10
WORKDIR /app
COPY ./examples .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8080
CMD [ "python", "./example.py" ]
