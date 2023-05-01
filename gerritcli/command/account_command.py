#!/usr/bin/python
# -*- coding:utf-8 -*-

import gerrit.utils.exceptions
from copy import deepcopy
import gerritcli.utils
import gerritcli
import sys

class account_command(gerritcli.maincommand):
    """
    ...
    """
    command = "account"
    help = "account command help"
    accounts_cache = dict() # id cache / username cache / email cache
    cache_by_id = dict()
    cache_by_username = dict()
    cache_by_email = dict()
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

    def __init__(self, subparser):
        self.subcmd_info = {
            "search": {
                "handler": self.get_search_handler,
                "help": 'Queries accounts visible to the caller.'
            },
            "get": {
                "handler": self.get_search_handler,
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
            cmd.add_argument('--output', '-o',
                                dest='output_file',
                                help='output to file, not stdout',
                                default=None, required=False)
            cmd.add_argument('--header',
                                dest='header',
                                help='output header, when output format is csv / table',
                                default=None, required=False)
            cmd.add_argument('--format',
                                dest='format',
                                help='output format, json / csv / table',
                                default='table', required=False)

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
            account_info = gerrit_account.to_dict()
            account_info['status'] = gerrit_account.get_status()
            account_info['active'] = gerrit_account.get_active()
            account_info['id']     = account_info['_account_id']
            account_info['registered_on'] = \
                    gerritcli.utils.utc2local(account_info['registered_on'])

            del account_info['_account_id']
            del account_info['secondary_emails']

        except gerrit.utils.exceptions.NotFoundError:
            print("%s not found" % userid, file=sys.stderr)
            is_found = False
            account_info = deepcopy(self.empty_account)
        if "email" not in account_info:
            account_info['email'] = self.empty_account['email']
        if "tags" not in account_info:
            account_info['tags'] = self.empty_account['tags']
        if "display_name" not in account_info:
            account_info['display_name'] = self.empty_account['display_name']

        if cache and is_found:
            self.cache_by_id[account_info['id']] = account_info
            self.cache_by_username[account_info['username']] = account_info
            if account_info['email'] != self.empty_account['email']:
                self.cache_by_email[account_info['email']] = account_info
        return account_info

    def search_account(self, query):
        """
        Documentation/user-search-accounts.html#_search_operators
        """
        client = gerritcli.gerrit_server.get_client()
        accounts_info = client.accounts.search(query)
        accounts = list()
        for info in accounts_info:
            account_id = info['_account_id']
            accounts.append(self.get_account(account_id))
        return accounts

    def get_search_handler(self, args):
        header = None
        if args.header:
            header = args.header.split(',')
            gerritcli.utils.check_header(header, self.empty_account.keys())
        gerritcli.utils.check_format(args.format)

        if args.output_file:
            f = open(args.output_file, 'w')
        else:
            f = sys.stdout

        if args.subcmd == 'search':
            accounts = self.search_account(args.query)
        elif args.subcmd == 'get':
            accounts = list()
            for userid in args.userids:
                accounts.append(self.get_account(userid, cache=True))
        else:
            print("unknow subcmd %s" % args.subcmd, file=sys.stderr)
            sys.exit(1)

        gerritcli.utils.show(accounts, header = header, format=args.format, file = f)
        if args.output_file:
            f.close()
        return

    def create_handler(self, args):
        print("TODO")
