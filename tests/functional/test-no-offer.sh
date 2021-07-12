#!/bin/bash

project_id=75681640118a4890b3da0d106eae8af7 # test1 uuid
tmpfile=$(mktemp ./tmpXXXXXX)
start=$(date +%Y-%m-%d)
end=$(date -d "+5 days" +%Y-%m-%d)
nodefile=$(mktemp /tmp/nodes/XXXX)
errfile=$(mktemp ./errXXXXXX)
node_uuid=$(echo $nodefile | sed 's/\/tmp\/nodes\///')

trap "rm -f $nodefile $tmpfile $errfile" EXIT

# Create dummy node

cat <<EOF > /tmp/nodes/$node_uuid
{
    "project_owner_id": "$project_id",
    "server_config": {
        "new attribute XYZ": "This is just a sample list of free-form attributes used for describing a server.",
        "cpu_type": "Intel Xeon",
        "cores": 16,
        "ram_gb": 512,
        "storage_type": "samsung SSD",
        "storage_size_gb": 204
    }
}
EOF

#######################
## LEASE CREATE TEST ##
#######################

# Tests that an owner can create a lease without a preexisting offer

echo "LEASE CREATE TEST"

openstack --os-cloud test1 esi lease create \
  $node_uuid \
  test1-subproject \
  --start-time $start \
  --end-time $end \
  --resource-type dummy_node \
  -f shell > $tmpfile \
  || { ec=$?; echo "ERROR: failed to create lease" >&2; exit $ec; }

cat $tmpfile
. $tmpfile

echo "LEASE CREATE TEST SUCCEEDED"

#######################
## LEASE DELETE TEST ##
#######################

# Tests that an owner can delete a lease on a node they own

echo "LEASE DELETE TEST"

openstack  --os-cloud test1 esi lease delete $uuid \
  || { ec=$?; echo "ERROR: failed to delete lease" >&2; exit $ec; }

echo "LEASE DELETE TEST SUCCEEDED"

####################################
## OFFER CREATE INVALID USER TEST ##
####################################

# Tests that an owner cannot create an offer on a node they don't own

echo "OFFER CREATE INVALID USER TEST"

openstack --os-cloud test2 esi offer create \
  $node_uuid \
  --start-time $start \
  --end-time $end \
  --resource-type dummy_node \
  -f shell > $tmpfile 2> $errfile
ec=$?
expected_error="Access was denied to dummy_node $node_uuid."

if ! cat $errfile | grep -q "$expected_error"; then
  if [[ $ec -eq 0 ]]; then
    echo "ERROR: succeeded creating offer despite invalid user" >&2
    . $tmpfile
    echo "Deleting invalid user test offer..."
    openstack --os-cloud admin esi offer delete $uuid
  else
    echo "ERROR: unexpected error during offer create invalid user test" >&2
    cat $errfile >&2
  fi
  exit 1
fi

echo "OFFER CREATE INVALID USER TEST SUCCEEDED"

####################################
## LEASE CREATE INVALID USER TEST ##
####################################

# Tests that an owner cannot create a lease on a node they don't own

echo "LEASE CREATE INVALID USER TEST"

openstack --os-cloud test2 esi lease create \
  $node_uuid \
  test2-subproject \
  --start-time $start \
  --end-time $end \
  --resource-type dummy_node \
  -f shell > $tmpfile 2> $errfile
ec=$?
expected_error="Access was denied to dummy_node $node_uuid."

if ! cat $errfile | grep -q "$expected_error"; then
  if [[ $ec -eq 0 ]]; then
    echo "ERROR: succeeded creating lease despite invalid user" >&2
    . $tmpfile
    echo "Deleting invalid user test lease..."
    openstack --os-cloud admin esi lease delete $uuid
  else
    echo "ERROR: unexpected error during lease create invalid user test" >&2
    cat $errfile >&2
  fi
  exit 1
fi

echo "LEASE CREATE INVALID USER TEST SUCCEEDED"


