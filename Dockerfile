FROM python:3.9-slim-buster
CMD ["ls -a"]
COPY . /usr/src/geo_database
WORKDIR /usr/src/geo_database
CMD ["ls -a"]
RUN pip3 install -r requirements.txt
EXPOSE 8000
CMD ["/usr/src/geo_database/auth.py"]
