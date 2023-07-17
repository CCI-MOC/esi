Automated Workflows
===================

Users may wish to set up automatic processes that trigger when nodes are leased or returned. There are two high-level ways of setting up such automated workflows, with each being suitable for a different class of user. Both require the use of `ESI Leap`_, and the configuration of ESI Leap notifications.

Event Configuration
-------------------

In order for ESI Leap to emit notifications, ensure that the `driver` and `transport_url` are correctly configured under the **[oslo_messaging_notifications]** section in the ``esi-leap.conf`` file. For example:

.. prompt::

    [oslo_messaging_notifications]
    driver=messagingv2
    transport_url=rabbit://<user>:<password>@<host>:<port>/?ssl=0

Once done, ESI Leap will emit a notification on the `esi_leap_version_notifications` topic in the RabbitMQ message bus whenever a lease is fulfilled, expired, or deleted. The list of notification types is as follows:

* esi_leap.lease.fulfill.start
* esi_leap.lease.fulfill.end
* esi_leap.lease.fulfill.error
* esi_leap.lease.delete.start
* esi_leap.lease.delete.end
* esi_leap.lease.delete.error

ESI Leap will now also store a truncated record of the event in the database. This event history is accessible by running `openstack esi event list`. Results are scoped to the user.

Monitoring Events for Automated Workflows
-----------------------------------------

Monitoring RabbitMQ
~~~~~~~~~~~~~~~~~~~

The first option for automated workflows is to use the scripts provided in `esi-event-actions`_ to monitor the message bus. This method is only suitable for ESI operators.

Start by following the instructions in the README to install `esi-event-actions`_. After installation, edit ``esi-event-action-listener.conf`` and then run `esi-event-action-listener.py`. An example configuration file might be as follows:

.. prompt::

    # used to connect to RabbitMQ and monitor specific queues
    [DEFAULT]
    user = <user in transport_url>
    password = <password in transport_url>
    host = <host in transport_url>
    port = <port in transport_url>
    queues = esi_leap_versioned_notifications.info,esi_leap_versioned_notifications.error

    # a section that specifies a script to run whenever the specified event is caught
    [fulfill]
    events = esi_leap.lease.fulfill.end
    script = fulfill.sh
    script_params = node_name,fulfill_time                           # values from the event payload to be passed into the script
    filter_params = {"purpose": "test", "properties.vendor": "foo"}  # filters on the event payload that must be fulfilled for the script to run

    # a section that specifies a script to run whenever the specified event is caught
    [delete]
    events = esi_leap.lease.delete.end
    script = delete.sh
    script_params = node_name,expire_time                             # values from the event payload to be passed into the script
    filter_params = {"purpose": "test", "properties.vendor": "foo"}}  # filters on the event payload that must be fulfilled for the script to run

In this example, the `[fulfill]` and `[delete]` sections detail scripts that will be run when the specified events are caught, with `filter_params` providing additional filters based on the event payload. Upon detection of these events, the listener triggers the execution of ``fulfill.sh`` and ``delete.sh`` respectively, passing in values from the event payload specified by `script_params`. Note that dot notation may be used to access subdictionary values of the event payload.

Monitoring Event History
~~~~~~~~~~~~~~~~~~~~~~~~

Tenant users are unlikely to have access to the message bus. An alternative is to monitor ESI Leap's event history. This can be done through a simple python script that calls `openstack esi event list` with the `--last-event-id` parameter to ensure that events are not returned multiple times. For example:

::

   import json
   import subprocess

   def run_openstack_command(cmd):
       output_json = subprocess.check_output('%s --format json' % cmd, shell=True)
       return json.loads(output_json)

   def get_last_event_id(default_last_event_id=0, file_name='.esi-last-event-id'):
       try:
           with open(file_name, "r") as f:
               last_event_id = int(f.read())
       except FileNotFoundError:
           last_event_id = default_last_event_id
       except ValueError:
           last_event_id = default_last_event_id
       return last_event_id

   def write_last_event_id(last_event_id, file_name='.esi-last-event-id'):
       with open(file_name, "w") as f:
           f.write(str(last_event_id))

   def main():
       last_event_id = get_last_event_id()
       events = run_openstack_command('openstack esi event list --last-event-id %s' % last_event_id)
       new_last_event_id = last_event_id
       for event in events:
           new_last_event_id = event['ID']
           if event['Event Type'] == 'esi_leap.lease.fulfill.end':
               node_uuid = event['Resource UUID']
               lease_uuid = event['Object UUID']
               lease = run_openstack_command('openstack esi lease show %s' % lease_uuid)
               print("Lease %s with purpose %s on node %s started" % (lease_uuid, lease['purpose'], node_uuid))
           elif event['Event Type'] == 'esi_leap.lease.delete.end':
               node_uuid = event['Resource UUID']
               lease_uuid = event['Object UUID']
               print("Lease %s on node %s ended" % (lease_uuid, node_uuid))
       write_last_event_id(new_last_event_id)

   if __name__ == "__main__":
       main()


.. _ESI Leap: https://github.com/CCI-MOC/esi-leap
.. _esi-event-actions: https://github.com/CCI-MOC/esi-event-actions
