import os
import configparser
import json
from tempest.lib.cli import base
from tempest.lib.cli import output_parser
from tempest.lib.common.utils import data_utils

class ESIFunctionalBase(base.ClientTestBase):
    @classmethod
    def setUpClass(cls):
        super(ESIFunctionalBase, cls).setUpClass()
        cls.clients = {}
        cls.config = {}
        cls.client_info = {}
        cls._cleanups = []

        cls._init_config(cls)
        cls._init_client(cls, 'admin')
        cls._init_roles(cls)

    @classmethod
    def tearDownClass(cls):
        cls._cleanups.reverse()
        for cleanup in cls._cleanups:
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

    def _init_client(self, client):
        auth = self.client_info[client]
        self.clients[client] = ESICLIClient(
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
        user_id = self.parse_details(self, output)['id']

        project_name = data_utils.rand_name('esi-project-%s' % name)
        output = self.clients['admin'].openstack('project create %s' %
                project_name, '', '--domain default --enable')
        project_id = self.parse_details(self, output)['id']

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

        self._cleanups.append([self.clients['admin'].openstack,
                'user delete', '', '%s' % username])
        self._cleanups.append([self.clients['admin'].openstack,
                'project delete', '', '%s' % project_name])
        self._cleanups.append([self.clients['admin'].openstack,
                'role remove', '', '--user %s --project %s esi_leap_%s' %
                    (username, project_name, role)])

    def _init_roles(self):
        for role in 'esi_leap_owner', 'esi_leap_lessee':
            try:
                self.clients['admin'].openstack('role show', '', '%s' % role)
            except:
                self.clients['admin'].openstack('role create', '', '%s' % role)
                self._cleanups.append([self.clients['admin'].openstack,
                        'role delete', '', '%s' % role])

    def _kwargs_to_flags(self, args):
        flag_string = ''
        project_flags = ('owner', 'lessee', 'project')
        string_flags = ('start_time', 'end_time', 'name', 'resource_type',
                'resource_uuid', 'status', 'time_range', 'availability_range'
                'offer_uuid', 'from_owner_id', 'to_owner_id')
        json_flags = ('properties')
        standalone_flags = ('long')

        for flag in args.keys():
            if args[flag] is not None:
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
        listing = output_parser.listing(output)
        details = {}
        for item in listing:
            details.update({ item['Field']: item['Value'] })
        return details

    def offer_create(self, client, node, parse=True, **kwargs):
        flags_default = { 'resource_type': 'dummy_node' }
        for flag in 'start_time', 'end_time', 'lessee', 'name', 'properties':
            flags_default[flag] = None

        flags = self._kwargs_to_flags(self._merge_kwargs(flags_default, kwargs))
        output = self.clients[client].esi('offer create', flags, node.uuid)

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
                (node.uuid, self.client_info[lessee]['project_name']))

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

class ESICLIClient(base.CLIClient):
    def esi(self, action, flags='', params='', fail_ok=False,
            merge_stderr=False):
        return self.openstack('esi %s' % action, '',
                '%s %s' % (flags, params), fail_ok, merge_stderr)
