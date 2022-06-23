from termcolor import colored
from basic_CLI.exceptions import ArgsException

import fsatoolbox
from fsatoolbox import *
import colorama

colorama.init()


def fm_CLI(args, opts, fsalst, **kwargs):

    printOnly = '-printOnly' in opts

    if printOnly:
        args_n=1
    else:
        args_n=2

    if len(args) < args_n: raise ArgsException()

    if not printOnly and args[0] in fsalst:
        inp = input(colored("Error, fsa already exists, do you want to overwrite it? [y/N]: ", "red"))
        if inp == 'N' or inp == 'n' or inp == '':
            return

    if args[args_n-1] not in fsalst:
        print(colored("Error, fsa doesn't exists", "red"))
        return

    try:
        result = fm(fsalst[args[args_n-1]])
        if printOnly:
            print(result)
        else:
            fsalst[args[0]]=result
    except Exception as e:
        print(colored("There was an error while computing the concurrent composition:", "red"))
        print(e)
        return
    
    
