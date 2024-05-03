New User Guide
==============

Prerequisites
-------------

The first step is to gain access to an ESI installation. After you do, the ESI operator will send you credentials and instructions regarding how to access your account.

Afterwards you'll need to install the ESI clients. It is recommended that you do so within a python virtual environment:

  .. prompt:: bash $

    python3 -mvenv .venv
    source .venv/bin/activate

To install the ESI clients, run the following:

  .. prompt:: bash (.venv)$

    pip install python-esiclient
    pip install python-esileapclient

Viewing Your Nodes
------------------

The ESI operator will have given you access to nodes. In order to view them, you can run one of the following:

  .. prompt:: bash (.venv)$

    openstack baremetal node list          # Ironic's node list command
    openstack esi node list                # ESI's node list command with leasing information
    openstack esi node network list        # ESI's node list command with node network information

To view additional details about a node, run:

  .. prompt:: bash (.venv)$

    openstack baremetal node show <node ID>   # The node ID can be its name or UUID

Node Provisioning States (and what they mean)
---------------------------------------------

``openstack baremetal node list`` and ``openstack esi node list`` both display a node's provisioning state. These states determine what actions can be performed upon a node.

* **manage**: node is configured and ready to be cleaned
* **available**: node has been cleaned and is ready for deployment
* **active**: node has been deployed
* **cleaning**: node is in the process of being cleaned before being returned to the **available** state

There are also transitionary states that indicate a node is in the process of moving from one state to another.

Configuring Your Networks
-------------------------

Your ESI installation may have networks available for use; for example, the `provisioning` network will often already be created by the operator. However you may also want to configure private networks, accessible only by your project. For details on the options available, read the `documentation regarding private networks`_ and talk to your ESI operator.

Configuring and Deploying Your Nodes
------------------------------------

A node in the **available** state can be configured and deployed. There are multiple options for doing so:

* To provision individual nodes, use the instructions detailed in `documentation for provisioning a node`_.
* To provision a cluster all at once, use the instructions detailed in `documentation for provisioning a cluster`_.

Accessing Your Nodes
--------------------

Once a node is provisioned, there are multiple scenarios for accessing the node explained in the `network scenarios documentation`_. You can view the networking configuration of your nodes at any time by running ``openstack esi node network list``.

Cleaning Your Nodes
-------------------

If you wish to undeploy an **active** node and return it to the **available** state, run the following:

  .. prompt:: bash (.venv)$

    openstack baremetal node undeploy <node ID>  # The node ID can be its name or UUID

If you provisioned the node using metalsmith, run this command instead:

  .. prompt:: bash (.venv)$

    metalsmith undeploy <node ID>                # The node ID can be its name or UUID

These commands will kick off the node cleaning process. Once cleaning is complete, the node will return to the **available** state.

Further Information
-------------------

OpenStack has a vast and powerful toolset. Some of those additional options are `detailed in the ESI documentation`_; a more comprehensive list can be found in the `OpenStack Ironic documentation`_.

If you have suggestions for improving this guide, please `contact us`_!

.. _documentation regarding private networks: network_scenarios.html#private-networks
.. _documentation for provisioning a node: cli.html#provisioning-a-node
.. _documentation for provisioning a cluster: cluster.html
.. _detailed in the ESI documentation: index.html#general-information
.. _OpenStack Ironic documentation: https://docs.openstack.org/ironic/latest/
.. _network scenarios documentation: network_scenarios.html
.. _contact us: ../contact-us.html
