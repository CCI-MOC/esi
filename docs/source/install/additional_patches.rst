Additional Patches
==================

The following patches may be of use. Depending on your OpenStack version, they may be already included in your installation.

+---------------------+-----------------------------------------------------+--------------------------+
| Repository          | Patch                                               | Status                   |
+=====================+=====================================================+==========================+
|                     | *Port Multi-Tenancy*                                |                          |
+---------------------+-----------------------------------------------------+--------------------------+
| ironic              | `Allow node lessee to see node's ports`_            | Released in **Victoria** |
+---------------------+-----------------------------------------------------+--------------------------+
| ironic              | `Allow node vif attach to specify port_uuid`_       | Released in **Victoria** |
+---------------------+-----------------------------------------------------+--------------------------+
| python-ironicclient | `Add port-uuid parameter to node vif attach`_       | Released in **Victoria** |
+---------------------+-----------------------------------------------------+--------------------------+
|                     | *Non-Admin Interface Override*                      |                          |
+---------------------+-----------------------------------------------------+--------------------------+
| ironic              | `Allow instance_info to override node interface`_   | Released in **Wallaby**  |
+---------------------+-----------------------------------------------------+--------------------------+
| ironic              | `Create node get_interface method`_                 | Merged **Upstream**      |
+---------------------+-----------------------------------------------------+--------------------------+
| ironic              | `Fix restricted allocation creation`_               | Merged **Upstream**      |
+---------------------+-----------------------------------------------------+--------------------------+
|                     | *Trunk Ports*                                       |                          |
+---------------------+-----------------------------------------------------+--------------------------+
| network-runner      | `Add kwargs to trunk ports`_                        | Released in **0.2.3**    |
+---------------------+-----------------------------------------------------+--------------------------+
| networking-ansible  | `Correct port detachment`_                          | Released in **Victoria** |
+---------------------+-----------------------------------------------------+--------------------------+
|                     | *Configure Clean Step Priorites*                    |                          |
+---------------------+-----------------------------------------------------+--------------------------+
| ironic              | `Enable priority overrides to enable/disable steps`_| Released in **Xena**     |
+---------------------+-----------------------------------------------------+--------------------------+

.. _Allow node lessee to see node's ports: https://review.opendev.org/c/openstack/ironic/+/730366
.. _Allow node vif attach to specify port_uuid: https://review.opendev.org/#/c/731780/
.. _Add port-uuid parameter to node vif attach: https://review.opendev.org/#/c/737585/
.. _Add kwargs to trunk ports: https://github.com/ansible-network/network-runner/pull/48
.. _Correct port detachment: https://review.opendev.org/#/c/745318/
.. _Allow instance_info to override node interface: https://review.opendev.org/c/openstack/ironic/+/777434
.. _Create node get_interface method: https://review.opendev.org/c/openstack/ironic/+/817086
.. _Fix restricted allocation creation: https://review.opendev.org/c/openstack/ironic/+/812007
.. _Enable priority overrides to enable/disable steps: https://review.opendev.org/c/openstack/ironic/+/804156
