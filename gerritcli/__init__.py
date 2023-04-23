#!/usr/bin/env python

import os
import configparser
from abc import ABC, abstractmethod
from gerrit import GerritClient

class gerrit_server:
    __instance = None
    gerrit_rc = os.path.join(os.environ['HOME'], '.gerrit.rc')
    client = dict()

    def __init__(self) -> None:
        self.config = configparser.ConfigParser()
        self.config.read(self.gerrit_rc)

    def write(self):
        with open(self.gerrit_rc, 'w') as f:
            self.config.write(f)
        return

    @staticmethod
    def client(name = None):
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
        return client

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
        all = {}
        for name in instance.config.sections():
            all[name] = dict(instance.config[name])
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

class subcommand(ABC):
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

    def init_argument(self):
        return

    @abstractmethod
    def handler(self, args, client):
        pass

import gerritcli.command
