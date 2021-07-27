import tests.functional.base as base
import tests.functional.utils.output_utils as utils

class ESIBaseTestClass(base.ESIFunctionalBase):
    def offer_create(self, client, node, parse=True, **kwargs):
        valid_flags = ('resource_type', 'start_time', 'end_time', 'lessee',
                'name', 'properties')
        flags = utils.kwargs_to_flags(valid_flags, kwargs)
        output = client.esi('offer create', flags, node.uuid)

        return utils.parse_details(output) if parse else output

    def offer_delete(self, client, offer_uuid):
        return client.esi('offer delete', '', offer_uuid)

    def offer_list(self, client, parse=True, **kwargs):
        valid_flags = ('long', 'status', 'project', 'resource_uuid',
                'resource_type', 'time_range', 'availability_range')
        flags = utils.kwargs_to_flags(valid_flags, kwargs)
        output = client.esi('offer list', flags, '')

        return self.parser.listing(output) if parse else output

    def offer_show(self, client, offer_uuid, parse=True):
        output = client.esi('offer show', '', offer_uuid)
        return utils.parse_details(output) if parse else output

    def offer_claim(self, client, offer_uuid, parse=True, **kwargs):
        valid_flags = ('start_time', 'end_time', 'properties')
        flags = utils.kwargs_to_flags(valid_flags, kwargs)
        output = client.esi('offer claim', flags, offer_uuid)

        return utils.parse_details(output) if parse else output

    def lease_create(self, client, node, lessee, parse=True, **kwargs):
        valid_flags = ('resource_type', 'start_time', 'end_time', 'name',
                'properties')
        flags = utils.kwargs_to_flags(valid_flags, kwargs)
        output = client.esi('lease create', flags, '%s %s' %
                (node.uuid, lessee))

        return utils.parse_details(output) if parse else output

    def lease_list(self, client, parse=True, **kwargs):
        valid_flags = ('long', 'all', 'status', 'offer_uuid', 'time_range',
                'project', 'owner', 'resource_type', 'resource_uuid')
        flags = utils.kwargs_to_flags(valid_flags, kwargs)
        output = client.esi('lease list', flags, '')

        return self.parser.listing(output) if parse else output

    def lease_delete(self, client, lease_uuid):
        return client.esi('lease delete', '', lease_uuid)

    def lease_show(self, client, lease_uuid, parse=True):
        output = client.esi('lease show', '', lease_uuid)
        return utils.parse_details(output) if parse else output
