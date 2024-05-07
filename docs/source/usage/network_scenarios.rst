Network Scenarios
=================

.. raw:: html

   <iframe width="560" height="315" src="https://www.youtube.com/embed/1WfE1g-gygk" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

Private Networks
----------------

If a lessee wishes to use a private network, they can run the following commands:

  .. prompt:: bash $

    openstack network create <network name>
    openstack subnet create --subnet-range <subnet range> --allocation-pool start=<allocation start>,end=<allocation end> --network <network name> <subnet name>

The created network will automatically have an assigned VLAN. This network can then be attached to a node as follows:

  .. prompt:: bash $

    openstack esi node network attach --network <network name> <node>

Note that a node must be active in order for this network configuration to be reflected upon the switch. OpenStack provisioning tools will often do this for you, but if you wish to use your own provisioning tools then run the following:

  .. prompt:: bash $

    openstack baremetal node manage <node>
    openstack baremetal node adopt <node>

In order for the lessee to access a node on a private network, they can use of the following options:

* Contact the ESI administrator to connect the VLAN to an accessible node or VM outside of ESI
* Use a trunk port whose native network is a VLAN that the lessee can already access - usually a public or external network - and which has a tagged network corresponding to the private network. That can be configured as follows:

  .. prompt:: bash $

    openstack esi trunk create --native-network <accessible network> <trunk name>
    openstack esi trunk add network --tagged-networks <private network> <trunk name>
    openstack esi node network attach --trunk <trunk name> <node>

* Use a floating IP on an external network as described `below`_

Private DNS
~~~~~~~~~~~

If you require a private DNS server for your private network, you can configure one on a node in your private network. Once that's done, configure your private subnet:

  .. prompt:: bash $

    openstack subnet set --dns-nameserver <dns server ip> <private subnet>

External Networks
-----------------

An external network must be configured by an ESI administrator as described `here`_. Once that's done, a lessee can provision a node upon their private network and then gain external network access using one of these methods.

Routers
~~~~~~~

An OpenStack router allows you to give nodes on your private subnet external network access.

  .. prompt:: bash $

    openstack router create external-router
    openstack router set --external-gateway <external network> external-router
    openstack router add subnet external-router <private subnet>

Floating IPs
~~~~~~~~~~~~

The use of floating IPs requires the following:

* The private network's VLAN must be configured as a tagged network on the switch port for each controller.
* An OpenStack router must be configured as described above.

Once these requirements are in place, you can create a floating IP:

  .. prompt:: bash $

    openstack floating ip create <external network>

Next, associate it with a provisioned node's Neutron port (which can be found by running ``openstack esi node network list``). You can do so
indiscriminately, allowing all network traffic to be forwarded through the floating IP:

  .. prompt:: bash $

    openstack floating ip set --port <port> <external floating ip>

Alternatively, you can constrain the forwarding to specific ports; for example, the following limits access to SSH:

  .. prompt:: bash $

    openstack floating ip port forwarding create \
      --port <port> \
      --internal-protocol-port 22 \
      --external-protocol-port 22 \
      --internal-ip-address <private fixed ip>  \
      --protocol tcp <external floating ip>


If your private network has an alternative mechanism for assigning IPs, you can manually creating a Neutron port associated with that IP before assigning a floating IP:

  .. prompt:: bash $

    openstack port create --network <private network> \
                          --fixed-ip subnet=<private subnet>,ip-address=<private ip address> \
                          <port name>

Direct Connection
~~~~~~~~~~~~~~~~~

If you do not need access to a private network, you can simply attach the external network to the node:

  .. prompt:: bash $

    openstack esi node network detach --port <port> <node>
    openstack esi node network attach --network <external name> <node>


Direct Connection - Trunk Port
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you need access to multiple networks through a single NIC, you can use a trunk port:

  .. prompt:: bash $

    openstack esi trunk create --native-network <private network> <trunk name>
    openstack esi trunk add network --tagged-networks <external network> <trunk name>
    openstack esi node network attach --trunk <trunk name> <node>

Access the node through the private network or a serial console, and create a new network interface configuration for the external network.

.. _below: https://esi.readthedocs.io/en/latest/usage/network_scenarios.html#external-networks
.. _here: https://esi.readthedocs.io/en/latest/install/external_network.html
