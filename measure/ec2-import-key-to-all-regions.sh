#!/bin/bash -e
profile=mine
AWS_REGIONS="$(aws ec2 --profile ${profile} --region us-west-1 describe-regions --query 'Regions[].RegionName' --output text)"
for region in ${AWS_REGIONS}; do
    aws ec2 --profile "${profile}" import-key-pair --key-name ted-key --public-key-material fileb://./ted-oregon.pub --region "$region"
done
