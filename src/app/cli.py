#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import argparse

COMMANDS = {
    'md2mmd': 'app.conversion.commands.md2mmd',
}


def main():
    parser = argparse.ArgumentParser(
        prog='vscodiumbench',
        description='Outillage VSCode/VSCodium — scripts, conversion diagrammes',
    )
    parser.add_argument('command', choices=list(COMMANDS), help='Commande à exécuter')
    parser.add_argument('args', nargs=argparse.REMAINDER, help='Arguments de la commande')

    args = parser.parse_args()

    import importlib
    mod = importlib.import_module(COMMANDS[args.command])
    sys.argv = [args.command] + args.args
    sys.exit(mod.main())


if __name__ == '__main__':
    main()
