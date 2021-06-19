FROM python:3.6
WORKDIR /code

# install GDAL
RUN apt-get update
RUN apt-get install -y binutils libgdal-dev gdal-bin
RUN apt-get install -y python3-opencv

# intall requirements
COPY requirements.txt /code/
RUN python3 -m pip install -r requirements.txt

ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

RUN python3 -m pip install -I GDAL==2.4.2

COPY . /code/