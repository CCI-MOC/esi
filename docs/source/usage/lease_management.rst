Lease Management
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

.. _ESI Leap: https://github.com/CCI-MOC/esi-leap
