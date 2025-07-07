FROM python:3.9

LABEL maintainer="Gear connect"

ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-distutils \
    python3-setuptools \
    python3-pip \
    python3-venv \
    gdal-bin \
    libgdal-dev \
    libproj-dev \
    proj-bin \
    graphviz \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000

ARG DEV=false
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip setuptools==57.5.0 wheel && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp

# Create the user and switch to it
RUN groupadd -r admin-user && useradd -r -g admin-user admin-user

USER admin-user

ENV PATH="/py/bin:$PATH"
