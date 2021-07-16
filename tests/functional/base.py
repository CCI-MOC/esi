import os
import configparser
from tempest.lib.cli import base
from tempest.lib.common.utils.data_utils import rand_name

class EsiFunctionalBase(base.ClientTestBase):
    """This class handles calls to the esi-leap client"""

    def setUp(self):
        super(EsiFunctionalBase, self).setUp()
        self.cfg = self._get_config()
        self.client = self._init_client()

    def _get_config(self):
        # allow custom configuration to be passed in via env var
        cfg_file_path = os.environ.get('OS_ESI_CFG_PATH', '/etc/esi-leap/esi-leap.conf')
        cfg_parser = configparser.ConfigParser()
        if not cfg_parser.read(cfg_file_path):
            self.fail('Could not open config file %s for reading' % cfg_file_path)

        # attempts to read authentication credentials in this order:
        # 1) [keystone] section of config file
        # 2) [keystone_authtoken] section of config file
        # 3) from the environment variables (e.g. OS_PASSWORD, etc)
        def auth_get(val):
            for sect in 'keystone', 'keystone_authtoken':
                if cfg_parser.has_section(sect):
                    try:
                        return cfg_parser.get(sect, val)
                    except:
                        pass
            x = os.environ.get('OS_%s' % val.upper())
            if x != None:
                return x
            else:
                raise configparser.NoOptionError

        parsed = {}
        try:
            if cfg_parser.has_section('dummy_node'):
                opt = 'dummy_node_dir'
                parsed[opt] = cfg_parser.get('dummy_node', opt)
            opt = 'auth_type'
            parsed[opt] = auth_get(opt)
            if not parsed[opt] == 'noauth':
                auth_opts = ['auth_url', 'username', 'password', 'project_name']
                for opt in auth_opts:
                    parsed[opt] = auth_get(opt) 
        except (configparser.NoOptionError):
            self.fail("Missing option %s in configuration file." % opt)
            
        return parsed

    def _init_client(self):
        venv_name = os.environ.get('OS_VENV_NAME', default='functional')
        cli_dir = os.path.join(os.path.abspath('.'), '.tox/%s/bin' % venv_name)
        
        if self.cfg['auth_type'] != 'noauth':
            client = base.CLIClient(cli_dir=cli_dir,
                                    username=self.cfg['username'],
                                    password=self.cfg['password'],
                                    tenant_name=self.cfg['project_name'],
                                    uri=self.cfg['auth_url'])
        else:
            client = base.CLIClient(cli_dir=cli_dir)

        return client
