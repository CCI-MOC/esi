# Elastic Secure Infrastructure

We want to create a set of services/systems to permit multiple tenants to flexibly allocate baremetal machines from a pool of available hardware, create networks, attach baremetal nodes and networks, and to optionally provision an operating system on those systems through the use of an associated provisioning service.

## References

This project is largely following the vision described in the follow papers:

- "[A secure cloud with minimal provider trust][0]"
- "[HIL: designing an exokernel for the data center][1]"

  This paper describes the initial implementation of the isolation service. You can find the code for this project at <https://github.com/cci-moc/hil>.
- "[Supporting Security Sensitive Tenants in a Bare-Metal Cloud][2]"
- "[M2: Malleable Metal as a Service][3]"

  This paper describes the original implementation of the provisioning service, called "BMI" or "M2". You can find the code for BMI at <https://github.com/cci-moc/m2>.

[0]: https://www.usenix.org/conference/hotcloud18/presentation/mosayyebzadeh
[1]: https://open.bu.edu/handle/2144/19198
[2]: https://www.usenix.org/conference/atc19/presentation/mosayyebzadeh
[3]: https://ieeexplore.ieee.org/abstract/document/8360313

(See [references.bib](references.bib) for complete references to these papers.)

## Documentation

- The [requirements document][reqs] describes the basic requirements of the ESI project.
- The [design document][design] describes how are are implementing those requirements.
- The [upstream features][upstream] document describes changes we will need to make in upstream projects to support those requirements or to allow an upstream project to take advantage of ESI.
- The [deployment document][deployment] describes a method of deploying and configuring ESI.
- The [usage document][usage] lists common commands used by administrators and users.

[design]: docs/esi-design.md
[reqs]: docs/esi-requirements.md
[upstream]: docs/upstream-features.md
[deployment]: docs/deployment.md
[usage]: docs/usage.md

## Contact and Contribution

You can contact the ESI development team on the Freenode `#moc` IRC channel.

You are welcome to open issues or submit pull requests concerning our documentation via the [GitHub repository][gh].

We are currently tracking project tasks on [our Trello board][trello].

[gh]: https://github.com/CCI-MOC/esi
[trello]: https://trello.com/b/1MDt78E9/esi-trask-tracking
