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

## Post-Deployment Configuration

After deploying Standalone TripleO, there are a few post-deployment configuration steps to consider.

### Ironic Policy

The Ironic policy file must be updated if you intend for non-admins to use the Ironic API. Access
for single-node API fuctions is granted through the use of the ``is_node_owner`` role, which applies
to a project specified by a node's ``owner`` field. Access to ``baremetal:node:list`` can safely be
opened to all, as that API call will filter results for non-admins by owner. Access to
``baremetal:node:create`` should not be exposed to non-admins.

For example, if you would like to update the default Ironic policy settings to allow non-admins to be
able to list/get/set the power state of nodes that they own, update the Ironic policy file as follows:

```
# Retrieve a single Node record
# GET  /nodes/{node_ident}
#"baremetal:node:get": "rule:is_admin or rule:is_observer"
"baremetal:node:get": "rule:is_admin or rule:is_observer or role:is_node_owner"

# Retrieve multiple Node records, filtered by owner
# GET  /nodes
# GET  /nodes/detail
#"baremetal:node:list": "rule:baremetal:node:get"
"baremetal:node:list": ""

# Change Node power status
# PUT  /nodes/{node_ident}/states/power
#"baremetal:node:set_power_state": "rule:is_admin"
"baremetal:node:set_power_state": "rule:is_admin or rule:is_node_owner"
```