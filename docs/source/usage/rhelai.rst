Installing RHELAI on ESI
========================

Prerequisites
-------------

* Access to Ironic's provisioning network (this will likely already exist with the name `provisioning`)
* `Access to an external network`_
* A `private network`_ with an `OpenStack router`_ for external network access and floating IP capabilities
* Usage of an ESI-managed GPU node in the 'available' state
* A RHELAI image available in Glance

Provisioning the Node with the RHELAI Image
-------------------------------------------

* Run Metalsmith to provision the node with the RHELAI image:

  .. prompt:: bash $

    metalsmith deploy --resource-class <node resource class> --image <image> --network <network> --candidate <node id> --ssh-public-key <path-to-key>

* `Attach an external floating IP to the port`_

Using RHELAI
------------

* Access your node through the attached floating IP

  .. prompt:: bash $

    ssh cloud-user@<floating IP>

* `Follow the RHELAI documentation`_

.. _Access to an external network: https://esi.readthedocs.io/en/latest/install/external_network.html
.. _private network: https://esi.readthedocs.io/en/latest/usage/network_scenarios.html#private-networks
.. _OpenStack router: https://esi.readthedocs.io/en/latest/usage/network_scenarios.html#routers
.. _Attach an external floating IP to the port: https://esi.readthedocs.io/en/latest/usage/network_scenarios.html#floating-ips
.. _Follow the RHELAI documentation: https://docs.redhat.com/en/documentation/red_hat_enterprise_linux_ai/
