FROM ubuntu:16.04
MAINTAINER CodaLab Worksheets <codalab.worksheets@gmail.com>

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y software-properties-common && add-apt-repository ppa:deadsnakes/ppa

RUN apt-get update; apt-get install -y \
    build-essential \
    curl \
    git \
    libfuse-dev \
    libjpeg-dev \
    libmysqlclient-dev \
    libssl-dev \
    mysql-client \
    python3.6 \
    python3.6-dev \
    python3-pip \
    python-virtualenv \
    python3-software-properties \
    zip;
 
# Set Python3.6 as the default python3 version
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 1

### Without this Python thinks we're ASCII and unicode chars fail
ENV LANG C.UTF-8

RUN python3 -m pip install --upgrade pip
RUN mkdir /opt/codalab-worksheets
WORKDIR /opt/codalab-worksheets

# Install dependencies
COPY docker/compose_files/files/wait-for-it.sh /opt/wait-for-it.sh
RUN chmod a+rx /opt/wait-for-it.sh
COPY requirements.txt requirements.txt
COPY requirements.docs.txt requirements.docs.txt
COPY requirements-server.txt requirements-server.txt
RUN python3 -m pip install -r requirements-server.txt

# Install code
COPY dockerfile ./

RUN python3 -m pip install -e .

# Allow non-root to read everything
RUN chmod -R og=u-w .

EXPOSE 2900
