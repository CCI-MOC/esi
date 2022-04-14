Node Cleaning and Maintenance
=============================

Ironic uses two main methods to perform actions on a node: `in-band and out-of-band`_. Ironic supports using both methods to clean a node. Further, Ironic provides two ways of cleaning a node: automated and manual.

Automated Node Cleaning
~~~~~~~~~~~~~~~~~~~~~~~

Automated cleaning is automatically performed before the first workload has been assigned to a node and when hardware is recycled from one workload to another. Automatic cleaning can be customized for to enable or disable certain features of cleaning.

Common use cases for automated cleaning:
  * Erase disk drives and destroy all the metadata from previous user.
  * Debug node failures resulting from disk failures by inspecting the automatic cleaning logs in Ironic conductor.
  * Cut the time spent in manually wiping and cleaning the node after every workload, saving man hours.
  * Reset raid configuration to a default state after every workload.

Steps involved in automated cleaning:
  1. Erase devices: out-of-band disk erase operation on all the supported physical drives in the node. Disk erase cannot be performed on physical drives.
  2. Erase Devices Metadata: Wipe partition tables, signatures, file-system identifications, and other disk devices.
  3. RAID Delete (Disabled-by-default): Delete any existing RAID configuration. This step needs to be enabled for automated cleaning.
  4. Setup RAID configuration in advance(Disabled-by-default): Create RAID configuration from a predefined template when the node in enrolled. This step needs to be enabled for automated cleaning.


Enable or Disable Automated Cleaning
------------------------------------

To enable automated cleaning, ensure that your ironic.conf has following option enabled.

.. prompt::

  [conductor]
  automated_clean=true

To disable it, ensure that your ironic.conf has following option disabled.

.. prompt::

  [conductor]
  automated_clean=false

Configuring Automated Cleaning Steps
------------------------------------

Disabling a step:
  A cleaning step can be disabled by setting the priority for that cleaning step to zero or ‘None’. For instance, to disable erase_devices, you would set the following configuration option:

  .. prompt::

    [deploy]
    erase_devices_priority=0

Enabling a step:
  A cleaning step can enabled by setting a positive integer value for its priority. For example, Ironic operator can enable factory_reset step by specifying priority in ironic.conf:

  .. prompt::

    [conductor]
    clean_step_priority_override=bios.factory_reset:10


Prioritizing a step:
  A cleaning step can be reordeed by modifying or overriding its integer priority. For example:

  .. prompt::

    [conductor]
    clean_step_priority_override=deploy.erase_devices_metadata:123
    clean_step_priority_override=management.reset_bios_to_default:234
    clean_step_priority_override=management.clean_priority_reset_ilo:345

This parameter can be specified as many times as required to define priorities for several cleaning steps - the values will be combined. More information about changing cleaning step priorities `here`_.

Ironic Automated Cleaning Default Steps:
  Most out-of-band cleaning steps have an explicit configuration option for priority, for in-band cleaning step (ironic-python-agent) use of a custom HardwareManager is required. The only exception is erase_devices, which can have its priority set in ironic.conf.

  Note:
    A priority value of zero indicates that the step is disabled by default.

  1. Driver-independent (default) Ironic-python-agent clean steps:

     Configuration options for the deploy clean steps are listed under [deploy] section in ironic.conf

    .. list-table::
      :widths: 25 25 25 50
      :header-rows: 1
      :align: left

      * - Step
        - Interface
        - Default Priority
        - Description
      * - erase_devices
        - deploy
        - 10
        - Securely erases all information from all recognized disk devices. Relatively fast when secure ATA erase is available, otherwise can take hours, especially on a virtual environment.
      * - erase_devices_metadata
        - deploy
        - 99
        - Erases partition tables from all recognized disk devices. Can be used as an alternative to the much longer erase_devices step.
      * - erase_devices_express
        - deploy
        - 0
        - Combines some of the perks of both erase_devices and erase_devices_metadata. Attempts to utilize hardware assisted data erasure features if available (currently only NVMe devices are supported).
      * - erase_pstore
        - deploy
        - 0
        - Erases entries from pstore, the kernel’s oops/panic logger. Disabled by default. Can be enabled via priority overrides.
      * - burnin_cpu
        - deploy
        - 0
        - Stress-test the CPUs of a node via stress-ng for a configurable amount of time.
      * - burnin_disk
        - deploy
        - 0
        - Stress-test the disks of a node via fio.
      * - burnin_network
        - deploy
        - 0
        - Stress-test the network of a pair of nodes via fio for a configurable amount of time.
      * - burnin_memory
        - deploy
        - 0
        - Stress-test the memory of a node via stress-ng for a configurable amount of time.
      * - delete_configuration
        - raid
        - 0
        - Delete existing RAID configuration. This step belongs to the raid interface and must be used through the `ironic RAID feature`_.
      * - create_configuration
        - raid
        - 0
        - Create a RAID configuration. This step belongs to the raid interface and must be used through the `ironic RAID feature`_.

  2. Driver-dependent cleaning steps:

     Configuration options for respective drivers are listed under their respective sections. For example.: ilo clean steps under [ilo] section in ironic.conf

    .. list-table::
      :widths: 25 25 25 50
      :header-rows: 1
      :align: left

      * - Driver
        - Step
        - Default Priority
        - Description
      * - `ilo`_
        - clean_priority_reset_ilo
        - 0
        - Resets the iLO. By default, this step is disabled.
      * - `ilo`_
        - clean_priority_reset_bios_to_default
        - 10
        - Resets system ROM settings to default, This clean step is supported only on Gen9 and above servers.
      * - `ilo`_
        - clean_priority_reset_secure_boot_keys_to_default
        - 20
        - Resets secure boot keys to manufacturer’s defaults. This step is supported only on Gen9 and above servers.
      * - `ilo`_
        - clean_priority_clear_secure_boot_keys
        - 0
        - Clears all secure boot keys. This step is supported only on Gen9 and above servers.
      * - `ilo`_
        - clean_priority_reset_ilo_credential
        - 30
        - Resets the iLO password, if ilo_change_password is specified as part of node’s driver_info.
      * - `irmc`_
        - clean_priority_restore_irmc_bios_config
        - 0
        - Automatically back up BIOS settings before deployment & restore these settings during automated cleaning.

