Installation
============

Installation is simple: `install OpenStack`_, version **Ussuri** or above. Ensure that you have the following services enabled:

* Glance
* Ironic
* Keystone
* Neutron

The key feature that needs to be configured is `Ironic node multi-tenancy`_.

Additional Patches
------------------

The following patches may be of use. Depending on your OpenStack version, they may be already included in your installation.

=================== ============================================= ========================
Repository          Patch                                         Status
=================== ============================================= ========================
ironic              `Allow node lessee to see node's ports`_      Released in **Victoria**
ironic              `Allow node vif attach to specify port_uuid`_ Released in **Victoria**
python-ironicclient `Add port-uuid parameter to node vif attach`_ Released in **Victoria**
network-runner      `Add kwargs to trunk ports`_                  Merged upstream
networking-ansible  `Correct port detachment`_                    Released in **Victoria**
=================== ============================================= ========================

ESI Add-Ons
-----------

Two additional ESI add-ons provide additional functionality:

* `ESI Leap`_: baremetal node leasing service; required for ESI leasing workflow
   * `python-esileapclient`_
* `python-esiclient`_: additional OpenStack CLI commands that provide ease of use for users

Instructions on installing these add-ons can be found within the linked repositories.

.. _install OpenStack: https://docs.openstack.org/install-guide/
.. _Ironic node multi-tenancy: https://docs.openstack.org/ironic/latest/admin/node-multitenancy.html
.. _ESI Leap: https://github.com/CCI-MOC/esi-leap
.. _python-esileapclient: https://github.com/CCI-MOC/python-esileapclient
.. _python-esiclient: https://github.com/CCI-MOC/python-esiclient
.. _Allow node lessee to see node's ports: https://review.opendev.org/c/openstack/ironic/+/730366
.. _Allow node vif attach to specify port_uuid: https://review.opendev.org/#/c/731780/
.. _Add port-uuid parameter to node vif attach: https://review.opendev.org/#/c/737585/
.. _Add kwargs to trunk ports: https://github.com/ansible-network/network-runner/pull/48
.. _Correct port detachment: https://review.opendev.org/#/c/745318/
