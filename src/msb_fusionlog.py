import zmq
import logging

from config import init


def sync(connect_to):
    # use connect socket + 1
    sync_with = ':'.join(
        connect_to.split(':')[:-1] + [str(int(connect_to.split(':')[-1]) + 1)]
    )

    logging.debug(f'additional socket to start communication: {sync_with}')

    ctx = zmq.Context.instance()
    s = ctx.socket(zmq.REQ)
    s.connect(sync_with)
    s.send(b'READY')
    s.recv()


def main():

    config = init()

    logging.debug('msb_fusionlog.py starting up')

    bind_to = f'{config["ipc_protocol"]}:///tmp/msb:{config["ipc_port"]}'

    logging.debug(f'trying to bind zmq to {bind_to}')

    ctx = zmq.Context()
    s = ctx.socket(zmq.SUB)
    s.bind(bind_to)
    s.setsockopt(zmq.SUBSCRIBE, b'')

    logging.debug(f'successfully bound to zeroMQ socket as subscriber')

    #sync(bind_to)

    logging.debug(f'entering endless loop')

    while True:
        a = s.recv_pyobj()
        print(f'received {a}')

if __name__ == '__main__':
    main()