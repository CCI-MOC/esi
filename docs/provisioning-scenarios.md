# ESI Provisioning Scenarios

This document highlights ESI provisioning scenarios after a user has leased a node.

## Policy Pre-Requisites

The policy files for Ironic and Neutron have to be updated as per the [deployment doc](xdocs/deployment.md). These changes allow non-administrative users to access the necessary APIs.

## Metalsmith

[Metalsmith](https://docs.openstack.org/metalsmith/latest/) is a CLI based tool that can be used to provision baremetal nodes using OpenStack services such as Ironic, Neutron, and Glance.

```
metalsmith deploy --image centos7 --network provisioning --ssh-public-key ~/.ssh/id_rsa.pub --resource-class baremetal
```

## External Provisioning

1. Create a Neutron network and subnet corresponding to the external provisioning network
2. Attach the external provisioning network to the node
3. Power on the node

```
openstack network create --provider-network-type vlan --provider-physical-network datacentre --provider-segment 1234 external-provisioning
openstack subnet create \
  --network external-provisioning \
  --subnet-range 192.168.17.0/24  \
  --ip-version 4 \
  --gateway 192.168.17.254 \
  --allocation-pool start=192.168.17.150,end=192.168.17.159 \
  external-provisioning-subnet
openstack esi node network attach --network external-provisioning node-A
openstack baremetal node power on node-A
```