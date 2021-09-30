#!/bin/bash
profile=mine
AWS_REGIONS="$(aws ec2 --profile ${profile} --region us-west-1 describe-regions --query 'Regions[].RegionName' --output text)"
for region in ${AWS_REGIONS}; do
    aws ec2 --profile "${profile}" --region "$region" delete-security-group --group-name allow-icmp
    aws ec2 --profile "${profile}" --region "$region" create-security-group --group-name allow-icmp --description "Allow ICMP"
    aws ec2 --profile "${profile}" --region "$region" authorize-security-group-ingress --group-name allow-icmp --ip-permissions \
        IpProtocol=icmp,FromPort=-1,ToPort=-1,IpRanges='[{CidrIp=0.0.0.0/0}]' \
        IpProtocol=tcp,FromPort=22,ToPort=22,IpRanges='[{CidrIp=0.0.0.0/0}]'
done
