#!/usr/bin/python
# -*- coding:utf-8 -*-

from gerritcli import subcommand
import gerrit.utils.exceptions
from copy import deepcopy
import gerritcli.utils
import sys

class account_command(subcommand):
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
        "registered_on": ""
    }

    def init_argument(self):
        self.subcmd = self.cmd_parser.add_subparsers(
                                help='',
                                dest='change_command',
                                required=True)

        self.subcmd_search = self.subcmd.add_parser('search', help = 'Queries accounts visible to the caller.')
        self.subcmd_search.set_defaults(handler=self.get_search)
        self.subcmd_search.add_argument('query',
                                         help='query string')
        self.subcmd_get = self.subcmd.add_parser('get', help = 'get account')
        self.subcmd_get.set_defaults(handler=self.get_search)
        self.subcmd_get.add_argument('userids',
                                      help='account id or name',
                                      nargs='+',
                                      default=['self'])

        for parser in [self.subcmd_search, self.subcmd_get]:
            parser.add_argument('--output', '-o',
                                dest='output_file',
                                help='output to file, not stdout',
                                default=None, required=False)
            parser.add_argument('--header',
                                dest='header',
                                help='output header, when output format is csv / table',
                                default=None, required=False)
            parser.add_argument('--format',
                                dest='format',
                                help='output format, json / csv / table',
                                default='table', required=False)

        self.subcmd_create = self.subcmd.add_parser('create', help = 'create account')
        self.subcmd_create.set_defaults(handler=self.create)
        return

    def handler(self, args, client):
        pass

    def get_account(self, client, userid, cache = True):
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

        if cache and is_found:
            self.cache_by_id[account_info['id']] = account_info
            self.cache_by_username[account_info['username']] = account_info
            if account_info['email'] != self.empty_account['email']:
                self.cache_by_email[account_info['email']] = account_info
        return account_info

    def search_account(self, client, query):
        """
        Documentation/user-search-accounts.html#_search_operators
        """
        accounts_info = client.accounts.search(query)
        accounts = list()
        for info in accounts_info:
            account_id = info['_account_id']
            accounts.append(self.get_account(client, account_id))
        return accounts

    def get_search(self, args, client):
        header = None
        if args.header:
            header = args.header.split(',')
            gerritcli.utils.check_header(header, self.empty_account.keys())
        gerritcli.utils.check_format(args.format)

        if args.output_file:
            f = open(args.output_file, 'w')
        else:
            f = sys.stdout

        if args.change_command == 'search':
            accounts = self.search_account(client, args.query)
        elif args.change_command == 'get':
            accounts = list()
            for userid in args.userids:
                accounts.append(self.get_account(client, userid, cache=True))
        else:
            print("unknow subcmd %s" % change_command, file=sys.stderr)
            sys.exit(1)

        gerritcli.utils.show(accounts, header = header, format=args.format, file = f)
        if args.output_file:
            f.close()
        return

    def create(self, args, client):
        print("TODO")
