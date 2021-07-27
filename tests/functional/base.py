import os
import configparser
from tempest.lib.cli import base
from tempest.lib.common.utils import data_utils
from tests.functional.utils.output_utils import parse_details

class ESIFunctionalBase(base.ClientTestBase):
    @classmethod
    def setUpClass(cls):
        super(ESIFunctionalBase, cls).setUpClass()
        cls.clients = {}
        cls.config = {}
        cls.client_info = {}
        cls._cls_cleanups = []

        cls._init_config(cls)
        cls._init_client(cls, 'admin')
        cls._init_roles(cls)

    @classmethod
    def tearDownClass(cls):
        cls._cls_cleanups.reverse()
        for cleanup in cls._cls_cleanups:
            cleanup[0](*cleanup[1:])

    def _get_clients(self):
        # NOTE: ClientTestBase requires this to be implemented, but to
        # initialize our clients, we need ClientTestBase's constructor to have
        # been called. We return nothing and pass the job on to _init_clients().
        return {}

    def _init_config(self):
        venv_name = os.environ.get('OS_VENV_NAME', default='functional')
        self.config['cli_dir'] = os.path.join(os.path.abspath('.'), 
                '.tox/%s/bin' % venv_name)

        # allow custom configuration to be passed in via env var
        cfg_file_path = os.environ.get('OS_ESI_CFG_PATH',
                '/etc/esi-leap/esi-leap.conf')
        cfg_parser = configparser.ConfigParser()
        if not cfg_parser.read(cfg_file_path):
            self.fail('Could not open config file %s for reading' %
                    cfg_file_path)

        # attempts to read authentication credentials in this order:
        # 1) [keystone] section of config file
        # 2) [keystone_authtoken] section of config file
        # 3) from the environment variables (e.g. OS_PASSWORD, etc)
        admin_auth = {}
        try:
            if cfg_parser.has_section('dummy_node'):
                opt = 'dummy_node_dir'
                self.config[opt] = cfg_parser.get('dummy_node', opt)
            # TODO: add support for keystone v2 (this is v3-only atm)
            auth_opts = ['auth_type', 'auth_url', 'username', 'password',
                    'project_name', 'user_domain_name', 'project_domain_name']
            for opt in auth_opts:
                for sect in 'keystone', 'keystone_authtoken':
                    if cfg_parser.has_option(sect, opt):
                        admin_auth[opt] = cfg_parser.get(sect, opt)
                        break
                if opt not in admin_auth.keys():
                    x = os.environ.get('OS_%s' % opt.upper())
                    if x is not None:
                        admin_auth[opt] = x
                    else:
                        raise configparser.NoOptionerror
        except (configparser.NoOptionError):
            self.fail("Missing option %s in configuration file." % opt)

        self.client_info['admin'] = admin_auth

    def _init_client(self, name):
        auth = self.client_info[name]
        self.clients[name] = ESICLIClient(
                cli_dir=self.config['cli_dir'],
                username=auth['username'],
                password=auth['password'],
                tenant_name=auth['project_name'],
                user_domain_name=auth['user_domain_name'],
                project_domain_name=auth['project_domain_name'],
                identity_api_version='3',
                uri=auth['auth_url'])
        
    def _init_dummy_cloud(self, name, role):
        if role not in ('owner', 'lessee'):
            raise Exception('unknown role: %s' % role)

        username = data_utils.rand_name('esi-user-%s' % name)
        password = data_utils.rand_password()
        output = self.clients['admin'].openstack('user create %s' % username,
                '', '--domain default --password %s --enable' % password)
        user_id = parse_details(output)['id']

        project_name = data_utils.rand_name('esi-project-%s' % name)
        output = self.clients['admin'].openstack('project create %s' %
                project_name, '', '--domain default --enable')
        project_id = parse_details(output)['id']

        self.clients['admin'].openstack('role add', '',
                '--user %s --project %s esi_leap_%s' %
                    (username, project_name, role))

        self.client_info[name] = {
                'auth_type': 'password',
                'auth_url': self.client_info['admin']['auth_url'],
                'username': username,
                'user_id': user_id,
                'password': password,
                'project_name': project_name,
                'project_id': project_id,
                'user_domain_name': 'default',
                'project_domain_name': 'default'}
        self._init_client(self, name)

        self._cls_cleanups.append([self.clients['admin'].openstack,
                'user delete', '', '%s' % username])
        self._cls_cleanups.append([self.clients['admin'].openstack,
                'project delete', '', '%s' % project_name])
        self._cls_cleanups.append([self.clients['admin'].openstack,
                'role remove', '', '--user %s --project %s esi_leap_%s' %
                    (username, project_name, role)])

    def _init_roles(self):
        # TODO: find a way to make this play nice when running tests in parallel
        for role in 'esi_leap_owner', 'esi_leap_lessee':
            try:
                self.clients['admin'].openstack('role show', '', '%s' % role)
            except:
                self.clients['admin'].openstack('role create', '', '%s' % role)
                self._cls_cleanups.append([self.clients['admin'].openstack,
                        'role delete', '', '%s' % role])

class ESICLIClient(base.CLIClient):
    def esi(self, action, flags='', params='', fail_ok=False,
            merge_stderr=False):
        return self.openstack('esi %s' % action, '',
                '%s %s' % (flags, params), fail_ok, merge_stderr)
