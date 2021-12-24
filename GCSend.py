#!/bin/env python3

import sys, argparse, serial

def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'port',
        type=str,
        help='port the machine is connected to'
    )
    parser.add_argument(
        'file',
        type=str,
        help='file to be run'
    )
    parser.add_argument(
        '--baud',
        '-b',
        type=int,
        default=115200,
        help='baud rate to use'
    )
    return parser.parse_args()

if __name__ == '__main__':
    args = getArgs()
    print('file: {}'.format(args.file))
    print('port: {}'.format(args.port))
    print('baud: {}'.format(args.baud))
