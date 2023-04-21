#!/usr/bin/env python

import os
import configparser
from abc import ABC, abstractmethod

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

    def get_server(self, name = None):
        if name is None:
            name = self.get_default()
        if name is None:
            return None
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
    def handler(self, args):
        pass

import gerritcli.command
