#!/usr/bin/env python3.4

import socket
import subprocess
import argparse

def readconfig(path):
    mapping = {}
    try:
        conf = open(path, 'r').readlines()
        for line in conf:
            if line != '\n':
                keys = line.split()
                mapping[keys[0]] = keys[1:]
    except Exception as e:
        print('Unable to parse config', path)
        if DEBUG:
            print(e)
        exit()
    return mapping

def do(action):
    if action == ['EXIT']:
        exit()
    elif action:
        # use Popen to run command in background
        subprocess.Popen(action)

def check_buttons(buttons, mapping):
    if buttons:
        print(buttons)

    for button in buttons:
        if button in mapping.keys():
            do(mapping[button])

def main():
    parser = argparse.ArgumentParser(description='wiimote2shell remote control program')
    parser.add_argument('--device', '-d', help='wiimote mac address', required=True)
    parser.add_argument('--config', '-c', help='config file path', required=True)
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    global DEBUG
    DEBUG = args.debug
    mac = args.device
    mapping = readconfig(args.config)

    if DEBUG:
        print(mapping)
        print(mac)

    # http://wiibrew.org/wiki/Wiimote#Buttons
    bitmap = [[0x01, 'LEFT' , 'TWO'],
              [0x02, 'RIGHT', 'ONE'],
              [0x04, 'DOWN' , 'B'],
              [0x08, 'UP'   , 'A'],
              [0x10, 'PLUS' , 'MINUS'],
              [0x80, None   , 'HOME']]

    print('Press 1 + 2 on your Wiimote...')
    try:
        # sockets will magically be closed on programs termination, so don't worry
        s_in = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_L2CAP)
        s_out = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_L2CAP)
        s_in.connect((mac, 0x13))
        s_out.connect((mac, 0x11))
    except OSError:
        print('Wiimote not found or bluetooth not available.')
        exit()
    print('Connected.')

    # request button only mode
    s_out.send(bytes('\x52\x12\x00\x30', 'ascii'))
    # enable first player led
    s_out.send(bytes('\x52\x11\x10', 'ascii'))

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
                # apply bitmask
                if msg[i]&hexv[0]:
                    buttons.append(hexv[i-1])

        check_buttons(buttons, mapping)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
