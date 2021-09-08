FROM python:3.9-slim-buster
COPY . /usr/src/geo_database
WORKDIR /usr/src/geo_database
RUN pip3 install -r requirements.txt
EXPOSE 8000
CMD ["python3", "auth.py"]
