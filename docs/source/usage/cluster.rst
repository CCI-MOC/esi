Installing a Cluster on ESI
===========================

A lessee wishing to create a cluster out of multiple leased nodes and a private network can do so by running the correct `CLI commands`_. Alternatively, they can use the cluster CLI commands in `python-esiclient`_ to simplify the workflow involved in creating and managing their clusters.

Prerequisites
-------------

* `python-esiclient`_ must be installed
* The nodes in the cluster must use image-based provisioning, with the image listed with ``openstack image list``

Orchestrating the Cluster
-------------------------

+---------------------+---------------------------------------------------------------------+
|                     | **Actions**                                                         |
+---------------------+---------------------------------------------------------------------+
| Orchestrate Cluster | ``openstack esi cluster orchestrate <path-to-cluster-config-file>`` |
+---------------------+---------------------------------------------------------------------+

A single command is sufficient to provision a bare metal cluster and configure its networking.

Cluster Configuration File
~~~~~~~~~~~~~~~~~~~~~~~~~~

A sample cluster configuration file is provided here:

.. prompt::

  {
      "node_configs": [
	  {
	      "nodes": {
		  "node_uuids": ["node1"]
	      },
	      "network": {
		  "network_uuid": "private-network-1",
		  "tagged_network_uuids": ["private-network-2"],
		  "fip_network_uuid": "external"
	      },
	      "provisioning": {
		  "provisioning_type": "image",
		  "image_uuid": "image-name",
		  "ssh_key": "/path/to/ssh/key"
	      }
	  },
	  {
	      "nodes": {
		  "num_nodes": "2",
		  "resource_class": "node-resource-class"
	      },
	      "network": {
		  "network_uuid": "private-network-1"
	      },
	      "provisioning": {
		  "provisioning_type": "image",
		  "image_uuid": "image-name-2",
		  "ssh_key": "/path/to/ssh/key"
	      }
	  }
      ]
  }

The config file consists of one or more ``node_configs`` sections, each of which contains the following:

nodes
^^^^^

The ``nodes`` section identifies which nodes will be used. You can either specifiy specific nodes by name or UUID:

.. prompt::

  "nodes": {
     "node_uuids": ["node1"]
  }

Or look for a given number of nodes of a specific resource class:

.. prompt::

  "nodes": {
     "num_nodes": 2,
     "resource_class": "node-resource-class"
  }

If the requested nodes cannot be found, the orchestration command will throw an error.

network
^^^^^^^

The ``network`` section details how nodes will be networked. Only the ``network_uuid`` attribute is required.

.. prompt::

  "network": {
     "network_uuid": "private-network-1"
  }

There are two optional attributes that can be specified. ``tagged_network_uuids`` creates a trunk port with the network specified in ``network_uuid`` and the networks specified in ``tagged_network_uuids``; and ``fip_network_uuid`` creates a floating IP on the specified network attached to the node. 

.. prompt::

  "network": {
     "network_uuid": "private-network-1"
     "tagged_network_uuids": ["private-network-2"],
     "fip_network_uuid": "external"
  }

provisioning
^^^^^^^^^^^^

The ``provisioning`` section details how nodes will be provisioned. Currently only image-based provisioning is supported; all the listed attributes are required.

.. prompt::

  "provisioning": {
     "provisioning_type": "image",
     "image_uuid": "image-name",
     "ssh_key": "/path/to/ssh/key"
  }

Listing Clusters
----------------

+---------------+--------------------------------+
|               | **Actions**                    |
+---------------+--------------------------------+
| List Clusters | ``openstack esi cluster list`` |
+---------------+--------------------------------+

This command lists all your clusters, along with each cluster's associated nodes and each node's associated resources (ports, floating IPs, etc).

Undeploying a Cluster
---------------------

+------------------+---------------------------------------------------+
|                  | **Actions**                                       |
+------------------+---------------------------------------------------+
| Undeploy Cluster | ``openstack esi cluster undeploy <cluster-uuid>`` |
+------------------+---------------------------------------------------+

This command undeploys a cluster by undeploying all nodes and deleting all associated resources. Cluster UUIDs can be found by running ``openstack esi cluster list``.

Using this command is highly recommended, as it ensures resources are freed up so they no longer count against your quota.


.. _CLI commands: cli.html
.. _python-esiclient: https://github.com/CCI-MOC/python-esiclient
