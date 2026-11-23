"""
Serve one of the benchmark apps: python serve.py <classic|ui> <port>
"""
import sys

import panel as pn

from apps import APPS

if __name__ == '__main__':
    name, port = sys.argv[1], int(sys.argv[2])
    pn.serve({name: APPS[name]}, port=port, show=False, verbose=False, websocket_origin='*')
