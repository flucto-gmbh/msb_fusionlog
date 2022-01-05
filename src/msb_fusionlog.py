import zmq
import logging
import socket
import json
import sys
import pickle

from fusionlog_config import init

def main():

    config = init()

    logging.debug('msb_fusionlog.py starting up')

    connect_to = f'{config["ipc_protocol"]}:{config["ipc_port"]}'

    logging.debug(f'trying to bind zmq to {connect_to}')

    ctx = zmq.Context()
    zmq_socket = ctx.socket(zmq.SUB)

    try:
        zmq_socket.connect(connect_to)
    except Exception as e:
        logging.fatal(f'failed to bind to zeromq socket: {e}')
        sys.exit(-1)

    # let fusionlog subscribe to all available data
    zmq_socket.setsockopt(zmq.SUBSCRIBE, b'')
    
    logging.debug('successfully bound to zeroMQ receiver socket as subscriber')

    # open socket
    try:
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except:
        logging.warning('failed to open udp socket, streaming not available')
        config['udp_address'] = None

    logging.debug(f'successfully opened udp socket. Sendig to {config["udp_address"]}:{config["udp_port"]}')

    logging.debug(f'entering endless loop')

    while True:

        # recv = zmq_socket.recv_pyobj()
        # [topic, data] = socket.recv_multipart()
        [topic, data] = zmq_socket.recv_multipart()
        topic = topic.decode('utf-8')
        data = pickle.loads(data)

        if config['print']: 
            print(f'{topic}: {data}')
        
        if config['udp_address'] and udp_socket:
            udp_socket.sendto(
                json.dumps({topic : data}).encode(), 
                (config['udp_address'], config['udp_port'])
            )
        
        #implement ring buffer logging here

if __name__ == '__main__':
    main()
