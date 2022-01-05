import zmq
import logging
import socket
import json
import sys
import pickle
import logging
from logging.handlers import RotatingFileHandler
from os import path
from os import makedirs
from datetime import datetime
# from logging.handlers import RotatingFileHandler

try:
    from fusionlog_config import init
except Exception as e:
    print(f'failed to load init from config: {e}')
    sys.exit(-1)


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

    # create new logger instance
    data_dir = path.join(config['base_data_dir'], config['custom_data_dir'] )
    data_file_name = f'{socket.gethostname()}_{datetime.utcnow().isoformat()}.log'
    data_file_path = path.join(data_dir, data_file_name)

    if not path.exists(data_file_path):
        try:
            makedirs(data_dir, exist_ok=True)
        except Exception as e:
            logging.fatal(f'failed to create log file dir: {data_dir}: {e}')
            sys.exit(-1)
 
    bytes_per_file = int(config['data_file_size'] * 1000 * 1000)
    n_files = config['max_number_data_files']

    data_file_handler = RotatingFileHandler(
        data_file_path,
        maxBytes=bytes_per_file,
        backupCount=n_files,
        encoding="utf-8",
    )

    data_file_handler.setLevel("INFO")
    data_file_handler.setFormatter(logging.Formatter("%(message)s"))

    data_file_logger = logging.getLogger('log_file_logger')
    data_file_logger.setLevel("INFO")
    data_file_logger.addHandler(data_file_handler)

    logging.debug(f'saving data to {data_file_path} with a file size of {bytes_per_file} and a maximum number of {n_files}')

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
        try:
            [topic, data] = zmq_socket.recv_multipart()
        except Exception as e:
            logging.error(f'failed to receive message: {e}')
            continue

        topic = topic.decode('utf-8')

        try:
            data = pickle.loads(data)
        except Exception as e:
            logging.error(f'failed to load pickle message, skipping: {e}')
            continue

        # log to data file
        data_file_logger.info({topic:data})

        if config['print']: 
            print(f'{topic}: {data}')
        
        if config['udp_address'] and udp_socket:
            try:
                udp_socket.sendto(
                    json.dumps({topic : data}).encode('utf-8'), 
                    (config['udp_address'], config['udp_port'])
                )
            except Exception as e:
                logging.error(f'failed to send data to {config["udp_address"]}:{config["udp_port"]}: {e}')
                continue
        
        #implement ring buffer logging here

if __name__ == '__main__':
    main()
