CLI Commands
============

Users can access any OpenStack CLI command that they have permission to use. For example, once a node is assigned to an owner or lessee they can use Ironic CLI commands to work with that node as limited by Ironic policy; see the `Ironic CLI reference`_ for more information.

These commands may be of particular interest to ESI users.

Assigning Owners
----------------

+---------------------+---------------------------------------------------------------------------+
|                     | **Admin Actions**                                                         |
+---------------------+---------------------------------------------------------------------------+
| Assign Node Owner   | ``openstack baremetal node set --owner <project_id> <node_name_or_uuid>`` |
+---------------------+---------------------------------------------------------------------------+
| Unassign Node Owner | ``openstack baremetal node unset --owner <node_name_or_uuid>``            |
+---------------------+---------------------------------------------------------------------------+

Leasing Workflows
-----------------

There are two possible node leasing workflows.

Simple Workflow
~~~~~~~~~~~~~~~

In the simple case, node lessees are managed directly by admins and owners, who assign and unassign
nodes to a project as they see fit. This workflow does not require any custom ESI services.

+----------------------+----------------------------------------------------------------------------+
|                      | **Admin/Owner Actions**                                                    |
+----------------------+----------------------------------------------------------------------------+
| Assign Node Lessee   | ``openstack baremetal node set --lessee <project_id> <node_name_or_uuid>`` |
+----------------------+----------------------------------------------------------------------------+
| Unassign Node Lessee | ``openstack baremetal node unset --lessee <node_name_or_uuid>``            |
+----------------------+----------------------------------------------------------------------------+

ESI Leasing Workflow
~~~~~~~~~~~~~~~~~~~~

If `ESI Leap`_ is installed, then node leases can also be managed as follows:

**Owner Actions**

Node owners can lease a node directly to a lessee, or offer up their nodes for lease for a given time period. Unoffered nodes cannot be seen by lessees.

+--------------+---------------------------------------------------------------------------------------------------------------------+
|              | **Owner Actions**                                                                                                   |
+--------------+---------------------------------------------------------------------------------------------------------------------+
| Create Lease | ``openstack esi lease create --start-time <start_time> --end-time <end_time> <node_uuid_or_name> <lessee_project>`` |
+--------------+---------------------------------------------------------------------------------------------------------------------+
| Show Lease   | ``openstack esi lease show <lease_uuid>``                                                                           |
+--------------+---------------------------------------------------------------------------------------------------------------------+
| Delete Lease | ``openstack esi lease delete <lease_uuid>``                                                                         |
+--------------+---------------------------------------------------------------------------------------------------------------------+
| Create Offer | ``openstack esi offer create --start-time <start_time> --end-time <end_time> <node_uuid_or_name>``                  |
+--------------+---------------------------------------------------------------------------------------------------------------------+
| View Offer   | ``openstack esi offer show <offer_uuid>``                                                                           |
+--------------+---------------------------------------------------------------------------------------------------------------------+
| Delete Offer | ``openstack esi offer delete <offer_uuid>``                                                                         |
+--------------+---------------------------------------------------------------------------------------------------------------------+

**Lessee Actions**

Users can view available offers and claim an offer to create a lease.

+--------------+--------------------------------------------------------------------------------------------+
|              | **Lessee Actions**                                                                         |
+--------------+--------------------------------------------------------------------------------------------+
| List Offers  | ``openstack esi offer list``                                                               |
+--------------+--------------------------------------------------------------------------------------------+
| Claim Offer  | ``openstack esi offer claim --start-time <start_time> --end-time <end_time> <offer_uuid>`` |
+--------------+--------------------------------------------------------------------------------------------+
| List Leases  | ``openstack esi lease list``                                                               |
+--------------+--------------------------------------------------------------------------------------------+
| Show Lease   | ``openstack esi lease show <lease_uuid>``                                                  |
+--------------+--------------------------------------------------------------------------------------------+
| Delete Lease | ``openstack esi lease delete <lease_uuid>``                                                |
+--------------+--------------------------------------------------------------------------------------------+

