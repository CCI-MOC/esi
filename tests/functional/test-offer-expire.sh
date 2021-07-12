#!/bin/bash

project_id=75681640118a4890b3da0d106eae8af7 # test1 uuid
tmpfile=$(mktemp ./leaseXXXXXX)
start=$(date +%Y-%m-%d)
end=$(date -d "+1 minute" +"%Y-%m-%d %H:%M:%S")

# Setup script, contains offer create test

./setup.sh "$tmpfile" "$project_id" "$start" "$end" "$resource_type"

. $tmpfile

# The uuid variable will be overwritten, so we save it here
test_offer_uuid=$uuid
# Run cleanup if the script exits, contains offer delete test
# Note: deletion will fail if handling of expired offers works
trap "./cleanup.sh $test_offer_uuid; rm -f $tmpfile $errfile $nodefile" EXIT

###################################
## OFFER LIST EXPIRED OFFER TEST ##
###################################

echo "OFFER LIST EXPIRED OFFER TEST"

sleep 2m
date +"%Y-%m-%D %H:%M:%S"

openstack --os-cloud test1-subproject esi offer list -f json > $tmpfile \
  || { ec=$?; echo "ERROR: failed to list offers" >&2; exit $ec; }
cat $tmpfile
jq -r ".[].UUID" $tmpfile | grep $uuid \
  && { ec=$?; echo "ERROR: expired offer is visible" >&2; exit $ec; }

echo "OFFER LIST EXPIRED OFFER TEST SUCCEEDED"

####################################
## OFFER CLAIM EXPIRED OFFER TEST ##
####################################

echo "OFFER CLAIM EXPIRED OFFER TEST"

openstack --os-cloud test1-subproject esi offer claim $test_offer_uuid -f shell > $tmpfile 2> $errfile
#openstack --os-cloud test1-subproject esi offer claim $test_offer_uuid -f shell
ec=$?
expected_error="Offer with name or uuid $test_offer_uuid not found."

if ! grep -q "$expected_error" $errfile; then
  if [[ $ec -eq 0 ]]; then
    echo "ERROR: succeeded claiming expired offer" >&2
  else
    echo "ERROR: unexpected error during claim expired offer test" >&2
    cat $errfile >&2
  fi
  exit 1
fi

echo "OFFER CLAIM EXPIRED OFFER TEST SUCCEEDED"
