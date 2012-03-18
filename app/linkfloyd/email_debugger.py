#!/usr/bin/env python
"""
Like the built-in debugging server, but unwarps long lines for easier
copy/paste of URLs.
"""
from __future__ import print_function
from smtpd import SMTPServer
import os

class DebuggingServer(SMTPServer):
    def process_message(self, peer, mailfrom, rcpttos, data):
        inheaders = 1
        lines = data.split('\n')
        print('---------- MESSAGE FOLLOWS ----------')
        for line in lines:
            # headers first
            if inheaders and not line:
                print('X-Peer:', peer[0])
                inheaders = 0
            if line.endswith('='):
                print(line[:-1], end='')
            else:
                print(line)
        print('------------ END MESSAGE ------------')

if __name__ == "__main__":
    os.system("python -m smtpd -n -c DebuggingServer localhost:1025")
