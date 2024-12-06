Installing OpenShift on ESI
===========================

.. raw:: html

   <iframe width="560" height="315" src="https://www.youtube.com/embed/tvd0bwT1BC8" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

Owners and lessees can easily install OpenShift on hardware managed through ESI through the use of the `OpenShift Assisted Installer`_. This guide assumes that the relevant roles have been granted access to the required Ironic actions.

There are two methods of using the Assisted Installer to install OpenShift: through the web UI, and through a CLI using `python-esiclient`_. Both methods have the same initial prerequisites.

Prerequisites
-------------

* Access to the OpenShift Assisted Installer
   * You may use https://console.redhat.com or a local installation of the OpenShift Assisted Installer
* Access to Ironic's provisioning network (this will likely already exist with the name `provisioning`)
* `Access to an external network`_
* A `private network`_ with an `OpenStack router`_ for external network access and floating IP capabilities and a `private DNS server`_ for your private network
* Usage of ESI-managed nodes in the 'available' state

The Ironic provisioning network must also be able to reach the Assisted Installer. If using https://console.redhat.com, an ESI administrator can configure this access with an external network and an OpenStack router:

  .. prompt:: bash $

    openstack router create provisioning-router
    openstack router set --external-gateway <external network> provisioning-router
    openstack router add subnet provisioning-router <provisioning subnet>

Using the Assisted Installer Web UI
-----------------------------------

Prepare Cluster on Assisted Installer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Log onto the Assisted Installer and select 'OpenShift' from the menu
* Click on 'Create Cluster', select the 'Datacenter' tab, and create a cluster from the 'Assisted Installer' subsection
* Input 'Cluster details' and click 'Next'
   * If you're only using a single node, click the 'Install single node OpenShift (SNO)' checkbox
* In the 'Host discovery' step, click the 'Add hosts' button
   * Select 'Minimal image file: Provision with virtual media'
   * Input your SSH public key
   * Click 'Generate Discovery ISO' and record the Discovery ISO URL

Configure Ironic Nodes
~~~~~~~~~~~~~~~~~~~~~~

* Run these commands to configure your nodes to boot from the generated OpenShift ISO:

  .. prompt:: bash $

    openstack baremetal node set --instance-info deploy_interface=ramdisk <node>
    openstack baremetal node set --instance-info boot_iso=<discovery iso url> <node>

* Attach the node to Ironic's provisioning network:

  .. prompt:: bash $

    openstack esi node network attach --network <provisioning network> <node>


Deploy
~~~~~~

* Once your nodes are ready, run the deploy command:

  .. prompt:: bash $

    openstack baremetal node deploy <node>

* Wait for the nodes to appear on the Assisted Installer as Ready. Once they do, switch the nodes to your private network and configure them to boot from disk:

  .. prompt:: bash $

    openstack esi node network list    # find names of ports attached to nodes
    openstack esi node network detach --port <port> <node>
    openstack esi node network attach --network <private network> <node>
    openstack baremetal node boot device set <node> disk --persistent

* Wait for the nodes to be Ready again. Once they are, select your nodes and click 'Next'.
* In the 'Networking' step, assign an API IP and an Ingress IP. These IPs should be in your private subnet range, outside of its allocation pool. Wait for the nodes in the 'Host inventory' section to be Ready (this may take a few minutes). Once they are, click 'Next'.
* In the 'Review and create' step, verify your installation parameters. Click 'Install cluster' when ready.
* Installation will begin and eventually complete. Once it does, the Assisted Installer will have credentials for logging into your OpenShift console.

Post Install
~~~~~~~~~~~~

* Allow external access to your API IP and Ingress IP as follows:

  .. prompt:: bash $

    openstack port create \
              --network <private network> \
              --fixed-ip subnet=<private subnet>,ip-address=<internal api ip> \
              <port name for api>
    openstack floating ip create external
    openstack floating ip set --port <port name for api> <external floating ip for api>

    openstack port create \
              --network <private network> \
              --fixed-ip subnet=<private subnet>,ip-address=<internal ingress ip> \
              <port name for ingress>
    openstack floating ip create external
    openstack floating ip set --port <port name for ingress> <external floating ip for ingress>

* Configure public DNS as required using the external floating IPs.
* Configure private DNS as required using the internal IPs.

Add Hosts
~~~~~~~~~

* Log onto the Assisted Installer, select 'Clusters', and click on your cluster.
* Navigate to the 'Add Hosts' tab.
* Click on the 'Add hosts' button.
   * Select 'Minimal image file: Provision with virtual media'
   * Input your SSH public key
   * Click 'Generate Discovery ISO' and record the Discovery ISO URL
* Run these commands to configure your nodes to boot from the generated OpenShift ISO and to attach it to the provisioning network:

  .. prompt:: bash $

    openstack baremetal node set --instance-info deploy_interface=ramdisk <node>
    openstack baremetal node set --instance-info boot_iso=<discovery iso url> <node>
    openstack esi node network attach --network <provisioning network> <node>

