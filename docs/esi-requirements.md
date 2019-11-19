# MOC HIL/BMI Requirements

## Overview

We want to create a set of services/systems to permit multiple tenants to flexibly allocate baremetal machines from a pool of available hardware, attach those systems to tenant-private networks, and to optionally provision an operating system on those systems through the use of an associated provisioning service.

## Definitions

### Isolation service

The isolation service provides a mechanism for reserving baremetal nodes, creating isolated tenant-private networks, and connecting nodes to these networks.

The service keeps track of which machines are available, what network interfaces they have, and to which switch ports those machines are connected. It allows the tenant to create networks (e.g. from an admin-defined pool of vlans) and attach those networks to network interfaces. An administrator may also expose public networks or existing VLANs into the baremetal environment.

The service interacts with the baseboard management controller of the baremetal nodes to control power, set boot devices, and access a serial console. 

Ultimately, the isolation service should provide the ability to create virtual networks such that nodes that do not share a common network infrastructure appear to be on the same layer 2 network.

### Provisioning service

A provisioning service allows a user to deploy an operating system onto baremetal hardware. The provisioning service must support the following features

* Provisioning an operating system image to local disk (boot-from-disk)

* Provisioning an operating system to a SAN volume, attaching that volume to a baremetal node, and booting from that volume (boot-from-volume)

* SAN storage must be robust in the event of storage server failures

* SAN storage must provide snapshotting capabilities to allow for quick recovery of initial state or rapid provisioning of multiple baremetal nodes from the same base volume.

## Existing HIL/BMI Features

This section describes the features and functions of HIL and BMI services. HIL serves as the isolation service at MOC, while BMI is the provisioning service.

* HIL: node access and configuration (including network)

    * Admins

        * Create public networks

        * Assign nodes to a project

        * Add/Remove nodes from HIL (i.e. make nodes available to be leased)

    * Users

        * View available nodes

        * Lease a node for their project

        * Create a project network

        * Grant access to a project network to other projects

        * Connect a network to a leased node’s NIC

        * Control power state of a leased node (status/power cycle/off/on)

        * Set boot device of a leased node (PXE or disk)

        * View serial console of a leased node (read only)

* BMI: provisioning of nodes

    * BMI Service

        * Sets up iSCSI targets (backed by Ceph RBD) for nodes to boot from; this is automatically done when a user issues a command to provision their leased nodes

    * Admins

        * Create images (public and non-public)

        * Add images to a user’s project

    * Users

        * Create a snapshot of a leased node

        * Boot a leased node from an image or a snapshot

Both BMI and HIL use custom databases to keep track of ownership of images, networks, nodes, etc.

Here’s a typical MOC workflow:

1. Users lease a node through HIL

2. They connect their leased node to a public network (something that gives internet access)

3. They connect their leased node’s provisioning NIC to the BMI provisioning network

4. They use the BMI CLI to specify how they would like their leased node to boot. They do so by specifying the node, an image, and the provisioning NIC

5. Finally, they power cycle their leased node so that it boots using those specifications 

