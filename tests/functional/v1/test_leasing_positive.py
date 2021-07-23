import tests.functional.base as base

class PositiveLeasingTests(base.EsiFunctionalBase):
    def setUp(self):
        super(PositiveLeasingTests, self).setUp()
        self._init_dummy_cloud('owner', 'owner')
        self._init_dummy_cloud('lessee', 'lessee')

        self._init_client('owner')
        self._init_client('lessee')

        self.dummy_node = self._new_dummy_node('owner')
        self.offers = {}
        self.leases = {}

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