Subleases
~~~~~~~~~

A lessee can perform owner actions on a node that they have leased, effectively subleasing a node. Note that a sublessee cannot further sublease a node.

Limited Offers and Subprojects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An offer can be made available to a limited number of projects by using the ``--lessee`` option when creating the offer.

+----------------------+------------------------------------------------------------------------------------------------------------------------------+
|                      | **Owner Actions**                                                                                                            |
+----------------------+------------------------------------------------------------------------------------------------------------------------------+
| Create Limited Offer | ``openstack esi offer create --start-time <start_time> --end-time <end_time> --lessee <lessee_project> <node_uuid_or_name>`` |
+----------------------+------------------------------------------------------------------------------------------------------------------------------+

An offer created in such a way is available not only to the lessee project, but to the entire subtree of projects beneath the lessee project. As a result, using this feature effectively requires projects to be carefully organized.

Resource Isolation and Sharing
------------------------------

ESI provides bare metal isolation through the use of owners and lessees. It may be useful to isolate or share additional OpenStack resources.

Networks
~~~~~~~~

By default, a network is only viewable and usable by the project that created it. Public networks can be created using the ``--share`` flag.

A private network can also be shared on a project-by-project basis:

+--------------------+--------------------------------------------------------------------------------------------------------------------------------+
|                    | **Network Owner Actions**                                                                                                      |
+--------------------+--------------------------------------------------------------------------------------------------------------------------------+
| List RBAC Policies | ``openstack network rbac list``                                                                                                |
+--------------------+--------------------------------------------------------------------------------------------------------------------------------+
| Share Network      | ``openstack network rbac create --action access_as_shared --type network --target-project <project-to-gain-access> <network>`` |
+--------------------+--------------------------------------------------------------------------------------------------------------------------------+
| Unshare Network    | ``openstack network rbac delete <rbac policy>``                                                                                |
+--------------------+--------------------------------------------------------------------------------------------------------------------------------+

Volumes
~~~~~~~

A volumes is only viewable and usable by the project that created it. Volumes cannot be shared; however, they can be transferred. First, the owner of the volume must create a volume transfer request:

+--------------------------------+--------------------------------------------------------------+
|                                | **Volume Owner Actions**                                     |
+--------------------------------+--------------------------------------------------------------+
| Create Volume Transfer Request | ``openstack volume transfer request create volume-bootable`` |
+--------------------------------+--------------------------------------------------------------+

The output of this command includes an ``id`` and an ``auth_key``. The volume owner sends these values to the desired project, who can then accept the transfer:

+--------------------------------+---------------------------------------------------------------------------------+
|                                | **Target Volume Owner Actions**                                                 |
+--------------------------------+---------------------------------------------------------------------------------+
| Accept Volume Transfer Request | ``openstack volume transfer request accept --auth-key <auth_key> <request_id>`` |
+--------------------------------+---------------------------------------------------------------------------------+

Images
~~~~~~

By default, an image is only viewable and usable by the project that created it. Administrators can create a public image by using the ``--public`` flag.

A private image can also be shared on a project-by-project basis:

+----------------------+------------------------------------------------------+
|                      | **Image Owner Actions**                              |
+----------------------+------------------------------------------------------+
| Share Image          | ``openstack image add project <image> <project>``    |
+----------------------+------------------------------------------------------+
| Unshare Image        | ``openstack image remove project <image> <project>`` |
+----------------------+------------------------------------------------------+

Note that the image owner must send the target project the image ID, and the target project must accept the image share:

+----------------------+---------------------------------------------+
|                      | **Target Project Actions**                  |
+----------------------+---------------------------------------------+
| Accept Image Share   | ``openstack image set --accept <image id>`` |
+----------------------+---------------------------------------------+

Provisioning a Node
-------------------

There are multiple ways for a non-admin to provision a node.

