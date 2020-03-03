#!/usr/bin/env python3
import logging
from argparse import ArgumentParser, FileType, ArgumentTypeError
from utils.util import TARGET_SERVER, ErgoClient, setup_logger
import threading
import queue
import time
from pprint import pprint

# кол-во потоков
THREAD_COUNT = 2

def parse_cli():
    parser = ArgumentParser()
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
    group.add_argument('-s', '--server',
        help='Address of RPC server in format SERVER:PORT')
    group.add_argument('--mainnet', action='store_true',
                       help='Using main net, default server localhost:9053')
    group.add_argument('--testnet', action='store_true',
                       help='Using test net, default server localhost:9052')
    opts = parser.parse_args()
    return opts

def transaction_gen(address, amount, num=1, prefix=None):
    prefix_ = f"{prefix}" if prefix else ''
    logging.debug(f'transaction gen {prefix_}{num} amount: {amount}')
    res = {
        "requests": [],
        "fee": 1000000,
        "inputsRaw": []
    }
    for i in range(num):
        res['requests'].append({
            "address": address,
            "amount": amount,
            "name": f"TST{i}",
            "description": f"Test token {prefix_}{i}",
            "decimals": 8
        })
    return res

def worker(api, qtasks):
    while True:
        rnum, req_data = qtasks.get()
        logging.debug(f'req for /generate {req_data}')
        code, tx_json = api.request('/wallet/transaction/generate', data=req_data)
        logging.debug(f'result: [{code}] {tx_json}')
        if code != 200:
            logging.error(tx_json)
            exit(1)

        # If no errors POST to /transactions
        url_ = '/transactions'
        # logging.debug('send transaction to %s' % url_)
        code, txid = api.request(url_, data=tx_json)
        if code != 200:
            logging.error(txid)
            exit(1)

        logging.debug(f'txId: {txid}')
        qtasks.task_done()

def main():
    opts = parse_cli()
    setup_logger(not opts.quiet)

    target_ = 'mainnet'
    if opts.testnet:
        target_ = 'testnet'

    address_to = 'Bf1X9JgQTUtgntaer91B24n6kP8L2kqEiQqNf1z97BKo9UbnW3WRP9VXu8BXd1LsYCiYbHJEdWKxkF5YNx5n7m31wsDjbEuB3B13ZMDVBWkepGmWfGa71otpFViHDCuvbw1uNicAQnfuWfnj8fbCa4'
    amount = 100000
    num_trans=2
    num_reqs=5

    server_ = opts.server or TARGET_SERVER[target_]
    api = ErgoClient(server_, opts.api_key)
    tasks = queue.Queue()
    for i in range(THREAD_COUNT):
        w = threading.Thread(
            target=worker,
            args=(api, tasks),
            name=f'worker-{i}'
        )
        w.setDaemon(True)
        w.start()

    for rnum in range(num_reqs):
        tasks.put((rnum, transaction_gen(address_to, amount, num=num_trans, prefix=f'req-{rnum}')))

    # http://stackoverflow.com/questions/11815947/cannot-kill-python-script-with-ctrl-c
    try:
        while threading.active_count() > 1:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Adieu")
    else:
        print('All requests done')

if __name__ == '__main__':
    main()
