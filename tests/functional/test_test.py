import tests.functional.base as base

# NOTE: this "test suite" will probably be deleted. it's here solely to allow me to
# run the tests to make sure setup/cleanup works.
class TestTest(base.EsiFunctionalBase):
    def test_setup(self):
        self.assertEqual("0", "0")
