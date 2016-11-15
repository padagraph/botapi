#-*- coding:utf-8 -*-
""":mod:`botapi`
=================
"""

from botapi import Botagraph, BotApiError
from botio import Botio

__all__ =  ["Botagraph", "BotApiError", "Botio"]

def arg_bot_parser():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--host", action='store', help="host", default="http://localhost:5000")
    parser.add_argument("--key" , action='store', help="authentification token", default=None)

    return parser
    