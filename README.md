# Elastic Secure Infrastructure (ESI)

The most current documentation, including information about installation and usage, can be found at the [ESI Read the Docs site](https://esi.readthedocs.io/en/latest/index.html).

## Activities and Planning

Our work is tracked on the [ESI Taskboard](https://github.com/CCI-MOC/esi/projects/1).

## Code Repositories

Our code development features a mix of upstream OpenStack work and custom ESI code.

- OpenStack
    - [ironic](https://github.com/openstack/ironic)
    - [networking-ansible](https://opendev.org/x/networking-ansible)
- ESI
    - [esi-leap](https://github.com/cci-moc/esi-leap): a simple leasing service
        - [python-esileapclient](https://github.com/cci-moc/python-esileapclient)
    - [python-esiclient](https://github.com/CCI-MOC/python-esiclient): CLI commands to simplify OpenStack workflows

## References

### Presentations

- ESI: How I Learned to Share My Hardware! [ [video](https://www.youtube.com/watch?v=o5g85SrPEWI) | [PDF](https://research.redhat.com/esi_ironic-presentation/) ]

### Academic papers [ [complete references](references.bib) ]

- "[A secure cloud with minimal provider trust][0]"
- "[HIL: designing an exokernel for the data center][1]"
- "[Supporting Security Sensitive Tenants in a Bare-Metal Cloud][2]"
    - Describes an initial implementation of an isolation service
    - Code for this implementation can be found at <https://github.com/cci-moc/hil>.
- "[M2: Malleable Metal as a Service][3]"
    - Describes an initial implementation of a provisioning service
    - Code for this implementation can be found at <https://github.com/cci-moc/m2>.

[0]: https://www.usenix.org/conference/hotcloud18/presentation/mosayyebzadeh
[1]: https://open.bu.edu/handle/2144/19198
[2]: https://www.usenix.org/conference/atc19/presentation/mosayyebzadeh
[3]: https://ieeexplore.ieee.org/abstract/document/8360313

## Contact and Contribution

You can contact the ESI development team on the [OFTC][oftc] `#moc` IRC channel.

You are welcome to open issues or submit pull requests concerning our documentation via the [ESI GitHub repository][gh].

We have a mailing list at esi@lists.massopen.cloud. Go [here](https://mail.massopen.cloud/mailman/listinfo/esi) to subscribe.

[oftc]: https://www.oftc.net/
[gh]: https://github.com/CCI-MOC/esi
