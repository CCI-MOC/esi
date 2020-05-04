# ESI Deployment

ESI is composed of multiple OpenStack services. As a result, any OpenStack deployment tool that can deploy and configure the required services can create an ESI deployment. Our recommended deployment tool is [Standalone TripleO](https://docs.openstack.org/project-deploy-guide/tripleo-docs/latest/deployment/standalone.html). Standalone TripleO is part of the active upstream [TripleO project](https://docs.openstack.org/tripleo-docs/latest/), and is highly configurable.

If you decide to use Standalone TripleO, you will need the following additional configurations before deployment.

## Required Version

ESI requires Ironic code that is currently only present in the master branch. For that reason, when running the Standalone TripleO installation steps, make sure you run the `tripleo-repos` command as follows:

```
sudo -E tripleo-repos current-tripleo-dev
```

## Ironic Configuration

Standalone TripleO requires the following configuration changes in order to deploy Ironic.

In `standalone_parameters.yaml`, add the following:

```
resource_registry:
  OS::TripleO::Services::NovaCompute: OS::Heat::None

parameter_defaults:
  NeutronMechanismDrivers: [openvswitch, baremetal]
  IronicEnabledHardwareTypes:
  - ipmi
  IronicEnabledPowerInterfaces:
  - ipmitool
  IronicEnabledManagementInterfaces:
  - ipmitool
  IronicCleaningDiskErase: 'metadata'
  IronicInspectorSubnets:
  - ip_range: 192.168.1.200,192.168.1.250
  IronicInspectorInterface: 'br-ctlplane'
```

## Ansible Networking Configuration

If your deployment requires switch management, add/update these parameters in `standalone_parameters.yaml`:

```
parameter_defaults:
  NeutronMechanismDrivers: [ansible, openvswitch, baremetal]             # order matters; ansible must be first
  NeutronNetworkVLANRanges: datacentre:<vlan start>:<vlan end>           # ex: datacenter:100:150
  ML2HostConfigs:
    switch1:
      ansible_network_os: <switch os>
      ansible_host: <switch host>
      ansible_user: <switch user>
      ansible_ssh_pass: <switch password>
      manage_vlans: true
      mac: <switch mac>
```

## Deployment

When running `openstack tripleo deploy`, add a reference to the following environment files:

```
  -e /usr/share/openstack-tripleo-heat-templates/environments/services/ironic.yaml
  -e /usr/share/openstack-tripleo-heat-templates/environments/services/ironic-inspector.yaml
  -e /usr/share/openstack-tripleo-heat-templates/environments/services/neutron-ovs.yaml
```

If you are using ansible networking, add the following:

```
  -e /usr/share/openstack-tripleo-heat-templates/environments/services/neutron-ml2-ansible.yaml
```

A full deploy command might look like the following:

```
sudo openstack tripleo deploy \
  --templates \
  --local-ip=$IP/$NETMASK \
  -e /usr/share/openstack-tripleo-heat-templates/environments/standalone/standalone-tripleo.yaml \
  -e /usr/share/openstack-tripleo-heat-templates/environments/services/ironic.yaml \
  -e /usr/share/openstack-tripleo-heat-templates/environments/services/ironic-inspector.yaml \
  -e /usr/share/openstack-tripleo-heat-templates/environments/services/neutron-ovs.yaml \
  -e /usr/share/openstack-tripleo-heat-templates/environments/services/neutron-ml2-ansible.yaml \
  -r /usr/share/openstack-tripleo-heat-templates/roles/Standalone.yaml \
  -e $HOME/containers-prepare-parameters.yaml \
  -e $HOME/standalone_parameters.yaml \
  --output-dir $HOME \
  --standalone
```

## Post-Deployment Configuration

After deploying Standalone TripleO, there are a few post-deployment configuration steps to consider.

### Ironic Policy

The Ironic policy file must be updated if you intend for non-admins to use the Ironic API. Access for single-node API functions is granted through the use of the ``is_node_owner`` and ``is_node_lessee` roles, which apply to a project specified by a node's ``owner`` and ``lessee`` field respectively. Further detail can be found in the upstream [node multi-tenancy documentation](https://docs.openstack.org/ironic/latest/admin/node-multitenancy.html)

This repository includes a sample Ironic policy file that enables node owners to manage their nodes and node lessees to provision their leased nodes. It can be found at [/etc/ironic/policy.json.sample](/etc/ironic/policy.json.sample).

### Neutron Policy

If you are using ansible networking to configure the switch, the following Neutron policy rule must be updated to allow non-admins to attach VLAN networks to their nodes:

```
# Get ``provider:physical_network`` attribute of a network
# GET  /networks
# GET  /networks/{id}
#"get_network:provider:physical_network": "rule:admin_only"
"get_network:provider:physical_network": "rule:admin_or_owner or rule:shared"
```

### Ansible Networking and Cisco Nexus Switches

If you are using a Cisco Nexus switch, then you'll need an updated Ansible playbook for configuring trunk ports. It can be found at https://github.com/ansible-network/network-runner/blob/devel/etc/ansible/roles/network-runner/providers/nxos/conf_trunk_port.yaml.

In addition, if you require PortFast mode, then you'll need to update the access port and trunk port Ansible playbooks to add a PortFast configuration commands whenever VLANs are added to a port: ``spanning-tree port type edge trunk``.
