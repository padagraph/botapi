#-*- coding:utf-8 -*-
""":mod:`botapi`
=================
"""
try:

    from botapi import Botagraph, BotaIgraph, BotApiError, BotLoginError
    from botio import Botio

except :
    from botapi.botapi import Botagraph, BotaIgraph, BotApiError, BotLoginError

__all__ =  ["Botagraph", "BotaIgraph", "BotLoginError","BotApiError", "Botio"]


def arg_bot_parser():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--host", action='store', help="host", default="http://localhost:5000")
    parser.add_argument("--key" , action='store', help="authentification token", default=None)

    return parser
    