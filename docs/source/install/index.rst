Installation
============

Installation is simple: `install OpenStack`_, version **Ussuri** or above. Ensure that you have the following services enabled:

* Glance
* Ironic
* Keystone
* Neutron

The key feature that needs to be configured is `Ironic node multi-tenancy`_. Configuring node multi-tenancy requires the use of a custom Ironic policy file; you can see a sample one `here`_.

.. toctree::
   :maxdepth: 2

   external_network
   additional_patches
   esi_add_ons
   functional_tests
   node_cleaning
   security_recommendations

.. _install OpenStack: https://docs.openstack.org/install-guide/
.. _Ironic node multi-tenancy: https://docs.openstack.org/ironic/latest/admin/node-multitenancy.html
.. _here: https://github.com/CCI-MOC/esi/blob/master/etc/ironic/policy.yaml.sample
