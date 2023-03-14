ESI Documentation
=================

Welcome to the documentation for Elastic Secure Infrastructure (ESI)!

ESI is a hardware isolation project built on top of OpenStack that allows multiple bare metal node owners to collaborate to form a single bare metal cloud. Owners have exclusive use of their nodes, and can also lease their nodes out to lessees. Take a look at our presentation for a good high-level overview:

* ESI: How I Learned to Share My Hardware! [ `video`_ | `PDF`_ ]

If you are using ESI for the first time, you may want to jump straight to the `New User Guide`_.

Installing and using ESI is easy: it's just `OpenStack with a specific configuration`_. A few `optional ESI components`_ can be installed for ease of use.

.. toctree::
   :maxdepth: 2

   usage/index
   install/index
   developer/index
   contact-us

.. _video: https://www.youtube.com/watch?v=o5g85SrPEWI
.. _PDF: https://research.redhat.com/esi_ironic-presentation/
.. _New User Guide: usage/new_user_guide.html
.. _OpenStack with a specific configuration: install/index.html
.. _optional ESI components: install/esi_add_ons.html
