import os
import configparser
import tempfile
import json
from tempest.lib.cli import base
from tempest.lib.common.utils import data_utils

class EsiFunctionalBase(base.ClientTestBase):
    """This class handles calls to the esi-leap client"""

    def setUp(self):
        super(EsiFunctionalBase, self).setUp()
        self.config = {}
        self.client_info = {}

        self._init_config()
        self._init_client('admin')
        self._init_roles()

    def _get_clients(self):
        #NOTE: ClientTestBase's constructor requires this to be implemented, but
        #to initialize our clients, we need ClientTestBase's constructor to have
        #been called. We return nothing and leave the job up to _init_clients().
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
        self.clients[client] = EsiCliClient(
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

        cloud = {}
        for field in 'project', 'user':
            cloud[field] = { 'name': data_utils.rand_name('esi-%s-%s'
                    % (field, name)) }

        def initialize(field, params):
            output = self.clients['admin'].openstack('%s create %s' %
                    (field, cloud[field]['name']), '', params)
            cloud[field]['id'] = self.parse_details(output)['id']

        pw = data_utils.rand_password()
        initialize('project', '--domain default --enable')
        initialize('user', '--domain default --password %s --enable' % pw)
        self.clients['admin'].openstack('role add', '',
                '--user %s --project %s esi_leap_%s' % (cloud['user']['name'],
                    cloud['project']['name'], role))

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
        self.addCleanup(self.clients['admin'].openstack, 'role remove', '',
                '--user %s --project %s esi_leap_%s' % (cloud['user']['name'],
                    cloud['project']['name'], role))
        return 0

    def _init_roles(self):
        for role in 'esi_leap_owner', 'esi_leap_lessee':
            try:
                self.clients['admin'].openstack('role show', '', '%s' % role)
            except:
                self.clients['admin'].openstack('role create', '', '%s' % role)
                self.addCleanup(self.clients['admin'].openstack,
                        'role delete', '', '%s' % role)

    def _new_dummy_node(self, owner):
        node_dir = self.config['dummy_node_dir']
        if not os.path.exists(node_dir):
            os.mkdir(node_dir)
        if not os.path.isdir(node_dir):
            raise OSError('Error creating dummy node @ %s: not a directory'
                    % node_dir)

        dummy_node_info = [
                '{',
                '   "project_owner_id": "%s",' % 
                    self.client_info[owner]['project_id'],
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

    def _kwargs_to_flags(self, args):
        flag_string = ''
        project_flags = ('owner', 'lessee', 'project')
        string_flags = ('start_time', 'end_time', 'name', 'resource_type',
                'resource_uuid', 'status', 'time_range', 'availability_range'
                'offer_uuid', 'from_owner_id', 'to_owner_id')
        json_flags = ('properties')
        standalone_flags = ('long')

        for flag in args.keys():
            if args[flag] != None:
                tmp = ' --%s' % flag.replace('_', '-')
                if flag in string_flags:
                    flag_string += '%s "%s"' % (tmp, args[flag])
                elif flag in project_flags:
                    flag_string += '%s %s' % (tmp,
                            self.client_info[args[flag]]['project_name'])
                elif flag in json_flags:
                    flag_string += '%s "%s"' % (tmp, json.dumps(args[flag]))
                elif flag in standalone_flags:
                    flag_string += tmp

        return flag_string

    def _merge_kwargs(self, default, args):
        for key in default.keys():
            if key in args.keys():
                default[key] = args[key]
        return default

    def parse_details(self, output):
        listing = self.parser.listing(output)
        details = {}
        for item in listing:
            details.update({ item['Field']: item['Value'] })
        return details

    def offer_create(self, client, node, parse=True, **kwargs):
        flags_default = { 'resource_type': 'dummy_node' }
        for flag in 'start_time', 'end_time', 'lessee', 'name', 'properties':
            flags_default[flag] = None

        flags = self._kwargs_to_flags(self._merge_kwargs(flags_default, kwargs))
        output = self.clients[client].esi('offer create', flags, node['uuid'])

        return self.parse_details(output) if parse else output

    def offer_delete(self, client, offer_uuid):
        return self.clients[client].esi('offer delete', '', offer_uuid)

    def offer_list(self, client, parse=True, **kwargs):
        flags_default = {}
        for flag in ('long', 'status', 'project', 'resource_uuid',
                'resource_type', 'time_range', 'availability_range'):
            flags_default[flag] = None

        flags = self._kwargs_to_flags(self._merge_kwargs(flags_default, kwargs))
        output = self.clients[client].esi('offer list', flags, '')

        return self.parser.listing(output) if parse else output

    def offer_show(self, client, offer_uuid, parse=True):
        output = self.clients[client].esi('offer show', '', offer_uuid)
        return self.parse_details(output) if parse else output

    def offer_claim(self, client, offer_uuid, parse=True, **kwargs):
        flags_default = {}
        for flag in 'start_time', 'end_time', 'properties':
            flags_default[flag] = None

        flags = self._kwargs_to_flags(self._merge_kwargs(flags_default, kwargs))
        output = self.clients[client].esi('offer claim', flags, offer_uuid)

        return self.parse_details(output) if parse else output

    def lease_create(self, client, node, lessee, parse=True, **kwargs):
        flags_default = { 'resource_type': 'dummy_node' }
        for flag in 'start_time', 'end_time', 'name', 'properties':
            flags_default[flag] = None

        flags = self._kwargs_to_flags(self._merge_kwargs(flags_default, kwargs))
        output = self.clients[client].esi('lease create', flags, '%s %s' %
                (node['uuid'], self.client_info[lessee]['project_name']))

        return self.parse_details(output) if parse else output

    def lease_list(self, client, parse=True, **kwargs):
        flags_default = {}
        for flag in ('long', 'all', 'status', 'offer_uuid', 'time_range',
                'project', 'owner', 'resource_type', 'resource_uuid'):
            flags_default[flag] = None

        flags = self._kwargs_to_flags(self._merge_kwargs(flags_default, kwargs))
        output = self.clients[client].esi('lease list', flags, '')

        return self.parser.listing(output) if parse else output

    def lease_delete(self, client, lease_uuid):
        return self.clients[client].esi('lease delete', '', lease_uuid)

    def lease_show(self, client, lease_uuid, parse=True):
        output = self.clients[client].esi('lease show', '', lease_uuid)
        return self.parse_details(output) if parse else output

    def owner_change_create(self, client, owner_prev, owner_new, node, 
            parse=True, **kwargs):
        flags_default = { 'resource_type': 'dummy_node' }
        for flag in 'start_time', 'end_time':
            flags_default[flag] = None

        flags = self._kwargs_to_flags(self._merge_kwargs(flags_default, kwargs))
        output = self.clients[client].esi('owner change create', flags,
                '%s %s %s' % (self.client_info[owner_prev]['project_id'],
                    self.client_info[owner_new]['project_id'], node['uuid']))

        return self.parse_details(output) if parse else output

    def owner_change_list(self, client, parse=True, **kwargs):
        flags_default = {}
        for flag in ('long', 'status', 'time_range', 'from_owner_id',
                'to_owner_id', 'resource_uuid', 'resource_type'):
            flags_default[flag] = None

        flags = self._kwargs_to_flags(self._merge_kwargs(flags_default, kwargs))
        output = self.clients[client].esi('owner change list', flags, '')

        return self.parser.listing(output) if parse else output

    def owner_change_delete(self, client, owner_change_uuid):
        return self.clients[client].esi('owner change delete', '',
                owner_change_uuid)

    def owner_change_show(self, client, owner_change_uuid, parse=True):
        output = self.clients[client].esi('owner change show',
                '', owner_change_uuid)
        return self.parse_details(output) if parse else output

class EsiCliClient(base.CLIClient):
    def esi(self, action, flags='', params='', fail_ok=False,
            merge_stderr=False):
        return self.openstack('esi %s' % action, '',
                '%s %s' % (flags, params), fail_ok, merge_stderr)
