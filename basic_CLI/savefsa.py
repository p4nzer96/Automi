import os.path
from basic_CLI.exceptions import ArgsException

import fsatoolbox
from fsatoolbox import *
from termcolor import colored
import colorama

colorama.init()


def save_CLI(args_d):
    args=args_d['args']
    fsalst=args_d['fsalst']
    path=args_d['']
    if len(args) < 2:
        raise ArgsException()

    if args[0] in fsalst:

        if not os.path.isabs(args[1]):
            filename = os.path.join(path, args[1])
        else:
            filename = args[1]

        try:
            fsalst[args[0]].to_file(filename)  # current path
        except Exception as e:
            print(colored("Error while saving the file:", "red"))
            print(e)
    else:
        print(colored("Error, fsa doesn't exists", "red"))
