from tests.functional.v1.common import ESIBaseTestClass
from tests.functional.utils.dummy_node import DummyNode
from testtools.matchers import Not, Equals, NotEquals, Contains

class PositiveTests(ESIBaseTestClass):
    @classmethod
    def setUpClass(cls):
        super(PositiveTests, cls).setUpClass()
        cls._init_dummy_cloud(cls, 'owner', 'owner')
        cls._init_dummy_cloud(cls, 'lessee', 'lessee')

    def setUp(self):
        super(PositiveTests, self).setUp()
        self.clients = PositiveTests.clients
        self.client_info = PositiveTests.client_info
        self.dummy_node = DummyNode(PositiveTests.config['dummy_node_dir'],
                self.client_info['owner']['project_id'])

    # NOTE: The assertThat/expectThat syntax was chosen over the more
    #       standard assertEquals/assertIn/etc. syntax because if an assert
    #       statement fails, the test immediately ends, which can result in
    #       offers/leases not getting deleted. expectThat() on the other hand,
    #       will not force an end to the test and allows delete commands to
    #       run. This was chosen over addCleanup() because addCleanup() runs
    #       unconditionally, which will result in an attempt to delete an
    #       already deleted test.

    def test_offer_owner(self):
        """ Tests basic functionality of "esi offer create/list/show/delete"
                when executed by a node-owning project.
            Test steps:
            1) Create an offer for an owned node.
            2) Check that offer details were returned.
            3) Check that the output of 'offer list' contains the new offer.
            4) Check that the output of 'offer show' contains the details of
                the new offer.
            5) Delete the offer created in step 1.
            6) Check that the output of 'offer list' does not contain the
                deleted offer. """
        offer = self.offer_create(self.clients['owner'], self.dummy_node,
                resource_type='dummy_node')
        self.assertThat(offer, NotEquals({}))

        listings = self.offer_list(self.clients['owner'])
        self.expectThat(listings, NotEquals([]))
        self.expectThat([x['UUID'] for x in listings], Contains(offer['uuid']))

        details = self.offer_show(self.clients['owner'], offer['uuid'])
        for field in offer.keys():
            self.expectThat(offer[field], Equals(details[field]))

        self.offer_delete(self.clients['owner'], offer['uuid'])
        listings = self.offer_list(self.clients['owner'])
        self.assertThat([x['UUID'] for x in listings],
                Not(Contains(offer['uuid'])))

    def test_lease_owner(self):
        """ Tests basic functionality of "esi lease create/list/show/delete"
                when called by an owner.
            Test steps:
            1) Create a lease for an owned node for the lessee.
            2) Check that lease details were returned.
            3) Check that the output of 'lease list' contains the new lease.
            4) Check that the output of 'lease show' contains the details of
                the new lease.
            5) Delete the lease created in step 1.
            6) Check that the output of 'lease list' does not contain the
                deleted lease. """
        lease = self.lease_create(self.clients['owner'], self.dummy_node,
                self.client_info['lessee']['project_name'],
                resource_type='dummy_node')
        self.assertThat(lease, NotEquals({}))

        listings = self.lease_list(self.clients['owner'])
        self.expectThat(listings, NotEquals([]))
        self.expectThat([x['UUID'] for x in listings], Contains(lease['uuid']))

        details = self.lease_show(self.clients['owner'], lease['uuid'])
        for field in lease.keys():
            self.expectThat(lease[field], Equals(details[field]))

        self.lease_delete(self.clients['owner'], lease['uuid'])
        listings = self.lease_list(self.clients['owner'])
        self.assertThat([x['UUID'] for x in listings],
                Not(Contains(lease['uuid'])))

    def test_offer_lessee(self):
        """ Tests basic functionality of "esi offer claim/show/list" when
                called by a lessee.
            Test steps:
            1) (owner) Create an offer for an owned node for the lessee.
            2) (owner) Check that offer details were returned.
            3) (lessee) Check that the output of 'offer list' contains the
                new offer.
            4) (lessee) Check that the output of 'offer show' contains the
                details of the new offer.
            5) (lessee) Claim the offer created in step 1.
            6) (lessee) Check that lease details were returned.
            7) (owner) Delete the offer created in step 5.
            8) (lessee) Check that the output of 'offer list' does not contain
                the deleted lease. """
        offer = self.offer_create(self.clients['owner'], self.dummy_node,
                lessee=self.client_info['lessee']['project_name'],
                resource_type='dummy_node')
        self.assertThat(offer, NotEquals({}))

        listings = self.offer_list(self.clients['lessee'])
        self.expectThat(listings, NotEquals([]))
        self.expectThat([x['UUID'] for x in listings], Contains(offer['uuid']))

        details = self.offer_show(self.clients['lessee'], offer['uuid'])
        for field in offer.keys():
            self.expectThat(offer[field], Equals(details[field]))

        lease = self.offer_claim(self.clients['lessee'], offer['uuid'])
        self.expectThat(lease, NotEquals({}))

        self.offer_delete(self.clients['owner'], offer['uuid'])
        listings = self.offer_list(self.clients['lessee'])
        self.assertThat([x['UUID'] for x in listings],
                Not(Contains(offer['uuid'])))
