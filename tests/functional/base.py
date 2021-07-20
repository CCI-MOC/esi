import os
import configparser
import tempfile
from tempest.lib.cli import base
from tempest.lib.common.utils import data_utils

class EsiFunctionalBase(base.ClientTestBase):
    """This class handles calls to the esi-leap client"""

    def setUp(self):
        super(EsiFunctionalBase, self).setUp()
        self.config = {}
        self.client_info = {}
        self.dummy_nodes = []

        self._init_config()
        self._init_client('admin')
        self._init_dummy_cloud('test')
        self._init_client('test')
        self.dummy_nodes.append(self._new_dummy_node())

    def _get_clients(self):
        # NOTE: ClientTestBase's constructor requires this to be implemented, but
        # to initialize our clients, we need ClientTestBase's constructor to have
        # been called. We return nothing and leave the job up to _init_clients().
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
            self.fail('Could not open config file %s for reading' % cfg_file_path)
            return -1

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

        admin_auth = {}
        try:
            if cfg_parser.has_section('dummy_node'):
                opt = 'dummy_node_dir'
                self.config[opt] = cfg_parser.get('dummy_node', opt)
            # TODO: add support for keystone v2 (this is v3-only atm)
            auth_opts = ['auth_type', 'auth_url', 'username', 'password',
                    'project_name', 'user_domain_name', 'project_domain_name']
            for opt in auth_opts:
                admin_auth[opt] = auth_get(opt)
        except (configparser.NoOptionError):
            self.fail("Missing option %s in configuration file." % opt)
            return -1
        finally:
            self.client_info['admin'] = admin_auth
        return 0

    def _init_client(self, client):
        auth = self.client_info[client]
        self.clients[client] = base.CLIClient(
                cli_dir=self.config['cli_dir'],
                username=auth['username'],
                password=auth['password'],
                tenant_name=auth['project_name'],
                user_domain_name=auth['user_domain_name'],
                project_domain_name=auth['project_domain_name'],
                identity_api_version='3',
                uri=auth['auth_url'])
        
    def _init_dummy_cloud(self, name):
        cloud = {}
        for field in 'project', 'user', 'role':
            cloud[field] = { 'name': data_utils.rand_name('esi-%s-%s'
                    % (field, name)) }

        def initialize(field, params):
            output = self.parser.listing(self.clients['admin'].openstack(
                '%s create %s' % (field, cloud[field]['name']), '', params))
            for row in output:
                if row['Field'] == 'id':
                    cloud[field]['id'] = row['Value']
                    break
        
        pw = data_utils.rand_password()
        initialize('project', '--domain default --enable')
        initialize('user', '--domain default --password %s --enable' % pw)
        initialize('role', '')
        self.clients['admin'].openstack('role add', '',
                '--user %s --project %s %s' % (cloud['user']['name'],
                    cloud['project']['name'], cloud['role']['name']))

        self.client_info[name] = {
                'auth_type': 'password',
                'auth_url': self.client_info['admin']['auth_url'],
                'username': cloud['user']['name'],
                'user_id': cloud['user']['id'],
                'password': pw,
                'project_name': cloud['project']['name'],
                'project_id': cloud['project']['id'],
                'user_domain_name': 'default',
                'project_domain_name': 'default'}

        for field in cloud.keys():
            self.addCleanup(self.clients['admin'].openstack, 
                    '%s delete' % field, '', '%s' % cloud[field]['name'])
        return cloud

    def _new_dummy_node(self):
        node_dir = self.config['dummy_node_dir']
        if not os.path.exists(node_dir):
            os.mkdir(node_dir)
        if not os.path.isdir(node_dir):
            raise OSError('Error creating dummy node @ %s: not a directory'
                    % node_dir)

        dummy_node_info = [
                '{',
                '   "project_owner_id": "%s",' % 
                    self.client_info['test']['project_id'],
                '   "server_config": {',
                '       "example_attribute": "example server config",',
                '       "cpu_type": "Intel Xeon",',
                '       "cores": 16,',
                '       "ram_gb": 512,',
                '       "storage_type": "Samsung SSD",',
                '       "storage_size_gb": 1024',
                '   }',
                '}']

        node = tempfile.mkstemp(prefix='', dir=node_dir, text=True)
        node_fd = node[0]
        node_path = node[1]
        for line in dummy_node_info:
            os.write(node_fd, ('%s\n' % line).encode())
        os.close(node_fd)

        self.addCleanup(os.remove, node_path)
        return { 'path': node_path, 'uuid': os.path.basename(node_path) }
