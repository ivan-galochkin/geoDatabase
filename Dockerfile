FROM python:3.9-slim-buster
COPY . /usr/src/geo_database
WORKDIR /usr/src/geo_database
RUN pip3 install -r requirements.txt
ARG SECRET_KEY
ARG JWT_SECRET
ARG db_password
ARG DATABASE_URL
EXPOSE 8000
CMD ["python3", "auth.py"]
