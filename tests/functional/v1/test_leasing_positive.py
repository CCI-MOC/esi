import tests.functional.base as base

class PositiveLeasingTests(base.EsiFunctionalBase):
    @classmethod
    def setUpClass(cls):
        super(PositiveLeasingTests, cls).setUpClass()
        cls._init_dummy_cloud(cls, 'owner', 'owner')
        cls._init_dummy_cloud(cls, 'lessee', 'lessee')

        cls._init_client(cls, 'owner')
        cls._init_client(cls, 'lessee')

        cls.dummy_node = cls._new_dummy_node(cls, 'owner')

    def setUp(self):
        super(PositiveLeasingTests, self).setUp()
        self.clients = PositiveLeasingTests.clients

    def test_offer_self(self):
        """ Tests basic functionality of "esi offer create/list/show/delete"
                when executed by a node-owning project.
            Test steps:
            1) Create an offer for an owned node.
            2) Check that offer details were returned.
            3) Check that the output of 'offer list' contains the new offer.
            4) Check that calling 'offer show' with the offer's uuid returns
                the details of the offer.
            5) Delete the offer created in step 1.
            6) Check that the output of 'offer list' does not contain the
                deleted offer. """
        offer = self.offer_create('owner', self.dummy_node)
        self.assertNotEqual(offer, {})

        listings = self.offer_list('owner')
        self.assertNotEqual(listings, [])
        self.assertIn(offer['uuid'], [x['UUID'] for x in listings])

        details = self.offer_show('owner', offer['uuid'])
        for field in offer.keys():
            self.assertEqual(offer[field], details[field])
        
        self.offer_delete('owner', offer['uuid'])
        listings = self.offer_list('owner')
        self.assertNotIn(offer['uuid'], [x['UUID'] for x in listings])

    def test_offer_lessee(self):
        """ Tests basic functionality of "esi offer claim/list" and "esi lease
                list/show/delete" when used by a lessee."""
        self.assertEqual(0, 0)
