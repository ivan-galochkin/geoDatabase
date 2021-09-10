FROM python:3.9-slim-buster
COPY . /usr/src/geo_database
WORKDIR /usr/src/geo_database
RUN pip3 install -r requirements.txt
ARG SECRET_KEY
ARG JWT_SECRET
ARG POSTGRES_PASSWORD
ARG POSTGRES_DB
ARG DB_HOST
ARG DB_PORT
ARG POSTGRES_USER
EXPOSE 8000
CMD ["python3", "auth.py"]
