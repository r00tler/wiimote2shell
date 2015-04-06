#!/usr/bin/env python3.4

import socket
import subprocess
import argparse

# <<< CONFIG BEGIN >>>

MAC = '00:22:AA:90:26:86'
#  Wiimote Button -> action
MAPPING = {'LEFT' : 'xdotool key Left',
           'RIGHT': 'xdotool key Right',
           'UP'   : 'xdotool key Up',
           'DOWN' : 'xdotool key Down',
           'PLUS' : 'xdotool key W', # upvote
           'MINUS': 'xdotool key S', # downvote
           'ONE'  : None,
           'TWO'  : None,
           'A'    : None,
           'B'    : None
          }
          # HOME -> Exit program

# <<< CONFIG END >>>

def readconfig():


def do(action):
    subprocess.call(action.split())

def check_buttons(buttons):
    if buttons:
        print(buttons)

    # intersect buttons pressed and mappings available
    for button in buttons:
        if button in MAPPING.keys():
            if MAPPING[button]:
                do(MAPPING[button])

def main():
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
        s_in.connect((MAC, 0x13))
        s_out.connect((MAC, 0x11))
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
        if 'HOME' in buttons:
            print('Disconnected.')
            break

        check_buttons(buttons)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
