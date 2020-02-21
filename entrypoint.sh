#!/bin/sh
cd $WORKDIR
if $AWS_CLI; then
    aws configure set aws_access_key_id $AWS_ACCESS_KEY_ID
    aws configure set aws_secret_access_key $AWS_SECRET_ACCESS_KEY
    aws configure set default.region $AWS_DEFAULT_REGION
    aws eks --region $AWS_DEFAULT_REGION update-kubeconfig --name production
fi

python -m bothub_nlp_nlu_worker_on_demand
