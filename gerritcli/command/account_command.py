#!/usr/bin/python
# -*- coding:utf-8 -*-

import gerrit.utils.exceptions
from copy import deepcopy
import gerritcli
import sys
from gerritcli.utils import utc2local

empty_account = {
    "id": None,
    "name": "",
    "email": "",
    "username": "",
    "status": "",
    "active": "",
    "tags": "",
    "registered_on": "",
    "display_name": ""
}

class gerrit_account_info(gerritcli.utils.gerrit_info):
    """
    Documentation/rest-api-accounts.html#account-info
    """

    def __init__(self, account, **kwargs):
        self.content['id']            = account.get('_account_id', empty_account['id'])
        if account['registered_on'] == empty_account['registered_on']:
            self.content['registered_on'] = account['registered_on']
        else:
            self.content['registered_on'] = utc2local(account['registered_on'])
        self.content['username']      = account['username']
        self.content['name']          = account['name']

        self.content['email']        = account.get('email',        empty_account['email'])
        self.content['tags']         = account.get('tags',         empty_account['tags'])
        self.content['display_name'] = account.get('display_name', empty_account['display_name'])
        self.content['status']       = kwargs.get('status', empty_account['status'])
        self.content['active']       = kwargs.get('active', empty_account['active'])
        super().__init__(**kwargs)

class account_command(gerritcli.maincommand):
    """
    ...
    """
    command = "account"
    help = "account command help"
    cache_by_id = dict()
    cache_by_username = dict()
    cache_by_email = dict()
    account_header = 'id,username,email,status,active'

    def __init__(self, subparser):
        self.subcmd_info = {
            "search": {
                "handler": self.search_handler,
                "help": 'Queries accounts visible to the caller.'
            },
            "get": {
                "handler": self.get_handler,
                "help": 'get account'
            },
            "create": {
                "handler": self.create_handler,
                "help": 'create account'
            }
        }
        super().__init__(subparser)

    def init_argument(self):
        self.subcmd['search'].add_argument('query', help='query string')
        self.subcmd['get'].add_argument('userids',
                                      help='account id or name',
                                      nargs='+',
                                      default=['self'])

        for cmd in [self.subcmd['search'], self.subcmd['get']]:
            gerritcli.utils.add_commmon_argument(cmd, 'output')
            gerritcli.utils.add_commmon_argument(cmd, 'header', default = self.account_header)
            gerritcli.utils.add_commmon_argument(cmd, 'format')

        gerritcli.utils.add_commmon_argument(self.subcmd['search'], 'limit')
        gerritcli.utils.add_commmon_argument(self.subcmd['search'], 'skip')

        # subcmd create no argument
        return

    def get_account(self, userid, cache = True):
        """
        Documentation/rest-api-accounts.html#account-info
        """
        # search local cache
        if cache:
            if userid in self.cache_by_id:
                return self.cache_by_id[userid]
            if userid in self.cache_by_username:
                return self.cache_by_username[userid]
            if userid in self.cache_by_email:
                return self.cache_by_email[userid]

        is_found = True
        client = gerritcli.gerrit_server.get_client()
        try:
            gerrit_account = client.accounts.get(userid, detailed=True)
            account = gerrit_account.to_dict()
            status = gerrit_account.get_status()
            active = gerrit_account.get_active()

            account_info = gerrit_account_info(account, status = status, active = active)

        except gerrit.utils.exceptions.NotFoundError:
            is_found = False
            account_info = gerrit_account_info(empty_account,
                                                id = userid,
                                                name = userid,
                                                username = userid,
                                                status = 'not found')

        if cache and is_found:
            self.cache_by_id[account_info.id] = account_info
            self.cache_by_username[account_info.username] = account_info
            if account_info.email != empty_account['email']:
                self.cache_by_email[account_info.email] = account_info
        return account_info

    def search_account(self, query, **kwargs):
        """
        Documentation/user-search-accounts.html#_search_operators
        """
        try:
            client = gerritcli.gerrit_server.get_client()
            accounts_info = client.accounts.search(query, **kwargs)
            accounts = list()
            for info in accounts_info:
                account_id = info['_account_id']
                accounts.append(self.get_account(account_id))
            return accounts
        except gerrit.utils.exceptions.ValidationError:
            print("query \"%s\" is invalid!!!" % query)
            sys.exit(1)

    def get_handler(self, args):
        header = args.header.split(',')
        accounts = list()
        for userid in args.userids:
            accounts.append(self.get_account(userid, cache=True))

        gerritcli.utils.show_info(
            accounts,
            header   = header,
            filename = args.output_file,
            format   = args.format)
        return

    def search_handler(self, args):
        header = args.header.split(',')
        accounts = self.search_account(
            args.query,
            limit = args.limit,
            skip = args.limit
        )

        gerritcli.utils.show_info(
            accounts,
            header   = header,
            filename = args.output_file,
            format   = args.format)

    def create_handler(self, args):
        print("TODO")
