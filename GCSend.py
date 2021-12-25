#!/bin/env python3

import time, argparse, signal, serial

def getArgs():
    parser = argparse.ArgumentParser(
        prog='GCSend',
        description='A command line GCode sender for GRBL machines',
        epilog='At any time you can press Ctrl + C to send an E-Stop signal to the machine.'
    )
    parser.add_argument(
        'port',
        type=str,
        help='port the machine is connected to'
    )
    parser.add_argument(
        '--file',
        '-f',
        type=str,
        default='stdin',
        help='file to be run (default stdin)'
    )
    parser.add_argument(
        '--baud',
        '-b',
        type=int,
        default=115200,
        help='baud rate to use (default 115200)'
    )
    parser.add_argument(
        '--verbosity',
        '-v',
        type=int,
        default=1,
        help='set verbosity'
    )
    parser.add_argument(
        '--quit-at-end',
        '-q',
        action='store_true',
        help='close the port and quit without user confirmation'
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
    debug(2, 'quit-at-end: {}'.format(args.quit_at_end))
    debug(1, '')    # Blank line
    debug(1, 'Press Ctrl+C at any time to send E-Stop.')
    debug(1, '')    # Blank line

    if args.file != 'stdin':
        with open(args.file, 'r') as gcodeFile:
            gcodeText = gcodeFile.read()
        gcodeCommands = str.splitlines(gcodeText)
    else:
        debug(1, 'Enter "\\q" or "\\quit" to quit.')

    def send(command):
        debug(1, 'Send: {}'.format(repr(command)))
        machine.write(command.encode('utf-8'))    # Send gcode command
        machine.write(b'\n')    # Send newline to signal end of command

    def recv():
        response = machine.readline().decode('utf-8')[0:-2]    # Get reponse
        debug(1, 'Receive: {}'.format(repr(response)))
        return response

    def eStop(currentSignal, frame):
        debug(0, '\n+=+=+=+=+=+ Transmitting E-Stop +=+=+=+=+=+')
        send('\x18')
        exit()

    signal.signal(signal.SIGINT, eStop)    

    with serial.Serial(args.port, args.baud) as machine:
        initGRBL(machine)
        
        ctr = 0
        while True:
            if args.file == 'stdin':
                command = input('Enter command to send: ')
                if command in ('\\quit', '\\q'):
                    debug(1, 'Quitting.')
                    break

            else:
                try:
                    command = gcodeCommands[ctr]
                    ctr += 1
                except IndexError:
                    debug(1, 'End of file, quitting.')
                    break
                
            send(command.strip()) # str.strip() to remove leading and trailing whitespace
            response = recv()

            if 'error' in response:
                debug(0, 'GRBL returned error {}, quitting.'.format(response.split(';')[1]))
                break


        if not args.quit_at_end:
            input('Press enter to close port and exit.')
