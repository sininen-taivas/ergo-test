#!/usr/bin/env python3
import logging
from argparse import ArgumentParser, FileType, ArgumentTypeError
from utils.util import TARGET_SERVER, ErgoClient, setup_logger


def parse_cli():
    parser = ArgumentParser()
    parser.add_argument(
        '-s', '--server',
        help='Address of RPC server in format SERVER:PORT'
    )
    parser.add_argument(
        '-q', '--quiet', action='store_true', default=False,
        help='Do not show debug output'
    )
    parser.add_argument(
        '--api-key',
        required=True,
        help='API key to pass RPC node authentication',
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--mainnet', action='store_true',
                       help='Using main net, default server localhost:9053')
    group.add_argument('--testnet', action='store_true',
                       help='Using test net, default server localhost:9052')

    opts = parser.parse_args()
    return opts

def main():
    opts = parse_cli()
    setup_logger(not opts.quiet)

    target_ = 'mainnet'
    if opts.testnet:
        target_ = 'testnet'

    server_ = opts.server or TARGET_SERVER[target_]
    api = ErgoClient(server_, opts.api_key)


if __name__ == '__main__':
    main()
