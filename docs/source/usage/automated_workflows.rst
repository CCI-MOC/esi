Automated Workflows
===================

ESI Leap is configured to emit notifications over a message bus to signal lease events within esi-leap services. These notifications can be consumed and processed by any external service. In our use case, we integrate the `esi-event-actions`_  script that listens to the message queue and executes scripts when lease events are caught.

Operator Workflow
-----------------
When a lease is fulfilled, expired or deleted, esi-leap emits the notification on the 'esi_leap_versioned_notifications' topic in the RabbitMQ message bus. ESI operator can utilize the esi-event-actions to listen for notification messages from esi-leap services. The notification payload includes lease and node attributes structured as JSON object, enabling operators to execute any script to handle the notification.

Configuration
-------------
esi-leap
~~~~~~~~
Ensure that the `driver` and `transport_url` are correctly configured under the **[oslo_messaging_notifications]** section in the ``esi-leap.conf`` file.
An example configuration:

.. prompt::

    [oslo_messaging_notifications]
    driver=messagingv2
    transport_url=rabbit://<user>:<password>@<host>:<port>/?ssl=0

esi-event-actions
~~~~~~~~~~~~~~~~~
Follow the instructions in the README.rst to install `esi-event-actions`_. After installation, edit ``esi-event-action-listener.conf``. Update the values in the **[DEFAULT]** section, setting the 'queues' to `esi_leap_versioned_notifications.info,esi_leap_versioned_notifications.error`.
The notification system supports the following list of events for a lease:

* esi_leap.lease.fulfill.start
* esi_leap.lease.fulfill.end
* esi_leap.lease.fulfill.error
* esi_leap.lease.delete.start
* esi_leap.lease.delete.end
* esi_leap.lease.delete.error

In each action section, operators can select any of the notification events and run a script of their choice to handle the events.
Here is an example configuration, operator listens for lease `fulfill` and `delete` messages. Upon detection of these messages, the listener triggers the execution of ``fulfill.sh`` and ``delete.sh`` scripts, respectively. Note that `script_params` and `filter_params` values must be attributes on the event data payload. Dot notation is valid to specify a value in a subdictionary:

.. prompt::

    [DEFAULT]
    user = <user in transport_url>
    password = <password in transport_url>
    host = <host in transport_url>
    port = <port in transport_url>
    queues = esi_leap_versioned_notifications.info,esi_leap_versioned_notifications.error

    [fulfill]
    events = esi_leap.lease.fulfill.end
    script = fulfill.sh
    script_params = node_name,fulfill_time
    filter_params = {"purpose": "test", "properties.vendor": "dell"}

    [delete]
    events = esi_leap.lease.delete.end
    script = delete.sh
    script_params = node_name,expire_time
    filter_params = {"purpose": "test", "properties.vendor": "dell"}}


.. _esi-event-actions: https://github.com/CCI-MOC/esi-event-actions