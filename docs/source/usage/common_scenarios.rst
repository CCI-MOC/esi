Common Scenarios
================

Lessee Node Assignment
----------------------

Lessee node assignment can be performed by the administrator or node owner. It can be executed using the Ironic CLI:

  .. prompt:: bash $

    openstack baremetal node set --lessee <lessee project id> <node>

However, if you require reporting on historical usage, it is recommended that you use the `ESI Leap`_ service to create a lease that can be tracked and reported upon. This can be done as follows:

  .. prompt:: bash $

    openstack esi lease create –start-time <optional start time> –end-time <optional end time> <node> <lessee project id>

An administrator or node owner can also use ESI-Leap to offer up a node for any project to claim:

  .. prompt:: bash $

    openstack esi offer create --start-time <optional start time> --end-time <optional end time> <node>

A lessee can then claim the node, creating a lease:

  .. prompt:: bash $

    openstack esi offer list           # note UUID of offer to claim
    openstack esi offer claim --start-time <optional start time> --end-time <optional end time> <offer UUID>

Multiple lessees can claim the same offer as long as their start and end times do not overlap.

Lease Reporting
---------------

In order to create a report regarding leases, use the ``openstack esi lease list`` command. By default, this will print current leases to the output. The command can be modified in a variety of ways:

  .. prompt:: bash $

    -f {csv,json,table,value,yaml}          # change the format of the output
    --status any                             # list all leases, regardless of status
    --time-range <start time> <end time>     # view leases within the time range

Lessee Private Network
----------------------

If a lessee wishes to use a private network, they can run the following commands:

  .. prompt:: bash $

    openstack network create <network name>
    openstack subnet create --subnet-range 192.168.17.0/24 --allocation-pool start=192.168.17.10,end=192.168.17.250 --network <network name> <subnet name>

The created network will automatically have an assigned VLAN. This network can then be attached to a node as follows:

  .. prompt:: bash $

    openstack esi node network attach --network <network name> <node>

In order for the lessee to access a node on a private network, they can do one of two things:

* Contact the ESI administrator to connect the VLAN to an accessible node or VM outside of ESI
* Use a trunk port whose native network is a VLAN that the lessee can already access - usually a public or external network - and which has a tagged network corresponding to the private network:

  .. prompt:: bash $

    openstack esi trunk create --native-network <accessible network> <trunk name>
    openstack esi trunk add network --tagged-networks <private network> <trunk name>
    openstack esi node network attach --trunk <trunk name> <node>

.. _ESI Leap: https://github.com/CCI-MOC/esi-leap
