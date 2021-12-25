#!/bin/env python3

import time, argparse, serial

def getArgs():
    parser = argparse.ArgumentParser(
        prog='GCSend',
        description='A command line GCode sender for GRBL machines'
    )
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
    parser.add_argument(
        '--verbosity',
        '-v',
        type=int,
        default=1,
        help='set verbosity'
    )
    parser.add_argument(
        '--wait-to-exit',
        '-w',
        action='store_true',
        help='wait for user confirmation before closing the port and exiting'
    )
    return parser.parse_args()

def initGRBL(machine):
    machine.write(b'\r\n\r\n')
    time.sleep(2)
    machine.flushInput()

if __name__ == '__main__':
    args = getArgs()

    def debug(level, *msg, **otherArgs):
        if args.verbosity >= level:
            print(*msg, **otherArgs)

    debug(1, 'file: {}'.format(args.file))
    debug(1, 'port: {}'.format(args.port))
    debug(1, 'baud: {}'.format(args.baud))
    debug(2, 'verbosity: {}'.format(args.verbosity))
    debug(2, 'wait-to-exit: {}'.format(args.wait_to_exit))
    debug(1, '')    # Blank line

    with open(args.file, 'r') as file:
        gcodeText = file.read()
    gcodeCommands = str.splitlines(gcodeText)

    with serial.Serial(args.port, args.baud) as machine:
        initGRBL(machine)
        
        for command in gcodeCommands:
            commandToSend = command.strip() # Remove leading and trailing whitespace
            debug(1, 'Send: {}'.format(repr(commandToSend)))
            machine.write(commandToSend.encode('utf-8'))    # Send gcode command
            machine.write(b'\n')    # Send newline to signal end of command

            response = machine.readline().decode('utf-8')[0:-2]    # Get reponse
            debug(1, 'Receive: {}'.format(repr(response)))
            if 'error' in response:
                debug(0, 'GRBL returned error {}'.format(response.split(';')[1]))
                break

        if args.wait_to_exit:
            input('Press enter to close port and exit')