* Deploy the nodes:

  .. prompt:: bash $

    openstack baremetal node deploy <node>

* Wait for the nodes to appear on the Assisted Installer. Once they do, switch the nodes to your private network and configure them to boot from disk:

  .. prompt:: bash $

    openstack esi node network list    # find names of ports attached to nodes
    openstack esi node network detach --port <port> <node>
    openstack esi node network attach --network <private network> <node>
    openstack baremetal node boot device set <node> disk --persistent

* Wait for the nodes to be Ready. In order to do so, you may have to do the following:
   * Assign an external floating IP to the node and log in as the `core` user.
   * Restart the OpenShift validations with the command  `sudo podman container restart next-step-runner`
* Once the nodes are Ready, click 'Install ready hosts'.
   * The installation is complete when the nodes' statuses change to Installed.
* From your OpenShift cluster console, navigate to 'Compute > Nodes'.
   * The new nodes will appear there as Discovered.
   * Click on their statuses to approve their CSRs.

Remove Hosts
~~~~~~~~~~~~

* Follow the Openshift documentation for `deleting nodes from a cluster`_.
* For each node that was removed, run `openstack baremetal node undeploy <node>`

Using the python-esiclient CLI
------------------------------

Configure Access to the Assisted Installer API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The python-esiclient CLI commands requires the user to access the Assisted Installer API. In order to do so, the user must `follow the steps in the Assisted Installer API documentation`_ which detail how to create a ``refresh-token`` script and how to export a ``PULL_SECRET`` to your environment.

Create a Cluster Configuration File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A cluster configuration file contains the following:

.. prompt::

  {
      "cluster_name": "name-of-cluster",
      "openshift_version": "4.13.12",
      "high_availability_mode": "Full",
      "base_dns_domain": "your.dns",
      "api_vip": "aaa.aa.aa.aaa",                  // a free IP on your private subnet
      "ingress_vip": "bbb.bb.bb.bbb",              // a free IP on your private subnet
      "ssh_public_key": "public-key",              // the content of the public key file (not just the path to the key)
      "external_network_name": "external",
      "private_network_name": "private-network",
      "private_subnet_name": "private-subnet",
      "nodes": ["node1", "node2", "node3"]
  }

Orchestrate the Cluster
~~~~~~~~~~~~~~~~~~~~~~~

+---------------------+-----------------------------------------------------------------------+
|                     | **Actions**                                                           |
+---------------------+-----------------------------------------------------------------------+
| Orchestrate Cluster | ``openstack esi openshift orchestrate <path-to-cluster-config-file>`` |
+---------------------+-----------------------------------------------------------------------+

Once the cluster config file is created, run ``refresh-token`` and then ``openstack esi openshift orchestrate`` to start the orchestration of the OpenShift cluster.

Installation will take roughly an hour, and involves constant calls to the Assisted Installer API. However, the token from ``refresh-token`` will expire after 15 minutes. When this happens, the orchestration command will fail. Fortunately, it will do so while providing a command to continue installation:

.. prompt::

  * YOU MAY NEED TO REFRESH YOUR OPENSHIFT API TOKEN
  Run this command to continue installation:
  openstack esi orchestrate openshift --cluster-id the-generated-cluster-id --infra-env-id the-generated-infra-env-id

If you see this message, simply run ``refresh-token`` again and then copy and paste the specified command.

Undeploy the Cluster
~~~~~~~~~~~~~~~~~~~~

+------------------+--------------------------------------------------------------------+
|                  | **Actions**                                                        |
+------------------+--------------------------------------------------------------------+
| Undeploy Cluster | ``openstack esi openshift undeploy <path-to-cluster-config-file>`` |
+------------------+--------------------------------------------------------------------+

To undeploy the OpenShift cluster, run the above command while passing in the same cluster configuration file used to orchestrate it. This ensures that any associated resources will be removed, freeing up quota.

.. _Access to an external network: https://esi.readthedocs.io/en/latest/install/external_network.html
.. _private network: https://esi.readthedocs.io/en/latest/usage/network_scenarios.html#private-networks
.. _OpenStack router: https://esi.readthedocs.io/en/latest/usage/network_scenarios.html#routers
.. _private DNS server: https://esi.readthedocs.io/en/latest/usage/network_scenarios.html#private-dns
.. _OpenShift Assisted Installer: https://cloud.redhat.com/blog/using-the-openshift-assisted-installer-service-to-deploy-an-openshift-cluster-on-metal-and-vsphere
.. _deleting nodes from a cluster: https://docs.openshift.com/container-platform/4.11/nodes/nodes/nodes-nodes-working.html#deleting-nodes
.. _python-esiclient: https://github.com/CCI-MOC/python-esiclient
.. _follow the steps in the Assisted Installer API documentation: https://access.redhat.com/documentation/en-us/assisted_installer_for_openshift_container_platform/2023/html/assisted_installer_for_openshift_container_platform/installing-with-api
