# ESI Deployment

ESI is composed of multiple OpenStack services. As a result, any OpenStack deployment tool that can deploy and configure the required services can create an ESI deployment. We currently recommend using the OpenStack **Ussuri** release, in conjunction with the following patches:

- ironic
    - [Allow node lessee to see node's ports](https://review.opendev.org/#/c/730366/)
    - [Allow node vif attach to specify port_uuid or portgroup_uuid](https://review.opendev.org/#/c/731780/)
- python-ironicclient
    - [Add port-uuid parameter to node vif attach](https://review.opendev.org/#/c/737585/)

In addition, the following may be needed depending on your networking requirements:

- network-runner
    - [adding kwargs to trunk ports](https://github.com/ansible-network/network-runner/pull/48)
- networking-ansible
    - [Correct port detachment](https://review.opendev.org/#/c/745318/)

Many of these changes are present in the OpenStack **Victoria** release; however, we have not yet tested such a deployment.

You may also find the following ESI-developed services and tools useful:

- [ESI Leap](https://github.com/cci-moc/esi-leap): a simple leasing service
    - [python-esileapclient](https://github.com/cci-moc/python-esileapclient)
- [python-esiclient](https://github.com/CCI-MOC/python-esiclient): CLI commands to simplify OpenStack workflows

## Deploying with Standalone TripleO

We use [Standalone TripleO](https://docs.openstack.org/project-deploy-guide/tripleo-docs/latest/deployment/standalone.html) as our deployment tool. Standalone TripleO is part of the active upstream [TripleO project](https://docs.openstack.org/tripleo-docs/latest/), and is highly configurable.

If you decide to use Standalone TripleO, you will need the following additional configurations before deployment.

### Ironic Configuration

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

### Ansible Networking Configuration

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
      stp_edge: True                                                     # only needed if PortFast mode is required
```

### Deployment

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

### Post-Deployment Configuration

After deploying Standalone TripleO, there are a few post-deployment configuration steps to consider.

#### Ironic Policy

The Ironic policy file must be updated if you intend for non-admins to use the Ironic API. Access for single-node API functions is granted through the use of the ``is_node_owner`` and ``is_node_lessee` roles, which apply to a project specified by a node's ``owner`` and ``lessee`` field respectively. Further detail can be found in the upstream [node multi-tenancy documentation](https://docs.openstack.org/ironic/latest/admin/node-multitenancy.html)

This repository includes a sample Ironic policy file that enables node owners to manage their nodes and node lessees to provision their leased nodes. It can be found at [/etc/ironic/policy.json.sample](/etc/ironic/policy.json.sample).

#### Neutron Policy

If you are using ansible networking to configure the switch, the following Neutron policy rule must be updated to allow non-admins to attach VLAN networks to their nodes:

```
# Get ``provider:physical_network`` attribute of a network
# GET  /networks
# GET  /networks/{id}
#"get_network:provider:physical_network": "rule:admin_only"
"get_network:provider:physical_network": "rule:admin_or_owner or rule:shared"
```
