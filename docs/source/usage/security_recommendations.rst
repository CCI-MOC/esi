Security Recommendations
========================

BIOS Settings Reset
-------------------

A lessee leasing a node can change the BIOS settings. If these settings are not reset after the node is returned, then this can result in unexpected behavior for future users of the node. Fortunately Ironic allows nodes to `specify BIOS settings`_ that are applied upon cleaning.
This feature has been tested and the details are listed below.

Prerequisites
~~~~~~~~~~~~~
Ironic operator can enable a specific hardware type that supports BIOS configuration and then enable bios interface. `iDRAC`_ hardware type is used here.

* Install python-dracclient:

.. prompt:: bash $

  sudo pip install 'python-dracclient>=3.1.0'

* Enable the iDRAC hardware type with the required interfaces in ironic.conf:

.. prompt::

  [DEFAULT]
  enabled_hardware_types=idrac
  enabled_management_interfaces=idrac-wsman
  enabled_power_interfaces=idrac-wsman
  enabled_vendor_interface=idrac-wsman
  enabled_bios_interface=idrac-wsman

* Restart the ironic conductor service for the new configuration to take effect.

Configure the Node
~~~~~~~~~~~~~~~~~~
The following command configures a baremetal node with the iDRAC hardware type using WSMAN for all interfaces:

.. prompt:: bash $

  openstack baremetal node set \
    --driver idrac \
    --power-interface idrac-wsman \
    --management-interface idrac-wsman \
    --vendor-interface idrac-wsman \
    --console-interface no-console \
    --bios-interface idrac-wsman \
    --driver-info drac_username=<drac_user> \
    --driver-info drac_password=>drac_passwd> \
    --driver-info drac_address=<drac_ip> \
    <node>

Retrieve BIOS Settings
~~~~~~~~~~~~~~~~~~~~~~
Owner can retrieve the cached BIOS configuration:

.. prompt:: bash $

  openstack baremetal node bios setting list (-f json) <node>

Run Node Cleaning
~~~~~~~~~~~~~~~~~

**Manual Cleaning (Owner)**

Two manual cleaning steps are available for managing node's BIOS settings. Owner can run manual cleaning when the node is in the 'manageable' state.

* Factory reset: set BIOS to factory defaults.

.. prompt:: bash $

  openstack baremetal node clean --clean-steps '[{"interface": "bios", "step": "factory_reset"}]' <node>

* Apply BIOS configuration

  Owner could compare the retrieved BIOS settings with the ones before the node is leased out and reset them properly.
  Examples of doing this with a file my-clean-steps.txt:

.. prompt::

  [
    {
      "interface": "bios",
      "step": "apply_configuration",
      "args": {
        "settings": [
          {
            "name": "name",
            "value": "value"
          },
          {
            "name": "name",
            "value": "value"
          }
        ]
      }
    }
  ]

.. prompt:: bash $

  openstack baremetal node clean --clean-steps my-clean-steps.txt <node>

**Automated Cleaning (Ironic Operator)**

For automated cleaning, ironic operator can enable factory_reset step by specifying priority in ironic.conf:

.. prompt::

  [conductor]
  clean_step_priority_override=bios.factory_reset:10

Note:
    * factory_reset's priority shouldn't be higher than deploy.erase_devices_metadata's priority, or it may cause issues during erasing metadata. If the bios interface is set to no-bios, the factory_reset cleaning step won't be executed.
    * Applying specific BIOS settings to nodes is not supported by automated cleaning. Owner should do it manually.

.. _specify BIOS settings: https://docs.openstack.org/ironic/latest/admin/bios.html
.. _iDRAC: https://docs.openstack.org/ironic/latest/admin/drivers/idrac.html