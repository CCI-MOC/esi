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
    --driver-info drac_password=<drac_passwd> \
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

For automated cleaning, Ironic operator can enable factory_reset step by specifying priority in ironic.conf:

.. prompt::

  [conductor]
  clean_step_priority_override=bios.factory_reset:10

Note:
    * factory_reset's priority shouldn't be higher than deploy.erase_devices_metadata's priority, or it may cause issues during erasing metadata. If the bios interface is set to no-bios, the factory_reset cleaning step won't be executed.
    * Applying specific BIOS settings to nodes is not supported by automated cleaning. Owner should do it manually.

iDRAC Settings Reset
--------------------

A lessee leasing a node can change the iDRAC settings of the leased node. If these settings are not reset after the node is returned, then this can result in unexpected behavior for future users of the node. A node Owner or Admin can back up the iDRAC settings before leasing a node and restore the settings after the lease ends. Two ways to import/export iDRAC settings:

* Redfish API
* OpenStack Ironic Bare Metal Cleaning service.


Prerequisites
~~~~~~~~~~~~~

The `iDRAC`_ hardware type requires the python-dracclient and the sushy library to be installed on the Ironic conductor node(s) if the node is configured to use an idrac-redfish or idrac-wsman interface implementation.

* Install the `required libraries`_ and `enable iDRAC hardware type`_ with the required interfaces.

* Restart the Ironic conductor service for the new configuration to take effect.

Configure the node appropriately:
 The following command configures a bare metal node with the idrac hardware type assuming a mix of Redfish and WSMAN interfaces are used:

.. prompt:: bash $

  openstack baremetal node set \
    --driver idrac \
    --driver-info drac_username=user \
    --driver-info drac_password=pa$$w0rd \
    --driver-info drac_address=drac.host \
    --driver-info redfish_username=user \
    --driver-info redfish_password=pa$$w0rd \
    --driver-info redfish_address=drac.host \
    --driver-info redfish_system_id=/redfish/v1/Systems/System.Embedded.1 \
    --bios-interface idrac-redfish \
    --inspect-interface idrac-redfish \
    --management-interface idrac-redfish \
    --power-interface idrac-redfish \
    <node>


Import or export iDRAC configuration with idrac-redfish:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sample scripts to export and import the iDRAC configuration using the `Redfish API`_ are shown below. For more information refer the Redfish Module `function definitions`_.

* Export configuration: The system configuration file will be exported and saved locally, after running the following script.

.. prompt:: bash $

  python3 ExportSystemConfigurationLocalREDFISH.py -ip '10.1.10.3' -u 'new-user' -p $ADMIN_PASSWORD -t IDRAC

* Making changes:

  An operator may want to get rid of certain node specific configuration settings such as iDRAC connection settings, passwords, or any other linked services from the exported system configuration file,
  after modification the system configuration file is ready to be imported and replicated in other systems.

* Import configuration: Run the following script to import the system configuration.

.. prompt:: bash $

  python3 ImportSystemConfigurationLocalREDFISH.py -ip '10.1.10.3' -u 'new-user' -p $ADMIN_PASSWORD -t IDRAC


Note:
 * A restart may be required after a successful import.
 * Redfish does not support exporting the iDRAC license iDRAC 7/8, RACADM command can be used instead.
      * Usage
           - racadm license help import
           - racadm license help export

Import or export iDRAC configuration with Ironic manual cleaning :
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The clean and deploy steps provided in this section allow an owner to configure the system and collect the system inventory using configuration mold files. To export or import the configuration of current system or replicate the system configuration to that of a similar system.


**Steps**:

1. Storage options for Configuration settings:

   * **Swift Containers** (*Admin-only*):  Swift containers rely on the Swift endpoints defined in Ironic conductor and Swift Ironic account setup in the `Ironic.conf`_ file

     a. Create the containers to be used for configuration mold storage.

     b. For Ironic Swift user that is configured in the [swift] section add read/write access to these containers.


   * **HTTP servers** :

     a. To use HTTP server with configuration molds, Enable HTTP PUT support in the web server.

     b. Create the directory to be used for the configuration mold storage.

     c. Configure read/write access for HTTP Basic access authentication and provide user credentials in [molds]user and [molds]password fields.


