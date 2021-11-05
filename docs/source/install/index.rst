Installation
============

Installation is simple: `install OpenStack`_, version **Ussuri** or above. Ensure that you have the following services enabled:

* Glance
* Ironic
* Keystone
* Neutron

The key feature that needs to be configured is `Ironic node multi-tenancy`_. Configuring node multi-tenancy requires the use of a custom Ironic policy file; you can see a sample one `here`_.

Additional Patches
------------------

The following patches may be of use. Depending on your OpenStack version, they may be already included in your installation.

+---------------------+---------------------------------------------------+--------------------------+
| Repository          | Patch                                             | Status                   |
+=====================+===================================================+==========================+
|                     | *Port Multi-Tenancy*                              |                          |
+---------------------+---------------------------------------------------+--------------------------+
| ironic              | `Allow node lessee to see node's ports`_          | Released in **Victoria** |
+---------------------+---------------------------------------------------+--------------------------+
| ironic              | `Allow node vif attach to specify port_uuid`_     | Released in **Victoria** |
+---------------------+---------------------------------------------------+--------------------------+
| python-ironicclient | `Add port-uuid parameter to node vif attach`_     | Released in **Victoria** |
+---------------------+---------------------------------------------------+--------------------------+
|                     | *Non-Admin Boot from Volume*                      |                          |
+---------------------+---------------------------------------------------+--------------------------+
| ironic              | `Allow instance_info to override node interface`_ | Released in **Wallaby**  |
+---------------------+---------------------------------------------------+--------------------------+
|                     | *Trunk Ports*                                     |                          |
+---------------------+---------------------------------------------------+--------------------------+
| network-runner      | `Add kwargs to trunk ports`_                      | Released in **0.2.3**    |
+---------------------+---------------------------------------------------+--------------------------+
| networking-ansible  | `Correct port detachment`_                        | Released in **Victoria** |
+---------------------+---------------------------------------------------+--------------------------+

ESI Add-Ons
-----------

Two additional ESI add-ons provide additional functionality:

* `ESI Leap`_: baremetal node leasing service; required for ESI leasing workflow
   * `python-esileapclient`_
* `python-esiclient`_: additional OpenStack CLI commands that provide ease of use for users

Instructions for installing these add-ons can be found within the linked repositories.

Functional Tests
----------------

The functional tests in `python-esiclient`_ and `python-esileapclient`_ may be useful in
ensuring that your OpenStack installation is configured properly for ESI. Documentation for running
these tests can be found within their respecitive repositories:

* `ESI Functional Tests`_
* `ESI Leap Functional Tests`_

.. _install OpenStack: https://docs.openstack.org/install-guide/
.. _Ironic node multi-tenancy: https://docs.openstack.org/ironic/latest/admin/node-multitenancy.html
.. _here: https://github.com/CCI-MOC/esi/blob/master/etc/ironic/policy.yaml.sample
.. _ESI Leap: https://github.com/CCI-MOC/esi-leap
.. _python-esileapclient: https://github.com/CCI-MOC/python-esileapclient
.. _python-esiclient: https://github.com/CCI-MOC/python-esiclient
.. _ESI Functional Tests: https://github.com/CCI-MOC/python-esiclient/tree/master/esiclient/tests/functional
.. _ESI Leap Functional Tests: https://github.com/CCI-MOC/python-esileapclient/tree/master/esileapclient/tests/functional
.. _Allow node lessee to see node's ports: https://review.opendev.org/c/openstack/ironic/+/730366
.. _Allow node vif attach to specify port_uuid: https://review.opendev.org/#/c/731780/
.. _Add port-uuid parameter to node vif attach: https://review.opendev.org/#/c/737585/
.. _Add kwargs to trunk ports: https://github.com/ansible-network/network-runner/pull/48
.. _Correct port detachment: https://review.opendev.org/#/c/745318/
.. _Allow instance_info to override node interface: https://review.opendev.org/c/openstack/ironic/+/777434
