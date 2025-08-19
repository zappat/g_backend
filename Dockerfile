FROM python:3.9-slim-bullseye

LABEL maintainer="Gear connect"

ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libproj-dev \
    proj-bin \
    graphviz \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./startup.sh /startup.sh
COPY ./app /app
WORKDIR /app
EXPOSE 8000

ARG DEV=false
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip setuptools==57.5.0 wheel && \
    /py/bin/pip install --no-cache-dir --default-timeout=300 --retries=15 -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp

# Make startup script executable before switching user
RUN chmod +x /startup.sh

# Create the user and switch to it
RUN groupadd -r admin-user && useradd -r -g admin-user admin-user

USER admin-user

ENV PATH="/py/bin:$PATH"

CMD ["/startup.sh"]