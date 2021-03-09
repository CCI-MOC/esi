Usage
=====

ESI accommodates three roles:

* **Admin**
   * Views and administrates the entire inventory of nodes.
   * Assigns owners and lessees to nodes.
* **Owner**
   * Views and administrates the nodes that they own.
   * Has exclusive use of their nodes, except for those that they choose to lease.
   * Assigns lessees to the nodes that they own.
   * Creates offers for their nodes, making them available for lease.
   * *Note:* The owner role is optional; every action they do can also be performed by an admin.
* **Lessee**
   * Can only view nodes that they have leased.
   * Has temporary use of their nodes for the duration of the lease.
   * Contracts out a node from an available offer.

Once a node is assigned to an owner or lessee, they can use existing OpenStack CLI commands to work with that node (as limited by Ironic policy); see the `Ironic CLI reference`_ for more information.

Additional commands that may be of use are listed here.

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

Node owners can offer up their nodes for lease for a given time period. Unoffered nodes will not be seen by lessees.

+--------------+------------------------------------------------------------------------------------------------------------------------------------------+
|              | **Owner Actions**                                                                                                                        |
+--------------+------------------------------------------------------------------------------------------------------------------------------------------+
| Create Offer | ``openstack lease offer create --resource-type ironic_node --resource_uuid <node_uuid> --start-time <start_time> --end-time <end_time>`` |
+--------------+------------------------------------------------------------------------------------------------------------------------------------------+
| View Offer   | ``openstack lease offer show <offer_uuid>``                                                                                              |
+--------------+------------------------------------------------------------------------------------------------------------------------------------------+
| Delete Offer | ``openstack lease offer delete <offer_uuid>``                                                                                            |
+--------------+------------------------------------------------------------------------------------------------------------------------------------------+

**Lessee Actions**

Users can view available offers and contract a node from an offer.

+-----------------+----------------------------------------------------------------------------------------------------------+
|                 | **Lessee Actions**                                                                                       |
+-----------------+----------------------------------------------------------------------------------------------------------+
| List Offers     | ``openstack lease offer list``                                                                           |
+-----------------+----------------------------------------------------------------------------------------------------------+
| Create Contract | ``openstack lease contract create --offer <offer_uuid> --start-time <start_time> --end-time <end_time>`` |
+-----------------+----------------------------------------------------------------------------------------------------------+
| List Contracts  | ``openstack lease contract list``                                                                        |
+-----------------+----------------------------------------------------------------------------------------------------------+
| Show Contract   | ``openstack lease contract show <contract_uuid>``                                                        |
+-----------------+----------------------------------------------------------------------------------------------------------+
| Delete Contract | ``openstack lease contract delete <contract_uuid>``                                                      |
+-----------------+----------------------------------------------------------------------------------------------------------+

Provisioning a Node
-------------------

There are multiple ways for a non-admin to provision a node.

Image
~~~~~

Image-based provisioning can be accomplished through the use of `Metalsmith`_. It requires the image to be uploaded into OpenStack Glance. Once that's done, a non-admin can run the following:

+----------------+---------------------------------------------------------------------------------------------------------------------+
|                | **Actions**                                                                                                         |
+----------------+---------------------------------------------------------------------------------------------------------------------+
| Provision Node | ``metalsmith deploy --resource-class baremetal --image <image> --network <network> --ssh-public-key <path-to-key>`` |
+----------------+---------------------------------------------------------------------------------------------------------------------+

Volume
~~~~~~

The process for booting a node from a volume is described in the `Ironic boot-from-volume documentation`_. There are two things to note for non-admin deployments:

* The node owner or admin should set the `iscsi_boot` node capability prior to leasing the node.
* The node lessee should not be allowed to edit the `storage_interface` node attribute. Instead, they can run the following command to temporarily override that value (until the node is cleaned):

+----------------------------+----------------------------------------------------------------------------------+
|                            | **Actions**                                                                      |
+----------------------------+----------------------------------------------------------------------------------+
| Override Storage Interface | ``openstack baremetal node set --instance-info storage_interface=cinder <node>`` |
+----------------------------+----------------------------------------------------------------------------------+

External Provisioning
~~~~~~~~~~~~~~~~~~~~~

In order to use an external provisioning service, simply attach the node to the appropriate network. You can do so through OpenStack Neutron and Ironic CLI commands; or use `python-esiclient`_:

+-------------------------------+------------------------------------------------------------------------------------+
|                               | **Actions**                                                                        |
+-------------------------------+------------------------------------------------------------------------------------+
| Attach Network to Node        | ``openstack esi node network attach (--network <network> | --port <port>) <node>`` |
+-------------------------------+------------------------------------------------------------------------------------+


Additional ESI CLI Actions
--------------------------

`python-esiclient`_ provides additional commands that combine multiple OpenStack CLI functions into a single action.

Node/Network Management
~~~~~~~~~~~~~~~~~~~~~~~

+-------------------------------+------------------------------------------------------------------------------------+
|                               | **Actions**                                                                        |
+-------------------------------+------------------------------------------------------------------------------------+
| List Node/Network Attachments | ``openstack esi node network list``                                                |
+-------------------------------+------------------------------------------------------------------------------------+
| Attach Network to Node        | ``openstack esi node network attach (--network <network> | --port <port>) <node>`` |
+-------------------------------+------------------------------------------------------------------------------------+
| Detach Network from Node      | ``openstack esi node network detach <node> <port>``                                |
+-------------------------------+------------------------------------------------------------------------------------+

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
