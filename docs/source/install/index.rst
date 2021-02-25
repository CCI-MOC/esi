Installation
============

Installation is simple: `install OpenStack`_, version **Ussuri** or above. Ensure that you have the following services enabled:

* Glance
* Ironic
* Keystone
* Neutron

The key feature that needs to be configured is `Ironic node multi-tenancy`_.

ESI Add-Ons
-----------

Two additional ESI add-ons may be of use:

* `ESI Leap`_: baremetal node leasing service; required for ESI leasing workflow
   * `python-esileapclient`_
* `python-esiclient`_: additional OpenStack CLI commands that provide ease of use for users

Instructions on installing these add-ons can be found within the linked repositories.

.. _install OpenStack: https://docs.openstack.org/install-guide/
.. _Ironic node multi-tenancy: https://docs.openstack.org/ironic/latest/admin/node-multitenancy.html
.. _ESI Leap: https://github.com/CCI-MOC/esi-leap
.. _python-esileapclient: https://github.com/CCI-MOC/python-esileapclient
.. _python-esiclient: https://github.com/CCI-MOC/python-esiclient
