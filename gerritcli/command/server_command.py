#!/usr/bin/python
# -*- coding:utf-8 -*-

from gerritcli import subcommand
from gerritcli import gerrit_server_config
# import gerritcli

class server_command(subcommand):
    command = "server"
    help = "add/remove/list gerrit server info"
    config = gerrit_server_config.get_config()

    def init_argument(self):
        self.server_subcmd = self.cmd_parser.add_subparsers(
                                help='add/remove/list gerrit server info',
                                dest='server_command',
                                required=True)

        self.server_add = self.server_subcmd.add_parser('add', help = 'add gerrit server')
        self.server_add.add_argument('name', help = 'gerrit server name')
        self.server_add.add_argument('host', help = 'gerrit server host')
        self.server_add.add_argument('username', help = 'gerrit login user name')
        self.server_add.add_argument('password', help = 'user http password')
        self.server_add.set_defaults(server_func=self.add)

        self.server_remove = self.server_subcmd.add_parser('remove', help = 'remove gerrit server')
        self.server_remove.add_argument('name', help = 'gerrit server name')
        self.server_remove.set_defaults(server_func=self.remove)

        self.server_list = self.server_subcmd.add_parser('list', help = 'list gerrit server')
        self.server_list.set_defaults(server_func=self.list)

        self.server_default = self.server_subcmd.add_parser('default', help = 'set default gerrit server')
        self.server_default.add_argument('name', help = 'gerrit server name')
        self.server_default.set_defaults(server_func=self.default)

    def handler(self, args):
        args.server_func(args)
        return

    def add(self, args):
        self.config.set_server(args.name, args.host, args.username, args.password)
        return

    def remove(self, args):
        self.config.remove_server(args.name)
        return

    def list(self, args):
        all = self.config.get_all_server()
        default = self.config.get_default()
        format = "%s %-20s %-20s %-10s"
        print(format % (' ', 'name', 'host', 'username'))
        for name in all:
            if name == default:
                prefix = '*'
            else:
                prefix = ' '
            print(format % (prefix, name, all[name]['host'], all[name]['username']))
        return

    def default(self, args):
        self.config.set_default(args.name)
