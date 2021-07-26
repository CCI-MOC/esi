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
        cls.offers = {}
        cls.leases = {}

    def setUp(self):
        super(PositiveLeasingTests, self).setUp()
        self.clients = PositiveLeasingTests.clients
        self.dummy_node = PositiveLeasingTests.dummy_node

    def test_offer_create(self):
        """ Tests basic functionality for offer create.
            Checks if offer details were returned.
            Will update self.offers with the created offer. """
        offer = self.offer_create('owner', self.dummy_node)
        self.assertNotEqual(offer, {})

        self.offers.update({ 'test_offer': offer })

    def test_offer_list(self):
        """ Tests that node owner can list offers they created.
            Checks that a listing was returned and that the uuid from the
                offer previously created is present in the list. """
        listings = self.offer_list('owner')
        self.assertNotEqual(listings, [])
        self.assertIn(self.offers['test_offer']['uuid'],
                [x['UUID'] for x in listings])
