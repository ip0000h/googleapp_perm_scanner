FROM python:3.7.2-slim

RUN apt-get update && apt-get install -qq -y --no-install-recommends \
    build-essential \
    libffi-dev \
&& apt-get purge -y --auto-remove \
    -o APT::AutoRemove::RecommendsImportant=false \
    -o APT::AutoRemove::SuggestsImportant=false $buildDeps \
&& apt-get clean \
&& rm -rf /var/lib/apt/lists/* \
&& easy_install pip

COPY ./requirements.txt requirements.txt

RUN pip install --upgrade pip \
&& pip install -U -r requirements.txt