# ESI Usage

This document highlights OpenStack CLI commands used to perform common ESI functions. A complete listing of commands can be found by reading the [complete OpenStack CLI documentation](https://docs.openstack.org/python-openstackclient/latest/cli/command-list.html). Each entry here also links to the appropriate entry in the OpenStack CLI documentation.

* [Identity](#identity)
* [Isolation](#isolation)
* [Maintenance](#maintenance)

## <a name="identity"></a>Identity

### Administrator

* **Create project:** `openstack project create <project-name>` [[full reference](https://docs.openstack.org/python-openstackclient/latest/cli/command-objects/project.html#project-create)]
* **Create user:** `openstack user create --project <project-name> --password <password> <user-name>` [[full reference](https://docs.openstack.org/python-openstackclient/latest/cli/command-objects/user.html#user-create)]
* **Give user role in project:** `openstack role add --project <project-name> --user <user-name> <role>` [[full reference](https://docs.openstack.org/python-openstackclient/latest/cli/command-objects/role.html#role-add)]
  * By default, admins should give users the ``member`` role in a project.

A typical series of commands to create a project and a user for that project might be:


```
    $ openstack project create test-project
    $ openstack user create --project test-project --password temporary test-user
    $ openstack role add --project test-project --user test-user member
```

### User

* **Set your password:** `openstack user password set`

## <a name="isolation"></a>Isolation

### Administrator

* **Add node to inventory:** `openstack baremetal node create <options>` [[full reference](https://docs.openstack.org/python-ironicclient/latest/cli/osc/v1/index.html#baremetal-node-create)]
  * Please refer to the linked CLI reference for the full list of options.
* **Add node to inventory: (bulk)** `openstack overcloud node import <node_file>` [[full reference](https://docs.openstack.org/python-tripleoclient/latest/commands.html#overcloud-node-import)]
  * Please refer to the linked CLI reference for the full list of options.
* **Remove node from inventory:** `openstack baremetal node delete <node-id-or-name>` [[full reference](https://docs.openstack.org/python-ironicclient/latest/cli/osc/v1/index.html#baremetal-node-delete)]
* **Assign node to project:** `openstack baremetal node set --owner <project-id> <node-id-or-name>` [[full reference](https://docs.openstack.org/python-ironicclient/latest/cli/osc/v1/index.html#baremetal-node-set)]
* **Unassign node from project:** `openstack baremetal node unset --owner <node-id-or-name>` [[full reference](https://docs.openstack.org/python-ironicclient/latest/cli/osc/v1/index.html#baremetal-node-unset)]

### User

None

## <a name="maintenance"></a>Maintenance

### Administrator

None

### User

The baremetal operations listed here are not available to non-administrators by default. Administrators must enable them by modifying Ironic's policy file.

* **Power on assigned node:** `openstack baremetal node power on <node-id-or-name>` [[full reference](https://docs.openstack.org/python-ironicclient/latest/cli/osc/v1/index.html#baremetal-node-power-on)]
* **Power off assigned node:** `openstack baremetal node power off <node-id-or-name>` [[full reference](https://docs.openstack.org/python-ironicclient/latest/cli/osc/v1/index.html#baremetal-node-power-off)]
* **Reboot assigned node:** `openstack baremetal node reboot <node-id-or-name>` [[full reference](https://docs.openstack.org/python-ironicclient/latest/cli/osc/v1/index.html#baremetal-node-reboot)]
