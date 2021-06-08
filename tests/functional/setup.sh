#!/bin/bash

tmpfile=$1
project_id=$2
start=$3
end=$4
lessee_option=''
nodefile=$(mktemp /tmp/nodes/XXXX)
errfile=$(mktemp ./errXXXXXX)
node_uuid=$(echo $nodefile | sed 's/\/tmp\/nodes\///')

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

# Check if the lessee was passed
if ! [[ -z ${5+x} ]]; then
  lessee_option=" --lessee $5"
fi

#######################
## OFFER CREATE TEST ##
#######################

# Tests that an owner can create an offer on a node they own

echo "OFFER CREATE TEST"

openstack --os-cloud test1 esi offer create \
  $node_uuid \
  --start-time $start \
  --end-time $end \
  --resource-type dummy_node\
  $lessee_option \
  -f shell > $tmpfile \
  || { ec=$?; echo "ERROR: failed to create offer" >&2; exit $ec; }

cat $tmpfile
echo "OFFER CREATE TEST SUCCEEDED"

. $tmpfile

cat <<EOF
Created offer $uuid:
  Starting at: $start_time
  Ending at:   $end_time
  For: $resource_type $node_uuid
EOF

cat <<EOF >> $tmpfile
errfile=$errfile
nodefile=$nodefile
node_uuid=$node_uuid
EOF
