FROM python:3.9-slim-buster
WORKDIR /usr/src/geo_database
COPY . .
RUN pip3 install -r requirements.txt
EXPOSE 8000
CMD ["python3", "auth.py"]