2. Use the following manual cleaning steps to export configuration to the wanted location. Run the cleaning step during “manageable” state,  replace the cleaning step and args with one of the following options:

   a. **export_configuration** from the existing system with the **export_configuration_location** input parameter to export the configuration to either a web server or a Swift container.

   HTTP Web Server:

   .. prompt:: bash $

     openstack baremetal node clean --clean-steps  '[{"interface": "management","step": "export_configuration","args":{"export_configuration_location": <HTTP-url>}}]' <node>

   Swift Container:

   .. prompt:: bash $

     openstack baremetal node clean --clean-steps  '[{"interface": "management","step": "export_configuration","args":{"export_configuration_location": <swift-container-url>}}]' <node>

3. Restore the selected system configuration mold using the import_configuration manual cleaning step.:

   a. Directly to the original system with minimal or no modification.

   b. Configure a one to many system configuration settings template i.e.. Modify and import the exported system configuration for other systems to replicate. For example, remove sections that do not need to be replicated such as iDRAC connection settings. The configuration mold can be accessed directly from the storage location.

4. Import Settings:

   HTTP Web Server:

   .. prompt:: bash $

     openstack baremetal node clean --clean-steps  '[{"interface": "management","step": "import_configuration","args":{"import_configuration_location": <HTTP-url>}}]' <node>

   Swift Container:

   .. prompt:: bash $

     openstack baremetal node clean --clean-steps  '[{"interface": "management","step": "import_configuration","args":{"import_configuration_location": <swift-container-url>}}]' <node>


Notes:
  * It is not mandatory to use export_configuration step to create a configuration mold. Upload the file to a designated storage location without using Ironic if it has been created manually or by other means.


Other Security Risks and Suggested Measures
-------------------------------------------

1. There are `two specific endpoints`_ in the Ironic Bare Metal API that are intended for use by the ironic-python-agent RAM disk. They are not intended for public use, These endpoints can potentially cause security issues. Access to these endpoints from external or untrusted networks should to be prohibited.
|br|

2. Baseboard management controller(BMC) drivers besides BIOS and iDRAC, have not been tested for node rescue and recovery measures yet. Proceed with caution when making modifications in the BMC; as a connection failure is possible, and a data center visit may be needed to fix such a node failure.
|br|

3. An infected bare metal node can attack other connected nodes in the same group if there are no firewall rules in place. Certain measures by owners and admins can ensure additional safety and security. These measures can be: the use of network groups, creation of firewall groups, avoiding the use of same driver passwords across multiple nodes.
|br|

4. Use of bare metal hardware for activities such as, mining cryptocurrency, overclocking the CPU cores to boost compute perforance, or excessive usage of hard disk space as virtual memory(VRAM) to boost memory perforance, can have a negative impact on bare metal hardware health, and lifespan. Discussing the terms of a lease before leasing a node is recommended.
|br|

5. An admin may not be able keep an active track of activites and usage of a bare metal node under lease in a non-inasive way; but it is possible to monitor sensor information of a lessee node through serial console by accessing the BMC firware. The sensor information such as cpu core temperatures, cpu voltages, I/O rates, network traffic and fan rpm can be monitor to ensure that the node is in a healthy state.
|br|



.. _Ironic.conf: https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/16.0/html/configuration_reference/ironic
.. _specify BIOS settings: https://docs.openstack.org/ironic/latest/admin/bios.html
.. _iDRAC: https://docs.openstack.org/ironic/latest/admin/drivers/idrac.html
.. _Redfish API: https://www.dell.com/support/kbdoc/en-us/000178045/redfish-api-with-dell-integrated-remote-access-controller
.. _function definitions: https://github.com/dell/iDRAC-Redfish-Scripting/tree/master/iDRAC%20Python%20Redfish%20Module
.. _reset: https://www.delltechnologies.com/asset/en-us/products/servers/technical-support/managing-dell-emc-hardware-with-openstack-ironic-idrac-driver-2-0.pdf#page=18
.. _required libraries: https://docs.openstack.org/ironic/latest/admin/drivers/idrac.html#prerequisites
.. _enable iDRAC hardware type: https://docs.openstack.org/ironic/latest/admin/drivers/idrac.html#enabling
.. _two specific endpoints: https://docs.openstack.org/api-ref/baremetal/#utility
.. |br| raw:: html

      <br>