Image
~~~~~

Image-based provisioning can be accomplished through the use of `Metalsmith`_. It requires the image to be uploaded into OpenStack Glance. Once that's done, a non-admin can run the following:

+----------------+-------------------------------------------------------------------------------------------------------------------------------------------+
|                | **Actions**                                                                                                                               |
+----------------+-------------------------------------------------------------------------------------------------------------------------------------------+
| Provision Node | ``metalsmith deploy --resource-class baremetal --image <image> --network <network> --candidate <node id> --ssh-public-key <path-to-key>`` |
+----------------+-------------------------------------------------------------------------------------------------------------------------------------------+
| Undeploy Node  | ``metalsmith undeploy <node id>``                                                                                                         |
+----------------+-------------------------------------------------------------------------------------------------------------------------------------------+

Volume
~~~~~~

If you'd like to create a volume from an image, run the following:

+--------------------------+------------------------------------------------------------------------------------------+
|                          | **Actions**                                                                              |
+--------------------------+------------------------------------------------------------------------------------------+
| Create Volume from Image | ``openstack volume create <volume-name> --image <image> --bootable --size <size-in-gb>`` |
+--------------------------+------------------------------------------------------------------------------------------+

In order to boot a node from a volume, two node attributes must be set as follows:

* The node owner or admin should set the `iscsi_boot` node capability prior to leasing the node.
* The node lessee should not be allowed to edit the `storage_interface` node attribute. Instead, they can run the following command to temporarily override that value (until the node is cleaned):

+----------------------------+----------------------------------------------------------------------------------+
|                            | **Actions**                                                                      |
+----------------------------+----------------------------------------------------------------------------------+
| Override Storage Interface | ``openstack baremetal node set --instance-info storage_interface=cinder <node>`` |
+----------------------------+----------------------------------------------------------------------------------+

The process for booting a node from a volume is described in the `Ironic boot-from-volume documentation`_. You can also use `python-esiclient`_ to run that workflow with a single command:

+-----------------------+--------------------------------------------------------------------------------------------+
|                       | **Actions**                                                                                |
+-----------------------+--------------------------------------------------------------------------------------------+
| Boot Node from Volume | ``openstack esi node volume attach (--network <network> | --port <port>) <node> <volume>`` |
+-----------------------+--------------------------------------------------------------------------------------------+

External Provisioning
~~~~~~~~~~~~~~~~~~~~~

In order to use an external provisioning service, start by moving the node to the ``manageable`` state:

+-------------+--------------------------------------------+
|             | **Actions**                                |
+-------------+--------------------------------------------+
| Manage Node | ``openstack baremetal node manage <node>`` |
+-------------+--------------------------------------------+

Next, mark the node as ``active`` with the `adopt` command. This is required for the subsequent networking action.

+------------+-------------------------------------------+
|            | **Actions**                               |
+------------+-------------------------------------------+
| Adopt Node | ``openstack baremetal node adopt <node>`` |
+------------+-------------------------------------------+

If you would like the node to pxe boot, set the boot device:

+----------------------+------------------------------------------------------------------------+
|                      | **Actions**                                                            |
+----------------------+------------------------------------------------------------------------+
| Set Node Boot Device | ``openstack baremetal node boot device set <node> pxe (--persistent)`` |
+----------------------+------------------------------------------------------------------------+

Now simply attach the node to the appropriate network. You can do so through OpenStack Neutron and Ironic CLI commands, or through `python-esiclient`_:

+------------------------+------------------------------------------------------------------------------------------------------+
|                        | **Actions**                                                                                          |
+------------------------+------------------------------------------------------------------------------------------------------+
| Attach Network to Node | ``openstack esi node network attach (--network <network> | --port <port> | --trunk <trunk>) <node>`` |
+------------------------+------------------------------------------------------------------------------------------------------+

Finally, power the node on:

