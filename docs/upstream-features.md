# ESI Upstream New Features

Some ESI features will require enhancement to upstream OpenStack projects.

## Ironic: Multi-tenant support

ESI requires multi-tenant support in Ironic to meet our basic functionality. This enables a tenant to “own” a baremetal node — that is, to have exclusive access to it — without requiring administrative privileges.

An initial implementation of this feature has merged as [If08586f3e9705dd38ff83e4b500d9ee3cd45bce3][]. There is a detailed description of the change available in the [associated blueprint][I1e898f7b9791aa579a733996711945e273ef6a4a].

[If08586f3e9705dd38ff83e4b500d9ee3cd45bce3]: https://review.opendev.org/#/q/If08586f3e9705dd38ff83e4b500d9ee3cd45bce3
[I1e898f7b9791aa579a733996711945e273ef6a4a]: https://review.opendev.org/#/q/I1e898f7b9791aa579a733996711945e273ef6a4a

## Ironic: Improved serial console support

In an ESI-managed environment, out-of-band management will happen primarily via a serial console. The existing serial console support in Ironic is brittle and would benefit from more robust process management.

## Ironic: Access hardware via another Ironic instance

In the future, we would like an OpenStack operator to be able to lease nodes from an ESI instance and then add these to a local Ironic as baremetal nodes. This will require Ironic to be able to interact with baremetal nodes via the Ironic API, rather than using IPMI.

## Ironic: Keylime support

Keylime provides attestation — that is, assurance that a given baremetal node has not been tampered with. We would like to integrate this into the Ironic provisioning workflow such that prior to provisioning a node Ironic will run it through an attestation step, and will fail the node if the attestation fails.

## Nova: Baremetal filters that are aware of Ironic multi-tenancy

Nova interacts with Ironic as a user with administrative privileges, which means it is able to provision any available baremetal node. Nova needs to be aware of Ironic's multi-tenant features so that it only attempt to use baremetal nodes that belong to the tenant initiating the provisioning request with Nova.

## Ansible network: Additional switch drivers

We will need additional switch drivers to support our ESI test environment. A driver for our Nexus switches has been submitted as [PR #37][] against the [Network-Runner][] project.

[pr #37]: https://github.com/ansible-network/network-runner/pull/37
[network-runner]: https://github.com/ansible-network/network-runner
