#!/usr/bin/python
# -*- coding:utf-8 -*-

from gerritcli import gerrit_server
import gerritcli

class server_command(gerritcli.maincommand):
    command = "server"
    help = "add/remove/list gerrit server info"

    def __init__(self, subparser):
        self.subcmd_info = {
            "add": {
                "handler": self.add_handler,
                "help": 'add gerrit server'
            },
            "remove": {
                "handler": self.remove_handler,
                "help": 'remove gerrit server'
            },
            "list": {
                "handler": self.list_handler,
                "help": 'list gerrit server'
            },
            "default": {
                "handler": self.default_handler,
                "help": 'set default gerrit server'
            }
        }
        super().__init__(subparser)

    def init_argument(self):
        self.subcmd['add'].add_argument('name', help = 'gerrit server name')
        self.subcmd['add'].add_argument('host', help = 'gerrit server host')
        self.subcmd['add'].add_argument('username', help = 'gerrit login user name')
        self.subcmd['add'].add_argument('password', help = 'user http password')

        self.subcmd['remove'].add_argument('name', help = 'gerrit server name')

        # subcmd list no argument

        self.subcmd['default'].add_argument('name', help = 'gerrit server name')

    def add_handler(self, args):
        gerrit_server.add(args.name, args.host, args.username, args.password)
        return

    def remove_handler(self, args):
        gerrit_server.remove(args.name)
        return

    def list_handler(self, args):
        all          = gerrit_server.get_all()
        default_name = gerrit_server.get_default_name()

        for server in all:
            if server['name'] == default_name:
                server['default'] = 'yes'
            else:
                server['default'] = ''

        gerritcli.utils.show(all, header = ['name', 'username', 'host', 'default'])
        return

    def default_handler(self, args):
        gerrit_server.set_default(args.name)