To keep an eye out for more Automated Cleaning options in future releases, refer to `Ironic node drivers`_.


Use Automated Cleaning
----------------------

Trigger Automated Cleaning:
  Put the node in “manage” mode and then put it again in “deploy” mode to launch automated cleaning. Run the following commands:

.. prompt:: bash $

  openstack baremetal node manage <node>
  openstack baremetal node deploy <node>


Manual Node Cleaning
~~~~~~~~~~~~~~~~~~~~

`Manual cleaning`_ is a way to run driver-specific actions on manageable nodes. The mechanism is the same as with automated cleaning but it is not limited to just cleaning nodes. manual cleaning is typically used to handle long running, manual, or destructive tasks that an operator wishes to perform either before the first workload has been assigned to a node or between workloads.


Enable Manual Cleaning
----------------------

Manual cleaning can only be performed when a node is in the manageable state, and NOT under maintenance mode. To put a node in the manageable state run the following command:

.. prompt:: bash $

  openstack baremetal node manage <node>

Use Manual Cleaning
-------------------

Once a node is in the manageable state, The list of available manual cleaning steps can be `found here`_. Each step requires three parameters.:

    1. An interface in the cleaning step: management, raid, bios.
    2. The desired cleaning step for the selected interface.
    3. Required arguments for the cleaning step.


Run one of the following commands with these arguments:
  a. Input cleaning parameters in JSON format

  .. prompt:: bash $

    baremetal node clean <node> \
    --clean-steps '[{
      "interface": "<interface>",
        "step": "<name of cleaning step>",
        "args": {"<arg1>": "<value1>", ..., "<argn>": <valuen>}
    }]'

  b. Input parameters through a text file, run the following command

  .. prompt:: bash $

    baremetal node clean <node> \
    --clean-steps my-clean-steps.txt

  c. Input parameters through stdin

  .. prompt:: bash $

    cat my-clean-steps.txt | baremetal node clean <node> \
      --clean-steps -


Use Cases for Manual Cleaning
-----------------------------

  * `BIOS settings`_ of bare metal nodes can be customized.

  * To install custom iDRAC firmware images or reinstall the same driver(reset):

    * Reset or restore `iDRAC settings`_.

  * Driver firmware can be installed or reset. To check for supported manual cleaning options refer to `Ironic node drivers`_.:

    * Refer here for available manual cleaning parameters to `Install or change Driver firmware`_.

  * `Create Software RAID`_ configurations. For example, a sample raid configuration manual cleaning step:

    .. prompt::

       [raid]
        {
          "target":"clean",
          "clean_steps": [{
            "interface": "raid",
            "step": "create_configuration",
            "args": {"create_nonroot_volumes": false}
          },
          {
            "interface": "deploy",
            "step": "erase_devices"
          }]
        }


  * Reset driver credentials, for example, reset iLO password:

    .. prompt::

       [management]
        {
        "target":"clean",
        "clean_steps": [{
        "interface": "management",
        "step": "reset_ilo_credential",
        "args": {}
          }
        }

  Note:
    Manual cleaning can only be performed when a node is in “manageable” state. Once the manual cleaning is finished, the node will be put in the “manageable” state again.


.. _in-band and out-of-band: https://docs.openstack.org/ironic/latest/admin/cleaning.html#in-band-vs-out-of-band
.. _Ironic node drivers: https://docs.openstack.org/ironic/latest/admin/drivers/
.. _here: https://docs.openstack.org/ironic/queens/admin/cleaning.html#how-do-i-change-the-priority-of-a-cleaning-step
.. _Manual cleaning: https://docs.openstack.org/ironic/queens/admin/cleaning.html#manual-cleaning
.. _BIOS settings: https://esi.readthedocs.io/en/latest/usage/security_recommendations.html#bios-settings-reset
.. _iDRAC settings: https://esi.readthedocs.io/en/latest/usage/security_recommendations.html#idrac-settings-reset
.. _Create Software RAID: https://docs.openstack.org/ironic/latest/admin/raid.html#software-raid
.. _Install or change Driver firmware: https://docs.openstack.org/ironic/latest/admin/cleaning.html#management-interface
.. _found here: https://docs.openstack.org/ironic/latest/admin/cleaning.html#management-interface
.. _ilo: https://docs.openstack.org/ironic/latest/admin/drivers/ilo.html#supported-automated-cleaning-operations
.. _irmc: https://docs.openstack.org/ironic/latest/admin/drivers/irmc.html#supported-automated-cleaning-operations
.. _ironic RAID feature: https://docs.openstack.org/ironic/latest/admin/raid.html
