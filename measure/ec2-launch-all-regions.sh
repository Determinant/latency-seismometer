#!/bin/bash -e
profile=mine
AWS_REGIONS="$(aws ec2 --profile ${profile} --region us-west-1 describe-regions --query 'Regions[].RegionName' --output text)"
#AWS_REGIONS="eu-south-1 eu-west-1 ap-northeast-3 ap-northeast-2 ap-northeast-1 sa-east-1 ca-central-1 ap-east-1 ap-southeast-1 ap-southeast-2 eu-central-1 us-east-1 us-east-2 us-west-1 us-west-2"

for region in ${AWS_REGIONS}; do
    ami="$(aws ec2 --profile ${profile} --region $region describe-images \
        --owners 099720109477 \
        --filters Name=root-device-type,Values=ebs \
        Name=architecture,Values=x86_64 \
        Name=name,Values='ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*' \
        --query 'Images[*].[ImageId,CreationDate]' --output text \
        | sort -k2 -r \
        | head -n1 \
        | awk '{ print $1 }')"
    echo "$region: $ami"
    aws ec2 --profile "${profile}" --region "$region" run-instances --image-id "$ami" --instance-type t3.micro --security-groups allow-icmp --key-name ted-key
done
