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

Assigning Owners
----------------

**Admin Actions**

* Assign Node Owner: ``openstack baremetal node set --owner <project_id> <node_name_or_uuid>``
* Unassign Node Owner: ``openstack baremetal node unset --owner <node_name_or_uuid>``


Leasing Workflows
-----------------

There are two possible node leasing workflows.

Simple Workflow
~~~~~~~~~~~~~~~

In the simple case, node lessees are managed directly by admins and owners, who assign and unassign
nodes to a project as they see fit. This workflow does not require any custom ESI services.

**Admin/Owner Actions**

* Assign Node Lessee: ``openstack baremetal node set --lessee <project_id> <node_name_or_uuid>``
* Unassign Node Lessee: ``openstack baremetal node unset --lessee <node_name_or_uuid>``

ESI Leasing Workflow
~~~~~~~~~~~~~~~~~~~~

If `ESI Leap`_ is installed, then node leases can also be managed as follows:

**Owner Actions**

Node owners can offer up their nodes for lease. Unoffered nodes will not be seen by lessees.

* Create Offer: ``openstack lease offer create --resource-type ironic_node --resource_uuid <node_uuid> --start-time <start_time> --end-time <end_time>``
* View Offer: ``openstack lease offer show <offer_uuid>``
* Delete Offer: ``openstack lease offer delete <offer_uuid>``

**Lessee Actions**

Users can view available offers and contract a node from an offer.

* List Offers: ``openstack lease offer list``
* Create Contract: ``openstack lease contract create --offer <offer_uuid> --start-time <start_time> --end-time <end_time>``
* List Contracts: ``openstack lease contract list``
* Show Contract: ``openstack lease contract show <contract_uuid>``
* Delete Contract: ``openstack lease contract delete <contract_uuid>``

Additional ESI CLI Actions
--------------------------

Additional commands are provided by `python-esiclient`_.

.. _ESI Leap: https://github.com/CCI-MOC/esi-leap
.. _python-esiclient: https://github.com/CCI-MOC/python-esiclient
