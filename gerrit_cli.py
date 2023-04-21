#!/usr/bin/env python3

from abc import ABC, abstractmethod
import configparser
from http import server
import sys, os
import argparse
import gerritcli

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
    for subcmd in gerritcli.subcommand.__subclasses__():
        subcmd.init_subcmd(subparser)

    args = parser.parse_args()
    # call command handler
    args.handler(args)
    return

if __name__ == "__main__":
    sys.exit(main(sys.argv))
