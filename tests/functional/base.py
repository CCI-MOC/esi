import os
import configparser
from tempest.lib.cli import base

class EsiFuntionalBase(base.ClientTestBase):
    """This class handles calls to the esi-leap client"""

    def setUp(self):
        super(EsiFunctionalBase, self).setUp()
        self.cfg = self._get_config()
        self.client = self._init_client()

    def _get_config():
        cfg_file_path = os.environ.get('OS_ESI_CFG_PATH', '/etc/esi-leap/esi-leap.conf')
        cfg_parser = configparser.ConfigParser()
        if not cfg_parser.read():
            self.fail('Could not open config file %s for reading' % cfg_file_path)



    def _init_client(self):
        venv_name = os.environ.get('OS_VENV_NAME', default='functional')
        cli_path = os.path.join(os.path.abspath('.'), '.tox/%s/bin' % venv_name)

        
