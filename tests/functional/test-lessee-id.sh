#!/bin/bash

project_id=75681640118a4890b3da0d106eae8af7 # test1 uuid
tmpfile=$(mktemp ./leaseXXXXXX)
start=$(date +%Y-%m-%d)
end=$(date -d "+5 days" +%Y-%m-%d)
lessee='test1-subproject'

# Setup script, contains offer create test

./setup.sh "$tmpfile" "$project_id" "$start" "$end" "$lessee"

# Sources variables defined in the setup script
. $tmpfile

# The uuid variable will be overwritten, so we save it here
test_offer_uuid=$uuid
# Run cleanup if the script exits, contains offer delete test
trap "./cleanup.sh $test_offer_uuid; rm -f $tmpfile $errfile $nodefile" EXIT 

#####################
## OFFER LIST TEST ##
#####################

# Tests that a lessee can list offers

echo "OFFER LIST TEST"

openstack --os-cloud test1-subproject esi offer list -f json > $tmpfile \
  || { ec=$?; echo "ERROR: failed to list offers" >&2; exit $ec; }
jq -r ".[].UUID" $tmpfile | grep $uuid \
  || { ec=$?; echo "ERROR: test offer not visible" >&2; exit $ec; }

echo "OFFER LIST TEST SUCCEEDED"

###################################
## OFFER CLAIM INVALID USER TEST ##
###################################

# Tests that a lessee cannot create a claim on an offer that they don't have access to

echo "OFFER CLAIM INVALID USER TEST"

openstack --os-cloud test1-subproject-1 esi offer claim $test_offer_uuid -f shell > $tmpfile 2> $errfile
ec=$?
expected_error="Access was denied to offer $test_offer_uuid."

if ! grep -q "$expected_error" $errfile; then
  if [[ $ec -eq 0 ]]; then
    echo "ERROR: succeeded claiming offer despite invalid user" >&2
  else
    echo "ERROR: unexpected error during invalid user test" >&2
    cat $errfile >&2
  fi
  exit 1
fi

echo "OFFER CLAIM INVALID USER TEST SUCCEEDED"

######################
## OFFER CLAIM TEST ##
######################

# Tests that a lessee can claim an offer available to them

echo "OFFER CLAIM TEST"

openstack --os-cloud test1-subproject esi offer claim $uuid -f shell > $tmpfile \
  || { ec=$?; echo "ERROR: failed to claim offer" >&2; exit $ec; }

echo "OFFER CLAIM TEST SUCCEEDED"

# Print info about the newly created lease

. $tmpfile

cat <<EOF
Created lease $uuid:
  Starting at: $start_time
  Ending at:   $end_time
  For: $resource_type $resource_uuid
  From offer:  $test_offer_uuid
EOF

#####################
## LEASE LIST TEST ##
#####################

# Tests that an owner can view leases on nodes they own

echo "LEASE LIST TEST"

openstack --os-cloud test1 esi lease list -f json > $tmpfile \
  || { ec=$?; echo "ERROR: failed to list leases" >&2; exit $ec; }

jq -r ".[].UUID" $tmpfile | grep $uuid \
  || { ec=$?; echo "ERROR: test lease not visible" >&2; exit $ec; }

echo "LEASE LIST TEST SUCCEEDED"

#######################
## LEASE DELETE TEST ##
#######################

# Tests that an owner can delete a lease on a node they own

echo "LEASE DELETE TEST"

openstack  --os-cloud test1 esi lease delete $uuid \
  || { ec=$?; echo "ERROR: failed to delete lease" >&2; exit $ec; }

echo "LEASE DELETE TEST SUCCEEDED"
