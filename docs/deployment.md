# ESI Deployment

ESI is composed of multiple OpenStack services. As a result, any OpenStack deployment tool that can deploy and configure the required services can create an ESI deployment. Our recommended deployment tool is [Standalone TripleO](https://docs.openstack.org/project-deploy-guide/tripleo-docs/latest/deployment/standalone.html). Standalone TripleO is part of the active upstream [TripleO project](https://docs.openstack.org/tripleo-docs/latest/), and is highly configurable.

If you decide to use Standalone TripleO, you will need the following additional configurations before deployment.

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

## Deployment

When running `openstack tripleo deploy`, add a reference to the following environment files:

```
  -e /usr/share/openstack-tripleo-heat-templates/environments/services/ironic.yaml
  -e /usr/share/openstack-tripleo-heat-templates/environments/services/ironic-inspector.yaml
  -e /usr/share/openstack-tripleo-heat-templates/environments/services/neutron-ovs.yaml
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
  -r /usr/share/openstack-tripleo-heat-templates/roles/Standalone.yaml \
  -e $HOME/containers-prepare-parameters.yaml \
  -e $HOME/standalone_parameters.yaml \
  --output-dir $HOME \
  --standalone
```