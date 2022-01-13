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
   * Obtains a lease on a node by claiming an available offer.

.. toctree::
   :maxdepth: 2

   cli
   openshift
   keylime
   security_recommendations
