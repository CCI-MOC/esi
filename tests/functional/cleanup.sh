#!/bin/bash

test_offer_uuid=$1

#######################
## OFFER DELETE TEST ##
#######################

# Tests that an owner can delete an offer on a node they own

echo "OFFER DELETE TEST"
echo "Deleting offer $test_offer_uuid"
openstack --os-cloud test1 esi offer delete $test_offer_uuid && echo "OFFER DELETE TEST SUCCEEDED"
