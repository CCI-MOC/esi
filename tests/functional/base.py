import os
import configparser
import tempfile
from tempest.lib.cli import base
from tempest.lib.common.utils.data_utils import rand_name

class EsiFunctionalBase(base.ClientTestBase):
    """This class handles calls to the esi-leap client"""

    def setUp(self):
        super(EsiFunctionalBase, self).setUp()
        self.cfg = self._init_config()
        self._init_clients()
        self.dummy_node = self._init_dummy_node()

    def _init_config(self):
        # allow custom configuration to be passed in via env var
        cfg_file_path = os.environ.get('OS_ESI_CFG_PATH',
                '/etc/esi-leap/esi-leap.conf')
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
                # TODO: add support for keystone v2 (this is v3-only atm)
                auth_opts = ['auth_url', 'username', 'password', 'project_name',
                        'user_domain_name', 'project_domain_name']
                for opt in auth_opts:
                    if opt == 'project_name':
                        parsed['admin_project_name'] = auth_get('project_name')
                    else:
                        parsed[opt] = auth_get(opt)
        except (configparser.NoOptionError):
            self.fail("Missing option %s in configuration file." % opt)
            
        return parsed

    def _get_clients(self):
        # NOTE: ClientTestBase's constructor requires this to be implemented, but
        # to initialize our clients, we need ClientTestBase's constructor to have
        # been called. We return nothing and leave the job up to _init_clients().
        return {}

    def _init_clients(self):
        venv_name = os.environ.get('OS_VENV_NAME', default='functional')
        cli_dir = os.path.join(os.path.abspath('.'), '.tox/%s/bin' % venv_name)

        def init_client(project_name):
            if self.cfg['auth_type'] != 'noauth':
                return base.CLIClient(cli_dir=cli_dir,
                        username=self.cfg['username'],
                        password=self.cfg['password'],
                        user_domain_name=self.cfg['user_domain_name'],
                        tenant_name=self.cfg[project_name],
                        project_domain_name=self.cfg['project_domain_name'],
                        uri=self.cfg['auth_url'])
            else:
                return base.CLIClient(cli_dir=cli_dir)

        # Initialize admin client, used to set up testing environment.
        admin_client = init_client('admin_project_name')
        self.clients['admin'] = admin_client

        # Initialize dummy project for the client that will execute test commands.
        dummy_project = self._init_dummy_project()
        for listing in dummy_project:
            for field in 'id', 'name':
                if listing['Field'] == field:
                    self.cfg['test_project_%s' % field] = listing['Value']

        test_client = init_client('test_project_name')
        self.clients['test'] = test_client
        self.addCleanup(self._cleanup_dummy_project)
        
    def _init_dummy_project(self):
        name = rand_name('EsiTestProject')
        description = '"Test project created by Tempest for ESI functional testing"'
        domain = self.cfg['project_domain_name']
        return self.os_execute('project create', '',
                '--description %s --domain %s --enable %s' %
                (description, domain, name), 'admin')

    def _cleanup_dummy_project(self):
        self.os_execute('project delete', '', '%s' % self.cfg['test_project_id'],
                'admin')

    def _init_dummy_node(self):
        node_dir = self.cfg['dummy_node_dir']
        if not os.path.exists(node_dir):
            os.mkdir(node_dir)
        if not os.path.isdir(node_dir):
            raise OSError('Error creating dummy node @ %s: not a directory'
                    % node_dir)

        dummy_node_info = [
                '{',
                '   "project_owner_id": "%s",' % self.cfg['test_project_id'],
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

        self.addCleanup(self._cleanup_dummy_node)
        return { 'path': node_path, 'uuid': os.path.basename(node_path) }

    def _cleanup_dummy_node(self):
        os.remove(self.dummy_node['path'])

    def os_execute(self, cmd, flags='', params='', client='test', parse=True):
        """Runs an openstack command via python-openstackclient.
        arguments:
            cmd - openstack command to run (e.g. "esi offer list")
            flags - flags for the openstack command
            params - positional arguments for the command (if required)
            client - which client (admin/test) to use to execute the command
            parse - determines if parsed output or raw output is returned
        returns:
            if parse=True - a list of dicts containing the parsed cmd output
            if parse=False - the raw output of the command as a string
        """
        result = (
                self.clients[client].openstack(cmd, flags, params) if
                self.cfg['auth_type'] != 'noauth' else
                execute('openstack', cmd, flags, params, cli_dir=self.client.cli_dir))

        return self.parser.listing(result) if parse else result
