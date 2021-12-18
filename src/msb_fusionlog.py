import zmq
import logging
import socket
import json
import sys

from config import init

def main():

    config = init()

    logging.debug('msb_fusionlog.py starting up')

    bind_to = f'{config["ipc_protocol"]}:///tmp/msb:{config["ipc_port"]}'
    bind_to_sender = f'{config["ipc_protocol"]}:///tmp/msb_fusion:{config["ipc_port"]}'

    logging.debug(f'trying to bind zmq to {bind_to}')

    ctx = zmq.Context()
    zmq_socket = ctx.socket(zmq.SUB)
    zmq_socket_sender = ctx.socket(zmq.PUB)

    try:
        zmq_socket.bind(bind_to)
    except Exception as e:
        logging.fatal(f'failed to bind to zeromq socket: {e}')
        sys.exit(-1)
    
    zmq_socket.setsockopt(zmq.SUBSCRIBE, b'')
    
    logging.debug('successfully bound to zeroMQ receiver socket as subscriber')

    logging.debug(f'trying to bind to {bind_to_sender}')
    try:
        zmq_socket_sender.bind(bind_to_sender)
    except Exception as e:
        logging.fatal(f'failed to bind to zeromq sender socket: {e}')
        sys.exit(-1)

    logging.debug(f'successfully bound to zeroMQ sender socket as publisher')

    # open socket
    try:
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except:
        logging.warning('failed to open udp socket, streaming not available')
        udp_socket = None

    logging.debug(f'entering endless loop')

    while True:

        recv = zmq_socket.recv_pyobj()

        zmq_socket_sender.send_pyobj(recv)

        if config['print']: 
            print(f'{recv}')
        
        if config['udp_stream'] and udp_socket:
            udp_socket.sendto(
                json.dumps(recv).encode(), 
                (config['udp_address'], config['udp_port'])
            )

if __name__ == '__main__':
    main()