+---------------+----------------------------------------------+
|               | **Actions**                                  |
+---------------+----------------------------------------------+
| Power Node On | ``openstack baremetal node power on <node>`` |
+---------------+----------------------------------------------+


Serial Console Access
---------------------

In order to access a node using a serial console, the admin or owner must configure the node's console interface.
Instructions for this can be found under `Configuring Web or Serial Console`_ in Ironic's documentation.
Once the node is properly configured, the console can be enabled and disabled as needed.

Following is the pre-requisite for functioning of serial console:

* The ``ipmi_terminal_port`` port must be unique and only the admin or node owner can set this value.
* The admin must open the firewall on the controller to allow TCP connections on the port.

+-----------------+-----------------------------------------------------+
|                 | **Actions**                                         |
+-----------------+-----------------------------------------------------+
| Enable Console  | ``openstack baremetal node console enable <node>``  |
+-----------------+-----------------------------------------------------+
| Disable Console | ``openstack baremetal node console disable <node>`` |
+-----------------+-----------------------------------------------------+

Serial console information is available from the Bare Metal service. Get
serial console information for a node from the Bare Metal service as follows:

+---------------------------+--------------------------------------------------+
|                           | **Actions**                                      |
+---------------------------+--------------------------------------------------+
| Show Console Information  | ``openstack baremetal node console show <node>`` |
+---------------------------+--------------------------------------------------+

``openstack baremetal node console show <node>`` will generate the following output:

+-----------------+----------------------------------------------------------------------+
| Property        | Value                                                                |
+-----------------+----------------------------------------------------------------------+
| console_enabled | True                                                                 |
+-----------------+----------------------------------------------------------------------+
| console_info    | {u'url': u'``tcp://<host>:<port>``', u'type': u'socat'}              |
+-----------------+----------------------------------------------------------------------+

If ``console_enabled`` is ``true``, we can access the serial console using following command:

``socat - tcp:<host>:<port>``

If ``console_enabled`` is ``false`` or ``console_info`` is ``None`` then
the serial console is disabled. Note, there can only be one ipmi connection to the node, meaning only one user may access the console at a time.


Additional ESI CLI Actions
--------------------------

`python-esiclient`_ and `python-esileapclient`_ provide additional commands that combine multiple OpenStack CLI functions into a single action.

Switch Information
~~~~~~~~~~~~~~~~~~

+-------------------------------+-----------------------------------------------------------------------------+
|                               | **Actions**                                                                 |
+-------------------------------+-----------------------------------------------------------------------------+
| List Switches                 | ``openstack esi switch list``                                               |
+-------------------------------+-----------------------------------------------------------------------------+
| List Switch Ports             | ``openstack esi switch port list <switch>``                                 |
+-------------------------------+-----------------------------------------------------------------------------+
| List Switch VLANs             | ``openstack esi switch vlan list <switch>``                                 |
+-------------------------------+-----------------------------------------------------------------------------+
| Add VLAN to Switch Trunk      | ``openstack esi switch trunk add vlan <switch> <switchport> <vlan_id>``     |
+-------------------------------+-----------------------------------------------------------------------------+
| Remove VLAN from Switch Trunk | ``openstack esi switch trunk remove vlan <switch> <switchport> <vlan_id>``  |
+-------------------------------+-----------------------------------------------------------------------------+
| Enable Switch Port Trunk      | ``openstack esi switch port enable trunk <switch> <switchport> <vlan_id>``  |
+-------------------------------+-----------------------------------------------------------------------------+
| Disable Switch Port Trunk     | ``openstack esi switch port disable trunk <switch> <switchport>``           |
+-------------------------------+-----------------------------------------------------------------------------+
| Enable Switch Port Access     | ``openstack esi switch port enable access <switch> <switchport> <vlan_id>`` |
+-------------------------------+-----------------------------------------------------------------------------+
| Disable Switch Port Access    | ``openstack esi switch port disable access <switch> <switchport>``          |
+-------------------------------+-----------------------------------------------------------------------------+

