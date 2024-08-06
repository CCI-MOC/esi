Deploying ESI on DevStack
=========================

This covers the steps to create a development deployment of ESI with DevStack, including setting up DevStack with Ironic integration and creating fake nodes in Ironic.

.. contents:: Table of Contents
   :depth: 2
   :local:

Prerequisites
-------------

- VM or bare metal node provisioned with Ubuntu 22.04.
- You can download the Ubuntu 22.04 image from the official Ubuntu website: `Download Ubuntu 22.04`_.
- For a list of DevStack-compatible images, visit the `DevStack documentation`_.
- The following instructions are specific to Ubuntu.


Prepare the Environment
-----------------------

**Update and upgrade the system packages:**

.. prompt:: bash $

   sudo apt update
   sudo apt upgrade -y
   sudo apt install -y git vim sudo curl

**Verify Network Connectivity:**

First, check if your instance has an active network connection by trying to ping a public IP address:

.. prompt:: bash $

   ping 8.8.8.8

**Check DNS Configuration:**

Ensure that your `/etc/resolv.conf` file is correctly configured with valid DNS servers. You can use Google's public DNS servers as a fallback:

.. prompt:: bash $

   sudo nano /etc/resolv.conf

Add the following lines if they are not present:

.. code-block:: text

   nameserver 8.8.8.8
   nameserver 8.8.4.4

**Restart Network Services:**

Restart the network manager to apply any changes made to the DNS configuration:

.. prompt:: bash $

   sudo systemctl restart network-manager

**Update the system:**

.. prompt:: bash $

   sudo apt update -y
   sudo apt upgrade -y

**Install Git:**

.. prompt:: bash $

   sudo apt install git -y

Install DevStack and Configure Ironic:
--------------------------------------

**Clone the DevStack repository:**

.. prompt:: bash $

   git clone https://opendev.org/openstack/devstack.git

**Create the 'stack' user:**

.. prompt:: bash $

   sudo ./devstack/tools/create-stack-user.sh

**Change permissions for the /opt/stack directory:**

.. prompt:: bash $

   sudo chmod 755 /opt/stack
   # Alternatively, if the above doesn't work:
   # sudo chmod +x /opt/stack

**Copy DevStack to the /opt/stack directory:**

.. prompt:: bash $

   sudo cp -r devstack /opt/stack
   sudo chown -R stack:stack /opt/stack/devstack

**Switch to the 'stack' user:**

.. prompt:: bash $

   sudo su - stack

**Navigate to the /opt/stack directory:**

.. prompt:: bash $

   cd /opt/stack

**Navigate to the DevStack directory:**

.. prompt:: bash $

   cd devstack

**Create a `local.conf` file with the following content:**

.. code-block:: ini

   [[local|localrc]]
   ADMIN_PASSWORD=secret
   DATABASE_PASSWORD=$ADMIN_PASSWORD
   RABBIT_PASSWORD=$ADMIN_PASSWORD
   SERVICE_PASSWORD=$ADMIN_PASSWORD

   # Enable Ironic
   enable_service ironic-api
   enable_service ironic-cond

   # More settings needs to be added. For a full example, see the Ironic DevStack Guide.

Copy the Ironic local.conf file from the `Ironic DevStack Guide`_.

**Run the DevStack setup script:**

.. prompt:: bash $

   bash stack.sh
   source ~/devstack/openrc admin admin

**Clean and Uninstall:**

If you might consider cleaning up the DevStack installation and starting fresh:

.. prompt:: bash $

   cd /opt/stack/devstack
   ./unstack.sh
   ./clean.sh
   ./stack.sh

Creating Fake Nodes with Ironic
-------------------------------

To configure the fake-hardware hardware type with the specified delays, you need to add the configuration settings to your Ironic configuration file. Follow these steps to configure and manage fake nodes:

1. **Edit the Ironic Configuration File:**

   Open the Ironic configuration file in a text editor:

   .. prompt:: bash $

     sudo nano /etc/ironic/ironic.conf

   Add the following section at the end of the file to configure the fake delays:

   .. code-block:: ini

     [fake]
     power_delay = 5
     boot_delay = 10
     deploy_delay = 60,360
     vendor_delay = 1
     management_delay = 5
     inspect_delay = 360,480
     raid_delay = 10
     bios_delay = 5
     storage_delay = 10
     rescue_delay = 120

2. **Restart the Ironic Services:**

   After editing the configuration file, restart the Ironic services to apply the changes:

   .. prompt:: bash $

     sudo systemctl restart openstack-ironic-api
     sudo systemctl restart openstack-ironic-conductor

3. **Create the Baremetal Node with Fake Hardware:**

   Create the node with the fake-hardware driver:

   .. prompt:: bash $

     openstack baremetal node create --name <node-name> --driver fake-hardware

   Set the node properties:

   .. prompt:: bash $

     openstack baremetal node set <node-name> --property cpu_arch=x86_64 --property cpus=4 --property memory_mb=8192 --property local_gb=100

4. **Enroll and Provide the Node:**

   Enroll the node:

   .. prompt:: bash $

     openstack baremetal node manage <node-name>

   Provide the node:

   .. prompt:: bash $

     openstack baremetal node provide <node-name>

5. **Verify the Node Creation:**

   To verify that the node has been created and is in the correct state, use the following command:

   .. prompt:: bash $

     openstack baremetal node list

Install ESI-Leap
----------------

- For instructions on installing ESI-Leap, please follow the instructions in the `ESI-Leap GitHub repository`_.
- For information on the ESI-Leap command line client, visit the `python-esileapclient`_ repository.

.. _Download Ubuntu 22.04: https://releases.ubuntu.com/22.04/ubuntu-22.04-live-server-amd64.iso
.. _DevStack documentation: https://docs.openstack.org/devstack/latest/
.. _Ironic DevStack Guide: https://docs.openstack.org/ironic/latest/contributor/devstack-guide.html
.. _ESI-Leap GitHub repository: https://github.com/CCI-MOC/esi-leap
.. _python-esileapclient: https://github.com/CCI-MOC/python-esileapclient