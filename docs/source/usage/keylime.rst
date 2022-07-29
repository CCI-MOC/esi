Installing Keylime on ESI
=========================

ESI provides a guide to use `Keylime`_ outside Ironic for run-time attestation with `IMA`_ and boot measurement with `Secure Boot_`.

Prerequisites
-------------
* A private attestation network.
* An optional public network to acquire Keylime.
* A node specified as Keylime server.
* The nodes-to-be-attested must have an active TPM 2.0 and keylime agent installed.
* For boot attestation, the nodes-to-be-attestated must have a BIOS with UEFI Secure Boot enabled and must boot a recent enough version of the Linux kernel (5.4 or later). 

Setup
-----

Build Keylime Server
~~~~~~~~~~~~~~~~~~~~

Provision the Node
^^^^^^^^^^^^^^^^^^
.. prompt:: bash $

  metalsmith deploy --image <image> --network <attestation_network> --resource-class baremetal --ssh-public-key <path_to_public_key>

Install Keylime Packages
^^^^^^^^^^^^^^^^^^^^^^^^

* Note: the server needs to be connected to the public internet in order to download Keylime packages. Attaching the node to the public network could be as simple as running the command ``openstack esi node network attach --network <public_network> <node>``.
* After the node is active, ssh into it. There are various ways to acquire Keylime. One possible way is listed below:

  .. prompt:: bash $

    git clone https://github.com/keylime/keylime.git
    cd keylime && ./installer.sh

Modify /etc/keylime.conf
^^^^^^^^^^^^^^^^^^^^^^^^

* Set ``require_ek_cert`` to false if the physical TPM does not have EK certificates.
* Set the binding address for verifier and registrar, for example:

  .. prompt::

    [cloud_verifier]
    cloudverifier_ip = 0.0.0.0

    [registrar]
    registrar_ip = 0.0.0.0

(Optional) Enable Boot Measurement Attestation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To work with boot measurement, a few extra steps are needed.

Boot measurement attestation is performed by a policy validator scipt run by the Keylime verifier.

A policy script must be placed on the machine running the Keylime verifier and registered. Policies can be registered by
calling keylime.elchecking.policies.register and passing in the name of the policy to be used by the Keylime config file, as well as the policy object from your policy file.

From here, the policy can be set in the Keylime config file:

  .. prompt::
    
    [measured_boot_policy_name] = policy_name

The policy file will generate a measured boot reference state from the UEFI Secure Boot eventlogs to compare with measured boot reference state the user will provide as a golden state.

Start Keylime Services
^^^^^^^^^^^^^^^^^^^^^^

* Note: if the node is not on the attestation network, it should now be put there using ``openstack esi node network attach --network <attestation_network> <node>``.

.. prompt:: bash $

  keylime_verifier
  keylime_registrar

Create Attestation Image
~~~~~~~~~~~~~~~~~~~~~~~~
`Diskimage-builder tool`_ could be used to build a provisioning image with keylime-agent installed.

* An example to use diskimage-builder tool to build a CentOS 8 image:

  .. prompt:: bash $

    export DIB_KEYLIME_AGENT_REGISTRAR_IP=<keylime_registrar_service_ip>
    export DIB_KEYLIME_AGENT_REGISTRAR_PORT=<keylime_registrar_service_port>
    export DIB_KEYLIME_AGENT_PORT=<keylime_agent_port> (default to 8890)
    disk-image-create centos baremetal dhcp-all-interfaces grub2 keylime-agent -o keylime-image

* TPM-emulator could be used instead of a real TPM hardware:

  .. prompt:: bash $

    disk-image-create centos baremetal dhcp-all-interfaces grub2 keylime-agent tpm-emulator -o keylime-image

  Note: Keylime does not recommend TPM emulators for production systems and TPM 1.2 is no longer supported by Keylime.

* Allowlist and its checksum could be extracted from the image initramfs or collected from the target node at boot time. Upload them to the machine that triggers attestation.

* Upload the image to Glance service:

  .. prompt:: bash $

    KERNEL_ID=$(openstack image create \
      --file keylime-image.vmlinuz --public \
      --container-format aki --disk-format aki \
      -f value -c id keylime-image.vmlinuz)
    RAMDISK_ID=$(openstack image create \
      --file keylime-image.initrd --public \
      --container-format ari --disk-format ari \
      -f value -c id keylime-image.initrd)
    openstack image create \
      --file keylime-image.qcow2 --public \
      --container-format bare \
      --disk-format qcow2 \
      --property kernel_id=$KERNEL_ID \
      --property ramdisk_id=$RAMDISK_ID \
      keylime-image

Alternatively, keylime agent and TPM utility prerequisites could be manually installed with this `instruction`_.

Usage
-----
Provision the Node-to-be-attested
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. prompt:: bash $

  metalsmith deploy --image keylime-image --network <attestation_network> --resource-class baremetal --ssh-public-key <path_to_public_key>

If using the keylime-image built with diskimage-builder, keylime-agent will start as a system service at boot time, generate its UUID, and register itself with the registrar service. Check the keylime-agent log to get agent UUID.

Trigger the Runtime Attestation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Runtime attestation can be triggered from the Keylime server machine or a third machine. If doing it from a third machine, make sure:

* this machine is in the same private attestation network.
* client certificates in /var/lib/keylime/cv_ca/ are copied from Keylime server.
* keylime-tenant is installed on this machine.
* allowlist of the target node is present on the machine.

Exclude list is a text file of directories or files which will be ignored when checking the gathered IMA measurements of a node. For example, the tmp directory can be ignored by adding ``/tmp/.*`` into exclude list.

Call keylime-tenant to start runtime attestation:

.. prompt:: bash $

  keylime_tenant -v <keylime_verifier_ip> -vp <keylime_verifier_port> -r <keylime_registrar_ip> -rp <keylime_registrar_port> -t <keylime_agent_ip> -tp <keylime_agent_port> -f <excludelist_path> --uuid <agent_uuid> --allowlist <allowlist_path> --exclude <excludelist_path> -c add

Stop Keylime from requesting attestation:

.. prompt:: bash $

  keylime_tenant -c delete -u <agent_uuid>

Trigger Boot Measurement Attestation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Boot Measurement Attestation should be triggered with the same tenant call used to provision the Keylime agent and trigger runtime attestation.

Use the flag as follows when calling the tenant

  .. prompt:: bash $
  
    --mb-refstate <path/measured_boot_reference_state.txt>

So in all a call to trigger runtime and boot measurement attestation would be constructed as follows:

.. prompt:: bash $

  keylime_tenant -v <keylime_verifier_ip> -vp <keylime_verifier_port> -r <keylime_registrar_ip> -rp <keylime_registrar_port> -t <keylime_agent_ip> -tp <keylime_agent_port> -f <excludelist_path> --uuid <agent_uuid> --allowlist <allowlist_path> --exclude <excludelist_path> --mb-refstate <path/measured_boot_reference_state.txt> -c add

.. _keylime: https://github.com/keylime/keylime
.. _IMA: https://keylime-docs.readthedocs.io/en/latest/user_guide/runtime_ima.html
.. _Diskimage-builder tool: https://docs.openstack.org/diskimage-builder/latest/
.. _instruction: https://github.com/keylime/keylime#manual
.. _Secure Boot: https://keylime-docs.readthedocs.io/en/latest/user_guide/use_measured_boot.html
