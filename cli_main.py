import os
import re
import shlex

from termcolor import colored
from fsatoolbox_cli.cli_commands import cmdict


def parse(inp):
    inp1 = shlex.split(inp, posix=False)
    if not inp1: return {'comm': None, 'args': [], 'opts': []}

    # remove spaces
    inp_noSpaces = inp.replace(" ", "")

    # pattern a=b(c,d)
    if re.compile('.*=.*\(.*\)').match(inp_noSpaces):

        # the command is between '=' and '('
        comm = inp_noSpaces.split('=')[1].split('(')[0]

        # the first argument is before '='
        args = [inp_noSpaces.split('=')[0]]
        # the other arguments are between the first and last parenthesis, splitted by a comma
        args = args + inp_noSpaces.split("(")[1].split(")")[0].split(',')

        # The options are after the parenthesis, marked by a '-' before
        try:
            opts = re.findall('-[a-zA-Z]+', inp_noSpaces.split(')')[-1])
        except AttributeError:
            opts = []

        pattern = 'matlab_eq'

        return pattern, {'comm': comm, 'args': args, 'opts': opts}

    # pattern a(b,c)
    if re.compile('.*\(.*\)').match(inp_noSpaces):

        # the command is before '('
        comm = inp_noSpaces.split('(')[0]

        # the arguments are between the first and last parenthesis, splitted by a comma
        args = inp_noSpaces.split("(")[1].split(")")[0].split(',')

        # The options are after the parenthesis, marked by a '-' before
        try:
            opts = re.findall('-[a-zA-Z]+', inp_noSpaces.split(')')[-1])
        except AttributeError:
            opts = []
            opts.append('-printOnly')

        pattern = 'matlab'

        return pattern, {'comm': comm, 'args': args, 'opts': opts}

    # pattern a b c d
    inp = list(filter(None, inp.split(' ')))  # split by spaces

    comm = inp[0] if len(inp) > 0 else None
    args = [x for x in inp[1:] if '-' not in x]
    opts = [x for x in inp[1:] if '-' in x]

    pattern = 'standard'

    return pattern, {'comm': comm, 'args': args, 'opts': opts}


def checkinput(pattern, inp):
    p_command = inp['comm']

    if p_command not in cmdict.keys():
        print(colored("ERROR: Unrecognized command", "red"))
        return False

    if pattern not in cmdict[p_command].input_formats:
        print(colored("ERROR: Input format not supported", "red"))
        return False

    return True


if __name__ == "__main__":

    forg_color = 'green'
    back_color = 'cyan'
    back1_color = 'on_grey'
    splash = [" ███████╗███████╗ █████╗ ████████╗ ██████╗  ██████╗ ██╗     ██████╗  ██████╗ ██╗  ██╗",
              " ██╔════╝██╔════╝██╔══██╗╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔══██╗██╔═══██╗╚██╗██╔╝",
              " █████╗  ███████╗███████║   ██║   ██║   ██║██║   ██║██║     ██████╔╝██║   ██║ ╚███╔╝ ",
              " ██╔══╝  ╚════██║██╔══██║   ██║   ██║   ██║██║   ██║██║     ██╔══██╗██║   ██║ ██╔██╗ ",
              " ██║     ███████║██║  ██║   ██║   ╚██████╔╝╚██████╔╝███████╗██████╔╝╚██████╔╝██╔╝ ██╗",
              " ╚═╝     ╚══════╝╚═╝  ╚═╝   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝"]
    print("")
    for row in splash:
        for char in row:
            if char == '█':
                print(colored(char, forg_color), end='')
            else:
                print(colored(char, back_color, back1_color), end='')
        print("")

    print("Note: this is still in development")
    print("Type \"help\" to see the list of commands\n")

    args = []
    opts = []

    cmdict["showdir"].func_call(args, opts)
    print("")

    while True:
        str_inp = input(">> ")

        pattern, inp = parse(str_inp)

        if checkinput(pattern, inp):
            if pattern == 'matlab':
                inp['args'] = [None] + inp['args']
            print(inp['args'])
            cmdict[inp['comm']].func_call(inp['args'], inp['opts'])
