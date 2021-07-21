import tests.functional.base as base

# NOTE: this "test suite" will probably be deleted. it's here solely to allow me to
# run the tests to make sure setup/cleanup works.
class TestTest(base.EsiFunctionalBase):
    def setUp(self):
        super(TestTest, self).setUp()
        self._init_dummy_cloud('test', 'owner')
        self._init_client('test')
        self.dummy_node = self._new_dummy_node('test')

    def test_setup(self):
        result = self.offer_create('test', self.dummy_node,
                start_time="2021-12-12")
        print(result)
        self.assertEqual("0", "0")
