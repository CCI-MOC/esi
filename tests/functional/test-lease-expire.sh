#!/bin/bash

project_id=75681640118a4890b3da0d106eae8af7 # test1 uuid
tmpfile=$(mktemp ./leaseXXXXXX)
start=$(date +%Y-%m-%d)
end=$(date -d "+5 days" +"%Y-%m-%d")
resource_type="dummy_node"

# Setup script, contains offer create test

./setup.sh "$tmpfile" "$project_id" "$start" "$end" "$resource_type"

. $tmpfile

# The uuid variable will be overwritten, so we save it here
test_offer_uuid=$uuid
# Run cleanup if the script exits, contains offer delete test
trap "./cleanup.sh $test_offer_uuid; rm -f $tmpfile $errfile $nodefile" EXIT

######################
## OFFER CLAIM TEST ##
######################

# Tests that a lessee can claim an offer available to them

echo "OFFER CLAIM TEST"

openstack --os-cloud test1-subproject esi offer claim $uuid \
  --start-time="$start" \
  --end-time="$(date -d "+1 minute" +"%Y-%m-%d %H:%M:%S")" \
  -f shell > $tmpfile \
  || { ec=$?; echo "ERROR: failed to claim offer" >&2; exit $ec; }

echo "OFFER CLAIM TEST SUCCEEDED"

echo "Sleeping for 2 minutes so the offer can expire"
sleep 2m
date +"%Y-%m-%D %H:%M:%S"

###################################
## LEASE LIST EXPIRED LEASE TEST ##
###################################

echo "LEASE LIST EXPIRED LEASE TEST"

openstack --os-cloud test1-subproject esi lease list -f json > $tmpfile \
  || { ec=$?; echo "ERROR: failed to list leases" >&2; exit $ec; }
cat $tmpfile
jq -r ".[].UUID" $tmpfile | grep $uuid \
  && { ec=$?; echo "ERROR: expired lease is visible" >&2; exit $ec; }

echo "LEASE LIST EXPIRED LEASE TEST SUCCEEDED"
