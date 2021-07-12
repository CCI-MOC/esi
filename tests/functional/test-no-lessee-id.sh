#!/bin/bash

project_id=75681640118a4890b3da0d106eae8af7 # test1 uuid
tmpfile=$(mktemp ./leaseXXXXXX)
start=$(date +%Y-%m-%d)
end=$(date -d "+5 days" +%Y-%m-%d)
resource_type="dummy_node"

# Setup script, contains offer create test

./setup.sh "$tmpfile" "$project_id" "$start" "$end" "$resource_type"

. $tmpfile

# The uuid variable will be overwritten, so we save it here
test_offer_uuid=$uuid
# Run cleanup if the script exits, contains offer delete test
trap "./cleanup.sh $test_offer_uuid; rm -f $tmpfile $errfile $nodefile" EXIT

#####################################
## OFFER CREATE TIME CONFLICT TEST ##
#####################################

# Tests that an owner cannot create an offer on a node that would cause a time conflict

echo "OFFER CREATE TIME CONFLICT TEST"

openstack --os-cloud test1 esi offer create \
  $node_uuid \
  --start-time $start \
  --end-time $end \
  --resource-type $resource_type \
  -f shell > $tmpfile 2> $errfile
ec=$?
expected_error="Time conflict for $resource_type $node_uuid."

if ! cat $errfile | grep -q "$expected_error"; then
  if [[ $ec -eq 0 ]]; then
    echo "ERROR: succeeded creating offer despite time conflict" >&2
    . $tmpfile
    echo "Deleting time conflict test offer..."
    ./cleanup.sh $uuid
  else
    echo "ERROR: unexpected error during time conflict test" >&2
    cat $errfile >&2
  fi
  exit 1
fi

echo "OFFER CREATE TIME CONFLICT TEST SUCCEEDED"

#################################
## OFFER DELETE NOT FOUND TEST ##
#################################

# Tests that an owner cannot delete a nonexistent offer

echo "OFFER DELETE NOT FOUND TEST"

openstack --os-cloud test1 esi offer delete "notanofferuuid" > $tmpfile 2> $errfile
ec=$?
expected_error='Offer with name or uuid notanofferuuid not found.'

if ! grep -q "$expected_error" $errfile; then
  if [[ $ec -eq 0 ]]; then
    echo "ERROR: succeeded deleting offer that shouldn't exist. Either someone named their offer 'notanofferuuid' or the delete command gave a success when it shouldn't have" >&2
  else
    echo "ERROR: unexpected error during offer not found test" >&2
    cat $errfile >&2
  fi
  exit 1
fi

echo "OFFER DELETE NOT FOUND TEST SUCCEEDED"

####################################
## OFFER DELETE INVALID USER TEST ##
####################################

# Tests that an owner cannot delete a nonexistent offer

echo "OFFER DELETE INVALID USER TEST"

openstack --os-cloud test2 esi offer delete $test_offer_uuid > $tmpfile 2> $errfile
ec=$?
# Ends up doing the same thing as the not found test since test2 can't view the offer
expected_error="Offer with name or uuid $test_offer_uuid not found."

if ! grep -q "$expected_error" $errfile; then
  if [[ $ec -eq 0 ]]; then
    echo "ERROR: succeeded deleting offer despite invalid user" >&2
  else
    echo "ERROR: unexpected error during delete offer invalid user test" >&2
    cat $errfile >&2
  fi
  exit 1
fi

echo "OFFER DELETE INVALID USER TEST SUCCEEDED"

############################################
## OFFER NOT AVAILABLE IN TIME RANGE TEST ##
############################################

# Tests that a lessee cannot claim an offer for a time range it is not available for

echo "OFFER NOT AVAILABLE IN TIME RANGE TEST"

openstack --os-cloud test1-subproject esi offer claim $test_offer_uuid --start-time $(date -d "+6 days" +%Y-%m-%d) --end-time $(date -d "+7 days" +%Y-%m-%d) -f shell > $tmpfile 2> $errfile
ec=$?
expected_error="Offer $test_offer_uuid has no availabilities at given time range"

if ! grep -q "$expected_error" $errfile; then
  if [[ $ec -eq 0 ]]; then
    echo "ERROR: offer was successfully claimed during invalid time range" >&2
  else
    echo "ERROR: unexpected error during not available in time range test" >&2
    cat $errfile >&2
  fi
  exit 1
fi

echo "OFFER NOT AVAILABLE IN TIME RANGE TEST SUCCEEDED"

######################
## OFFER CLAIM TEST ##
######################

# Tests that a lessee can claim an offer available to them
# Setting up a claim is needed for the claim time conflict test

echo "OFFER CLAIM TEST"

openstack --os-cloud test1-subproject esi offer claim \
  --start-time $start \
  --end-time $(date -d "+2 days" +%Y-%m-%d) \
  $test_offer_uuid -f shell > $tmpfile \
  || { ec=$?; echo "ERROR: failed to claim offer" >&2; exit $ec; }
cat $tmpfile
. $tmpfile

echo "OFFER CLAIM TEST SUCCEEDED"

####################################
## OFFER CLAIM TIME CONFLICT TEST ##
####################################

# Tests that a lessee cannot create a claim on an offer that would cause a time
# conflict with a lease created by another lessee

echo "OFFER CLAIM TIME CONFLICT TEST"

openstack --os-cloud test1-subproject-1 esi offer claim $test_offer_uuid -f shell > $tmpfile 2> $errfile
ec=$?
expected_error='Attempted to create lease resource with an invalid Start Time.*'
cat $errfile

if ! grep -q "$expected_error" $errfile; then
  if [[ $ec -eq 0 ]]; then
    echo "ERROR: succeeded claiming offer despite time conflict" >&2
  else
    echo "ERROR: unexpected error during time conflict test" >&2
    cat $errfile >&2
  fi
  exit 1
fi

echo "OFFER CLAIM TIME CONFLICT TEST SUCCEEDED"

#######################################
## OFFER CLAIM MULTIPLE LESSEES TEST ##
#######################################

# Tests that different lessees can each claim a single offer as long as there is no time conflict

echo "OFFER CLAIM MULTIPLE LESSEES TEST"

openstack --os-cloud test1-subproject esi offer claim \
  --start-time $(date -d "+2 days" +%Y-%m-%d) \
  --end-time $end \
  $test_offer_uuid -f shell > $tmpfile \
  || { ec=$?; echo "ERROR: failed to claim offer" >&2; exit $ec; }
cat $tmpfile
. $tmpfile

echo "OFFER CLAIM MULTIPLE LESSEES TEST SUCCEEDED"
