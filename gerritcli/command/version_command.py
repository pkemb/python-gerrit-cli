#!/usr/bin/python
# -*- coding:utf-8 -*-
import gerritcli

class version_command(gerritcli.maincommand):
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


    def handler(self, args):
        client = gerritcli.gerrit_server.get_client()
        return self.version(client)
