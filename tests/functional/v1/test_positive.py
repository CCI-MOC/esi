from tests.functional.v1.common import ESIBaseTestClass
from tests.functional.utils.dummy_node import DummyNode

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

    def test_offer_owner(self):
        """ Tests basic functionality of "esi offer create/list/show/delete"
                when executed by a node-owning project.
            Test steps:
            1) Create an offer for an owned node.
            2) Check that offer details were returned.
            3) Check that the output of 'offer list' contains the new offer.
            4) Check that the output of 'offer show' contains the details of
                the new offer.
            5) (cleanup) Delete the offer created in step 1. """
        offer = self.offer_create(self.clients['owner'], self.dummy_node,
                resource_type='dummy_node')
        self.assertNotEqual(offer, {})
        self.addCleanup(self.offer_delete, self.clients['owner'],
                offer['uuid'])

        listings = self.offer_list(self.clients['owner'])
        self.assertNotEqual(listings, [])
        self.assertIn(offer['uuid'], [x['UUID'] for x in listings])

        details = self.offer_show(self.clients['owner'], offer['uuid'])
        for field in offer.keys():
            self.assertEqual(offer[field], details[field])

    def test_lease_owner(self):
        """ Tests basic functionality of "esi lease create/list/show/delete"
                when called by an owner.
            Test steps:
            1) Create a lease for an owned node for the lessee.
            2) Check that lease details were returned.
            3) Check that the output of 'lease list' contains the new lease.
            4) Check that the output of 'lease show' contains the details of
                the new lease.
            5) (cleanup) Delete the lease created in step 1. """
        lease = self.lease_create(self.clients['owner'], self.dummy_node,
                self.client_info['lessee']['project_name'],
                resource_type='dummy_node')
        self.assertNotEqual(lease, {})
        self.addCleanup(self.lease_delete, self.clients['owner'],
                lease['uuid'])

        listings = self.lease_list(self.clients['owner'])
        self.assertNotEqual(listings, [])
        self.assertIn(lease['uuid'], [x['UUID'] for x in listings])

        details = self.lease_show(self.clients['owner'], lease['uuid'])
        for field in lease.keys():
            self.assertEqual(lease[field], details[field])

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
            7) (owner) (cleanup) Delete the offer created in step 1. """
        offer = self.offer_create(self.clients['owner'], self.dummy_node,
                lessee=self.client_info['lessee']['project_name'],
                resource_type='dummy_node')
        self.assertNotEqual(offer, {})
        self.addCleanup(self.offer_delete, self.clients['owner'],
                offer['uuid'])

        listings = self.offer_list(self.clients['lessee'])
        self.assertNotEqual(listings, [])
        self.assertIn(offer['uuid'], [x['UUID'] for x in listings])

        details = self.offer_show(self.clients['lessee'], offer['uuid'])
        for field in offer.keys():
            self.assertEquals(offer[field], details[field])

        lease = self.offer_claim(self.clients['lessee'], offer['uuid'])
        self.assertNotEqual(lease, {})
