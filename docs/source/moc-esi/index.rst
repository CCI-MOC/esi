MOC-ESI
=======

New User Sign-up
----------------
New users must first `register for an MGHPCC Account`_.

Next, they can access the ESI OpenStack `dashboard`_ login page and choose the **OpenID Connect** authentication method. Then you will be redirected to a page to select a login provider. After choosing a login method, follow the steps provided.

Note that during the first login, you will receive an error message like this: ``Login failed: You are not authorized for any projects or domains``. If this occurs, please contact ESI admin to add your user account to a proper project and assign roles to your account.

After your account has been properly configured, you can follow the same steps to log in and successfully authenticate, getting access to the ESI Horizon dashboard.

Accessing the CLI
-----------------
Once new users have signed up using Horizon WebSSO, they can use the CLI tool to access the ESI OpenStack APIs.

Creating an Application Credential
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Log in to ESI `dashboard`_ using your account credentials.
2. Select the project for which you want to create an application credential from the dropdown menu.
3. In the sidebar, navigate to **Identity > Application Credentials**.
4. Click the **Create Application Credential** button.
5. Provide a name for your credential and select all available roles. All other fields are optional.
6. After creation, you will be prompted to download an RC file or a clouds.yaml file. Download the file and use it to run OpenStack command-line clients. You can find more information about OpenStack Client usage `here`_.

Installing the CLI Clients
~~~~~~~~~~~~~~~~~~~~~~~~~~
It is recommended that you install the CLI clients within a Python virtual environment:

  .. prompt:: bash $

    python3 -mvenv .venv
    source .venv/bin/activate

Run the following to install the needed clients:

  .. prompt:: bash (.venv)$

    pip install python-esiclient
    pip install python-esileapclient


Leasing Nodes
-------------
The MOC admins may have already granted you long-term leases on nodes. You can also obtain short-term one day leases on available nodes. To see the list, run:

  .. prompt:: bash (.venv)$

    openstack esi offer list

To claim an offer, run:

  .. prompt:: bash (.venv)$

    openstack esi offer claim <offer uuid>


Using Nodes
-----------
Please consult the `New User Guide`_ section for more information on how to configure, provision and access your leased nodes.

Contact
-------
If you have any questions about ESI functionality, the specifications of the nodes, or anything else, please contact us in the ``#esi`` channel within the MOC Alliance Slack.

.. _register for an MGHPCC Account: https://regapp.mss.mghpcc.org/
.. _here: https://docs.openstack.org/python-openstackclient/latest/configuration/index.html
.. _dashboard: https://esi.massopen.cloud/
.. _New User Guide: ../usage/new_user_guide.html
