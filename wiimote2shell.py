#!/usr/bin/env python3.4

import socket
import shlex
import subprocess
import argparse

def readconfig(path):
    mapping = {}
    try:
        conf = open(path, 'r').readlines()
        for line in conf:
            if line != '\n':
                keys = shlex.split(line)
                mapping[keys[0]] = keys[1:]
    except Exception as e:
        print('Unable to parse config', path) # logger nehmen
        exit()
    return mapping

def do(action):
    if action == ['EXIT']:
        exit()
    elif action:
        # use Popen to run command in background
        subprocess.Popen(action)
    else:
        # ignore empty action
        pass

def check_buttons(buttons, mapping):
    """
    in: [pressed button]
    tests if each button is bound to some action
    and executes it

    TODO: combo actions?
    """
    for button in buttons:
        if button in mapping.keys():
            print(button, mapping[button])
            do(mapping[button])

def main():
    parser = argparse.ArgumentParser(description='wiimote2shell remote control program')
    parser.add_argument('--device', '-d', help='wiimote mac address', required=True)
    parser.add_argument('--config', '-c', help='config file path', required=True)
    args = parser.parse_args()

    mac = args.device

    # get {keyid => shellcmd list}
    mapping = readconfig(args.config)

    # http://wiibrew.org/wiki/Wiimote#Buttons
    bitmap = [[0x01, 'LEFT' , 'TWO'],
              [0x02, 'RIGHT', 'ONE'],
              [0x04, 'DOWN',  'B'],
              [0x08, 'UP',    'A'],
              [0x10, 'PLUS',  'MINUS'],
              [0x80, None,    'HOME']]

    print('Press 1 + 2 on your Wiimote for discover mode!')
    try:
        # TODO: set or display timeout for connection attempt
        # sockets will magically be closed on programs termination, so don't worry
        s_in = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_L2CAP)
        s_out = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_L2CAP)
        s_in.connect((mac, 0x13))  # wiimote receive port=19
        s_out.connect((mac, 0x11)) # wiimote transmit port=17
    except OSError:
        print('Wiimote not found or bluetooth not available.')
        exit()
    print('Connected.')

    # request button only mode
    s_out.send(b'\x52\x12\x00\x30')
    # enable first player led
    s_out.send(b'\x52\x11\x10')

    while True:
        try:
            # read enough bytes, but only use the first 4 bytes
            msg = s_in.recv(23)[:4]
        except Exception as e:
            print(e)
            continue

        buttons = []

        # msg layout:    0  1  2  3
        #             (a1) 30 BB BB
        for i in [2, 3]:
            for hexv in bitmap:
                # test each bit, it represents a pressed button
                if msg[i] & hexv[0]:
                    buttons.append(hexv[i-1])

        check_buttons(buttons, mapping)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
