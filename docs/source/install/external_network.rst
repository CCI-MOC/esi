External Networks
=================

The recommended way to allow external network access to a baremetal node is by `creating a shared external provider network`_. The instructions in the link explain how; in addition, this network should be created as ``--provider-network-type vlan`` with the appropriate vlan specified by ``--provider-segment``. For example:

  .. prompt:: bash $

    openstack network create \
              --provider-network-type vlan \
              --provider-segment <vlan id> \
              --provider-physical-network datacentre \
              --external --share \
              external
    openstack subnet create \
              --network external \
              --subnet-range <subnetrange> \
              --ip-version 4 \
              --gateway <gateway ip> \
              --allocation-pool start=<allocation start>,end=<allocation end> \
              --dns-nameserver 8.8.8.8 \
              --dhcp \
              subnet-external

Doing so allows ESI users to work with external networks the same way that they do with any other VLAN network.

.. _creating a shared external provider network: https://docs.openstack.org/install-guide/launch-instance-networks-provider.html
