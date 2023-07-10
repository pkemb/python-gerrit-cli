#!/usr/bin/env python

import os
import sys
import configparser
from abc import ABC, abstractmethod
from gerrit import GerritClient
import gerrit
import requests
import gerritcli.utils

__version__ = "1.0.6"
version_string = f'gerritcli {__version__}, Written by PKEMB, Kai Peng'

class gerrit_server:
    __instance = None
    gerrit_rc = os.path.join(os.environ['HOME'], '.gerrit.rc')
    gerrit_client = None

    def __init__(self) -> None:
        self.config = configparser.ConfigParser()
        self.config.read(self.gerrit_rc)

    def write(self):
        with open(self.gerrit_rc, 'w') as f:
            self.config.write(f)
        return

    @staticmethod
    def login(name = None):
        """
        登录服务器，返回client
        """
        instance = gerrit_server.get_instance()
        server = instance.get(name)
        if server is None:
            return None

        client = GerritClient(
                    base_url=server['host'],
                    username=server['username'],
                    password=server['password'])
        try:
            version = client.version
        except requests.exceptions.MissingSchema as e:
            print("invalid host %s.\n%s" % (instance.get_host(name), str(e)))
            sys.exit(1)
        except gerrit.utils.exceptions.UnauthorizedError as e:
            print("login fail, please check username and http password!!!")
            sys.exit(1)

        instance.gerrit_client = client
        return client

    @staticmethod
    def get_client():
        instance = gerrit_server.get_instance()
        if instance.gerrit_client is None:
            print("no login", file=sys.stderr)
            sys.exit(1)
        return instance.gerrit_client

    @staticmethod
    def get(name = None):
        """
        获取服务器的详细信息

        {
            "host": xxxx,
            "username": xxxx,
            "password": xxxx
        }
        """
        instance = gerrit_server.get_instance()
        if name is None:
            name = instance.get_default_name()
        if name is None:
            return None
        if name == 'DEFAULT':
            return None
        if name in instance.config:
            return dict(instance.config[name])
        else:
            return None

    @staticmethod
    def get_all():
        """
        获取所有服务器的详细信息
        """
        instance = gerrit_server.get_instance()
        all = []
        for name in instance.config.sections():
            server = dict(instance.config[name])
            server['name'] = name
            all.append(server)
        return all

    @staticmethod
    def get_host(name = None):
        instance = gerrit_server.get_instance()
        server = instance.get(name)
        if server:
            return server['host']
        else:
            return None

    @staticmethod
    def get_username(name = None):
        instance = gerrit_server.get_instance()
        server = instance.get(name)
        if server:
            return server['username']
        else:
            return None

    @staticmethod
    def add(name, host, username, password, overwrite = False):
        """
        新增一个服务器
        """
        instance = gerrit_server.get_instance()
        if overwrite == False and name in instance.config:
            print("%s exits" % name)
            return False
        if name == "DEFAULT":
            print("invalid name: %s" % name)
            return False
        instance.config[name] = { 'host':host, 'username':username, 'password':password }
        if len(instance.config.sections()) == 1:
            instance.set_default(name)
        instance.write()

    @staticmethod
    def remove(name):
        """
        移除一个服务器
        """
        instance = gerrit_server.get_instance()
        if name in instance.config.sections():
            instance.config.remove_section(name)
            if len(instance.config.sections()) == 0 or name == instance.get_default_name():
                instance.config.remove_option('DEFAULT', 'name')
            instance.write()
            return True
        return False

    @staticmethod
    def set_default(name):
        """
        设置默认的服务器
        """
        instance = gerrit_server.get_instance()
        if name == 'DEFAULT':
            print("invalid name: %s" % name)
            return False

        if name in instance.config.sections():
            instance.config['DEFAULT'] = {'name': name}
            instance.write()
            return True
        else:
            print("no such server %s" % name)
            return False

    @staticmethod
    def get_default_name():
        """
        获取默认服务器的名字
        """
        instance = gerrit_server.get_instance()
        if instance.config.has_option('DEFAULT', 'name'):
            return instance.config.get('DEFAULT', 'name')
        return None

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

class maincommand(ABC):
    __instance = None

    command = ""
    help = ""
    maincmd = None
    subcmd_info = None
    subcmd = dict()
    subcmd_subparser = None

    def __init__(self, subparser):
        if self.command == "" or self.help == "":
            raise NotImplementedError
        self.maincmd_subparser = subparser
        self.maincmd = self.maincmd_subparser.add_parser(self.command, help=self.help)
        self.maincmd.set_defaults(handler=self.handler)

        if self.subcmd_info:
            self.subcmd_subparser = self.maincmd.add_subparsers(
                                        help=self.help,
                                        dest='subcmd',
                                        required=True)
            for cmd in self.subcmd_info:
                helpstr = self.subcmd_info[cmd]['help']
                handler = self.subcmd_info[cmd]['handler']
                self.subcmd[cmd] = self.subcmd_subparser.add_parser(cmd, help=helpstr)
                self.subcmd[cmd].set_defaults(handler=handler)


    @classmethod
    def init(cls, subparser):
        if cls.__instance is None:
            cls.__instance = cls(subparser)
            cls.__instance.init_argument()
        return cls.__instance

    @classmethod
    def get(cls):
        if cls.__instance is None:
            print("command \"%s\" not init" % cls.command)
            exit(1)
        return cls.__instance

    def init_argument(self):
        return

    def handler(self, args):
        return

import gerritcli.command