Node/Lease Information
~~~~~~~~~~~~~~~~~~~~~~

+------------------------------+-----------------------------+
|                              | **Actions**                 |
+------------------------------+-----------------------------+
| List Nodes with Lease Status | ``openstack esi node list`` |
+------------------------------+-----------------------------+

Node/Network Management
~~~~~~~~~~~~~~~~~~~~~~~

+-------------------------------+------------------------------------------------------------------------------------------------------+
|                               | **Actions**                                                                                          |
+-------------------------------+------------------------------------------------------------------------------------------------------+
| List Node/Network Attachments | ``openstack esi node network list``                                                                  |
+-------------------------------+------------------------------------------------------------------------------------------------------+
| Attach Network to Node        | ``openstack esi node network attach (--network <network> | --port <port> | --trunk <trunk>) <node>`` |
+-------------------------------+------------------------------------------------------------------------------------------------------+
| Detach Network from Node      | ``openstack esi node network detach --port <port> <node>``                                           |
+-------------------------------+------------------------------------------------------------------------------------------------------+

Boot Node from Volume
~~~~~~~~~~~~~~~~~~~~~

+-----------------------+--------------------------------------------------------------------------------------------+
|                       | **Actions**                                                                                |
+-----------------------+--------------------------------------------------------------------------------------------+
| Boot Node from Volume | ``openstack esi node volume attach (--network <network> | --port <port>) <node> <volume>`` |
+-----------------------+--------------------------------------------------------------------------------------------+

Set Node Boot Device
~~~~~~~~~~~~~~~~~~~~

+----------------------+-----------------------------------------------------------------------------------------------------+
|                      | **Actions**                                                                                         |
+----------------------+-----------------------------------------------------------------------------------------------------+
| Set Node Boot Device | ``openstack baremetal node boot device set <node> bios|cdrom|disk|pxe|safe|wanboot (--persistent)`` |
+----------------------+-----------------------------------------------------------------------------------------------------+

If the ``--persistent`` flag is not used, the node will only boot from the specified device once. If the ``--persistent`` flag is used, the node will boot from the specified device until the node is cleaned.

Trunk Ports
~~~~~~~~~~~

+--------------------------------+------------------------------------------------------------------------------------------------------------+
|                                | **Actions**                                                                                                |
+--------------------------------+------------------------------------------------------------------------------------------------------------+
| List Trunk Ports               | ``openstack esi trunk list``                                                                               |
+--------------------------------+------------------------------------------------------------------------------------------------------------+
| Create Trunk Port              | ``openstack esi trunk create --native-network <native-network> --tagged-networks <tagged-network> <name>`` |
+--------------------------------+------------------------------------------------------------------------------------------------------------+
| Add Network to Trunk Port      | ``openstack esi trunk add network --tagged-networks <tagged-network> <name>``                              |
+--------------------------------+------------------------------------------------------------------------------------------------------------+
| Remove Network from Trunk Port | ``openstack esi trunk remove network --tagged-networks <tagged-network> <name>``                           |
+--------------------------------+------------------------------------------------------------------------------------------------------------+
| Delete Trunk Port              | ``openstack esi trunk delete <name>``                                                                      |
+--------------------------------+------------------------------------------------------------------------------------------------------------+

.. _Ironic CLI reference: https://docs.openstack.org/python-ironicclient/latest/cli/osc_plugin_cli.html
.. _ESI Leap: https://github.com/CCI-MOC/esi-leap
.. _Metalsmith: https://docs.openstack.org/metalsmith/latest/
.. _Ironic boot-from-volume documentation: https://docs.openstack.org/ironic/latest/admin/boot-from-volume.html
.. _python-esiclient: https://github.com/CCI-MOC/python-esiclient
.. _python-esileapclient: https://github.com/CCI-MOC/python-esileapclient
.. _Configuring Web or Serial Console: https://docs.openstack.org/ironic/latest/admin/console.html
