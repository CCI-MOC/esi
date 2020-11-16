# Elastic Secure Infrastructure (ESI)

We want to create a set of services/systems to permit multiple tenants to flexibly allocate baremetal machines from a pool of available hardware, create networks, attach baremetal nodes and networks, and to optionally provision an operating system on those systems through the use of an associated provisioning service.

## Activities

### Past

- [Ironic node Multi-Tenancy](https://docs.openstack.org/ironic/latest/admin/node-multitenancy.html)
- Support for the Cisco Nexus switch in [networking-ansible](https://opendev.org/x/networking-ansible)
- [ESI Leap](https://github.com/cci-moc/esi-leap): a simple leasing service
    - [python-esileapclient](https://github.com/cci-moc/python-esileapclient)
- [python-esiclient](https://github.com/CCI-MOC/python-esiclient): CLI commands to simplify OpenStack workflows
- Test deployment of single-cloud hardware leasing system in [Mass Open Cloud (MOC)](https://massopen.cloud/)
    - External provisioning tests

### Current

- Test deployment of single-cloud hardware leasing system in [Mass Open Cloud (MOC)](https://massopen.cloud/)
    - Scale testing [[network](docs/network-load-testing.md)]
    - Usability tests
    - Test of [Cinder Ceph ISCSI driver](https://review.opendev.org/#/c/662829/)
- Integration of [Keylime](https://keylime.dev/) attestation in Ironic

### Future

- Deployment of multi-cloud hardware leasing system for MOC and [Open Cloud Testbed (OCT)](https://massopen.cloud/open-cloud-testbed-developing-a-testbed-for-the-research-community-exploring-next-generation-cloud-platforms/)
- Multiple ESI architecture: allow creation of a bare metal cluster comprised of hardware leased from multiple ESIs
- Recursive ESI architecture: allow hardware leased from one ESI to be offered up in another

## Code Repositories

Our code development features a mix of upstream OpenStack work and custom ESI code.

- OpenStack
    - [ironic](https://github.com/openstack/ironic)
    - [networking-ansible](https://opendev.org/x/networking-ansible)
- ESI
    - [esi-leap](https://github.com/cci-moc/esi-leap): a simple leasing service
        - [python-esileapclient](https://github.com/cci-moc/python-esileapclient)
    - [python-esiclient](https://github.com/CCI-MOC/python-esiclient): CLI commands to simplify OpenStack workflows

## Documentation

### Operations

- [Deployment][deployment]: a method of deploying and configuring ESI
- [Usage][usage]: common commands used by ESI administrators and users
- [Provisioning Scenarios][provisioning-scenarios]: provisioning scenarios for nodes leased through ESI

### Planning

- [Requirements][reqs]: initial requirements of the ESI project
- [Design][design]: initial implementation  plans
- [Upstream Features][upstream]: initial plans for changes we will make in upstream projects

[design]: docs/esi-design.md
[reqs]: docs/esi-requirements.md
[upstream]: docs/upstream-features.md
[deployment]: docs/deployment.md
[usage]: docs/usage.md
[provisioning-scenarios]: docs/provisioning-scenarios.md

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

You can contact the ESI development team on the Freenode `#moc` IRC channel.

You are welcome to open issues or submit pull requests concerning our documentation via the [ESI GitHub repository][gh].

We have a mailing list at esi@lists.massopen.cloud. Go [here](https://mail.massopen.cloud/mailman/listinfo/esi) to subscribe.

[gh]: https://github.com/CCI-MOC/esi
