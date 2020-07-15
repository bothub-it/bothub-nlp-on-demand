FROM python:3.6-alpine

ENV WORKDIR /root/app
ENV BOTHUB_NLP_WORKER_ON_DEMAND_API_PORT 2658

WORKDIR $WORKDIR

COPY . .

RUN apk update \
    && apk add --virtual .build-dependencies --no-cache \
        alpine-sdk \
        git \
        python3-dev \
    && pip install --upgrade pip \
    && pip install -U pip setuptools \
    && pip install pipenv redis \
    && pipenv install --system --deploy

RUN pip install awscli
RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
RUN chmod +x ./kubectl
RUN mv ./kubectl /usr/local/bin

RUN apk del .build-dependencies && rm -rf /var/cache/apk/*

RUN chmod +x ./entrypoint.sh
ENTRYPOINT [ "./entrypoint.sh" ]
