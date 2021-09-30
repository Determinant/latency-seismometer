#!/bin/bash -e
profile=mine
AWS_REGIONS="$(aws ec2 --profile ${profile} --region us-west-1 describe-regions --query 'Regions[].RegionName' --output text)"
for region in ${AWS_REGIONS}; do
    aws ec2 --profile "${profile}" --region "$region" describe-instances --filters Name=instance-state-name,Values=running --query 'Reservations[*].Instances[*].{Ip1:PublicIpAddress}' --output text
done > ips.txt

python ./gen_inventory.py > nodes.ini
