import argparse
import json
import sys
import signal
import logging
import socket

from datetime import datetime
from os import path

def signal_handler_exit(sig, frame):
    logging.info('* msb_fusionlog: bye')
    sys.exit(0)

def dump_config_file(config : dict):
    with open(config['dump_config_file'], 'w') as config_file_handle:
        config_file_handle.writelines(
            json.dumps(
                config,
                indent=4
            )
        )

def read_parse_config_file(config : dict) -> dict:

    try:
        config_file_handler = open(config['config_file'], 'r')
    except Exception as e:
        print(f'failed to open config file: {e}')
        sys.exit(-1)

    config_file_args = json.load(config_file_handler)

    for key, value in config_file_config.items():
        if key == 'config_file':
            continue

        if key in config:

            print(f'parsing {key} : {value}')
            config[key] = value
        else:
            print(f'key not found: {key} omitting')

    return config   

def parse_arguments() -> dict:
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument(
        '--verbose',
        action='store_true',
        help='for debugging purposes'
    )

    arg_parser.add_argument(
        '--print',
        action='store_true',
        help='prints the incoming data',
        default=False
    )

    arg_parser.add_argument(
        '--logfile',
        help='path to logfile',
        type=str,
        default=f'/tmp/msb_fusionlog_{datetime.now().astimezone().strftime("%Y-%m-%dT%H-%M-%S%z")}.log',
    )

    arg_parser.add_argument(
        '--imu-output-div',
        help='sensor output data rate. calculated by 1100/(1+output_data_div). default 21 (100 Hz)',
        default=21,
        type=int
    )

    arg_parser.add_argument(
        '--config-file',
        help='configuration file: overwrite all commandline options!',
        default='',
        type=str,
    )

    arg_parser.add_argument(
        '--dump-config-file',
        help='dumps the default config values into a file',
        default='',
    )

    arg_parser.add_argument(
        '--udp-stream', 
        help='flag to enable data streaming via a UDP socket',
        default=False,
        action='store_true'
    )

    arg_parser.add_argument(
        '--udp-address', 
        help='host to stream sensor data to',
        default='192.168.4.1',
        type=str
    )

    arg_parser.add_argument(
        '--udp-port',
        help='port to stream darta to',
        default=9870,
        type=int
    )

    arg_parser.add_argument(
        '--ipc-port',
        help='IPC port used by zeroMQ',
        default=5555,
        type=int
    )

    arg_parser.add_argument(
        '--ipc-protocol',
        help='the protocol used for IPC with zeroMQ',
        default='ipc',
        type=str,
    )

    arg_parser.add_argument(
        '--profile',
        help='profile flag',
        default=False,
        action='store_true'
    )

    return arg_parser.parse_args().__dict__

def init() -> dict:

    signal.signal(signal.SIGINT, signal_handler_exit)

    config = parse_arguments()

    logging.basicConfig(
        filename=config['logfile'],
        level=config['verbose'] if logging.DEBUG else logging.WARNING,
        format='%(levelname)s: %(asctime)s %(message)s',
        datefmt='%Y%m%dT%H%M%S%z',
    )

    logging.debug('msb_fusionlog.py parsing of configuration done')

    if config['config_file']:
        logging.debug('parsing config file')
        config = read_parse_config_file(config)
        logging.debug(f'updated config file: {config}')

    if config['dump_config_file']:
        logging.debug(f'dumping config file to {config["dump_config_file"]}')
        dump_config_file(config)
        
    return config
    
