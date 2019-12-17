# MOC HIL/BMI Requirements

## Overview

We want to create a set of services/systems to permit multiple tenants to securely and flexibly allocate baremetal machines from a pool of available hardware, create networks, attach baremetal nodes to networks, and to optionally provision an operating system on those systems through the use of an associated provisioning service.

## Definitions

### Isolation service

The isolation service provides a mechanism for reserving baremetal nodes, creating isolated tenant-private networks, and connecting nodes to these networks and to other networks available in the environment.

The service keeps track of which machines are available, what network interfaces they have, and to which switch ports those machines are connected. It allows the tenant to create networks (e.g. from an admin-defined pool of vlans) and attach those networks to network interfaces. An administrator may also expose existing infrastructure networks into the baremetal environment.

The service must provide an API that interfaces with the baseboard management controller of the baremetal nodes to control power, set boot devices, and access a serial console.

In order to provide a secure environment, the service should reset the BMC to a known state and sanitize locally attached storage when a baremetal node is returned to the pool of available hardware.

Ultimately, the isolation service should provide the ability to create virtual networks such that nodes that do not share a common network infrastructure appear to be on the same layer 2 network.

### Provisioning service

A provisioning service allows a user to deploy an operating system onto baremetal hardware. The provisioning service provided by ESI must support the following features

* Provisioning an operating system image to local disk (boot-from-disk)

* Provisioning an operating system to a network-attached volume, attaching that volume to a baremetal node, and booting from that volume (boot-from-volume)

* Network-attached volumes must be robust in the event of storage server failures

* Network-attached volumes must provide snapshotting capabilities to allow for quick recovery of initial state or rapid provisioning of multiple baremetal nodes from the same base volume.

An ESI operator may elect to use their own provisioning system.

## Existing HIL/BMI Features

[HIL][] ("Hardware Isolation Layer") and BMI ("Bare-Metal Imaging") are the names for the initial implementation of ESI-style services currently in use at the MOC.  This section describes the features and functions of HIL and BMI, which are the minimal set of features we must implement in ESI in order to meet our goals.  HIL serves as the isolation service at MOC, while BMI is the provisioning service.

[hil]: https://open.bu.edu/handle/2144/19198

* HIL: node access and configuration (including network)

    * Admins

        * Add a pool of networks to HIL

        * Create public networks (from the pool)

        * Import networks outside of the standard allocation pool.

        * Assign nodes to a project

        * Add/Remove nodes from HIL (i.e. make nodes available to be leased)

    * Users

        * View available nodes

        * Lease a node for their project

        * Create a project network

        * View all networks accessible by their project automatically (private and public).

        * Grant access to a project network to other projects

        * Connect a network to a leased node’s NIC

        * Control power state of a leased node (status/power cycle/off/on)

        * Set boot device of a leased node (PXE or disk)

        * View serial console of a leased node (read only)

* BMI: provisioning of nodes

    * BMI Service

        * Sets up iSCSI targets (backed by Ceph RBD) for nodes to boot from; this is automatically done when a user issues a command to provision their leased nodes

        * Note: The BMI codebase/documentation refers to rbd volumes as images. Those are not the same as openstack images.

    * Admins

        * Import bootable volumes from storage (ceph) into user's projects. This creates a deep copy of the volumes for the project and are immutable.

    * Users

        * Boot a leased node from a shallow clone of a volume in their project. The original volume in their project is never attached to a node.

        * Snapshot the shallow clones of the volumes from which a node is booted from. These snapshots are flattened and immutable.

        * Boot other leased nodes from shallow clones of the snapshots.

Both BMI and HIL use custom databases to keep track of ownership of images, networks, nodes, etc.

Here’s a typical MOC workflow:

1. Users lease a node through HIL

2. They connect their leased node to a public network (something that gives internet access)

3. They connect their leased node’s provisioning NIC to the BMI provisioning network

4. They use the BMI CLI to specify how they would like their leased node to boot. They do so by specifying the node, an image, and the provisioning NIC

5. Finally, they power cycle their leased node so that it boots using those specifications 

