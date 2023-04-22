#!/usr/bin/python
# -*- coding:utf-8 -*-
from gerritcli import subcommand

class version_command(subcommand):
    """
    打印gerrit服务器版本
    """
    command = "version"
    help = "show gerrit server version"

    def version(self, client):
        """
        打印gerrit服务器版本
        :return:
        """
        print(client.version)
        return True


    def handler(self, args, client):
        return self.version(client)
