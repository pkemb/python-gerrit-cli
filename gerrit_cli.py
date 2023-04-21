#!/usr/bin/env python3

from abc import ABC, abstractmethod
import configparser
from http import server
import sys, os
import argparse

class gerrit_server_config:
    __instance = None
    gerrit_rc = os.path.join(os.environ['HOME'], '.gerrit.rc')

    def __init__(self) -> None:
        self.config = configparser.ConfigParser()
        self.config.read(self.gerrit_rc)

    def write(self):
        with open(self.gerrit_rc, 'w') as f:
            self.config.write(f)
        return

    def set_server(self, name, host, username, password):
        self.config[name] = { 'host':host, 'username':username, 'password':password }
        if len(self.config.sections()) == 1:
            self.set_default(name)
        self.write()

    def get_server(self, name):
        if name in self.config:
            return dict(self.config[name])
        else:
            return None

    def get_all_server(self):
        all = {}
        for name in self.config.sections():
            all[name] = self.get_server(name)
        return all

    def remove_server(self, name):
        if name in self.config.sections():
            self.config.remove_section(name)
            if len(self.config.sections()) == 0 or name == self.get_default():
                self.config.remove_option('DEFAULT', 'name')
            self.write()
            return True
        return False

    def set_default(self, name):
        self.config['DEFAULT'] = {'name': name}
        self.write()
        return

    def get_default(self):
        if self.config.has_option('DEFAULT', 'name'):
            return self.config.get('DEFAULT', 'name')
        return None

    @classmethod
    def get_config(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

class sub_command(ABC):
    __instance = None

    command = ""
    help = ""
    cmd_parser = None
    def __init__(self, subparser):
        if self.command == "" or self.help == "":
            raise NotImplementedError
        self.subparser = subparser
        self.cmd_parser = self.subparser.add_parser(self.command, help=self.help)
        self.cmd_parser.set_defaults(handler=self.handler)

    @classmethod
    def init_subcmd(cls, subparser):
        if cls.__instance is None:
            cls.__instance = cls(subparser)
            cls.__instance.init_argument()
        return cls.__instance

    @classmethod
    def get_subcmd(cls):
        if cls.__instance is None:
            print("sub command \"%s\" not init" % cls.command)
            exit(1)
        return cls.__instance

    @abstractmethod
    def init_argument(self):
        pass

    @abstractmethod
    def handler(self, args):
        pass

class server_command(sub_command):
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

def main(argv):
    parser = argparse.ArgumentParser()

    # global option
    parser.add_argument('-s',
            dest="server",
            help='specify gerrit server. If not specified, the default value is used',
            required=False)

    # sub command
    subparser = parser.add_subparsers(help='command usage', dest='command', metavar = "subcmd", required=True)
    # call all child init function for add sub command
    for subclass in sub_command.__subclasses__():
        subclass.init_subcmd(subparser)

    args = parser.parse_args()
    # call command handler
    args.handler(args)
    return

if __name__ == "__main__":
    main(sys.argv)