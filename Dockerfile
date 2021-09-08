FROM python:3.9-slim-buster
WORKDIR /usr/src/geo_database
EXPOSE 8000
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . .
CMD ["/usr/src/geo_database/auth.py"]
