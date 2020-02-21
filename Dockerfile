FROM python:3.6-alpine

ENV WORKDIR /root/app
ENV BOTHUB_NLP_WORKER_ON_DEMAND_API_PORT 2658
ENV AWS_CLI false
ENV AWS_ACCESS_KEY_ID null
ENV AWS_SECRET_ACCESS_KEY null
ENV AWS_DEFAULT_REGION null

WORKDIR $WORKDIR

COPY . .

RUN apk update \
    && apk add --virtual .build-dependencies --no-cache \
        alpine-sdk \
        git \
        python3-dev \
    && apk add --no-cache postgresql-dev \
    && pip install pipenv redis \
    && pipenv install --system --deploy

RUN pip install awscli
RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
RUN chmod +x ./kubectl
RUN mv ./kubectl /usr/local/bin

RUN apk del .build-dependencies && rm -rf /var/cache/apk/*

RUN chmod +x ./entrypoint.sh
ENTRYPOINT [ "./entrypoint.sh" ]
