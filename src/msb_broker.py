import zmq
import logging
import socket
import json
import sys

try:
    from config import init
except ImportError as e:
    print(f'failed to import init funtion: {e}')
    sys.exit(-1)



def main():

    config = init()

    # where all data comes in
    # subscriber = f'{config["ipc_protocol"]}:///tmp/msb:{config["subscriber_ipc_port"]}'
    # where the incoming data is routed to
    # publisher = f'{config["ipc_protocol"]}:///tmp/msb:{config["publisher_ipc_port"]}'

    # where all data comes in
    subscriber = f'tcp://*:5555'
    # where the incoming data is routed to
    publisher = f'tcp://*:5556'


    logging.debug(f'subscriber: {subscriber}')
    logging.debug(f'publisher: {publisher}')

    ctx = zmq.Context()

    xpub = ctx.socket(zmq.XPUB)
    try:
        xpub.bind(publisher)
    except Exception as e:
        logging.fatal(f'failed to bind to publisher: {e}')
    
    xsub = ctx.socket(zmq.XSUB)
    try:
        xsub.bind(subscriber)
    except Exception as e:
        logging.fatal(f'failed to bin to subscriber: {e}')

    try:
        zmq.proxy(xpub, xsub)
    except Exception as e:
        logging.fatal(f'failed to create proxy: {e}')


if __name__ == "__main__":
    main()