import shlex
from unicodedata import category
import colorama
from numpy import load
from termcolor import colored
import os

from basic_CLI.exceptions import *
from basic_CLI.commands_CLI import cmdict
from basic_CLI.utils_CLI import *

class Container:
    def __init__(self,data):
        self.data = data
    def __str__(self):
        return str(self.data)

home = os.path.normpath(os.path.expanduser("~"))
path = Container(home + '/Documents/FsaToolbox')

fsalst = dict()

# splashscreen
forg_color = 'green'
back_color = 'cyan'
back1_color = 'on_grey'
splash = [" ███████╗███████╗ █████╗ ████████╗ ██████╗  ██████╗ ██╗     ██████╗  ██████╗ ██╗  ██╗",
          " ██╔════╝██╔════╝██╔══██╗╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔══██╗██╔═══██╗╚██╗██╔╝",
          " █████╗  ███████╗███████║   ██║   ██║   ██║██║   ██║██║     ██████╔╝██║   ██║ ╚███╔╝ ",
          " ██╔══╝  ╚════██║██╔══██║   ██║   ██║   ██║██║   ██║██║     ██╔══██╗██║   ██║ ██╔██╗ ",
          " ██║     ███████║██║  ██║   ██║   ╚██████╔╝╚██████╔╝███████╗██████╔╝╚██████╔╝██╔╝ ██╗",
          " ╚═╝     ╚══════╝╚═╝  ╚═╝   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝"]
for row in splash:
    for char in row:
        if char == '█':
            print(colored(char, forg_color), end='')
        else:
            print(colored(char, back_color, back1_color), end='')
    print("")
print("\nNote: this is still in development")
print("Type \"help\" to see the list of commands")
print("\n\nNote: the default path is:")
print(path)
print("")


while True:
    try:
        inp = shlex.split(input(">>"), posix=False)
    except KeyboardInterrupt:
        exit()

    #check if the input is the function format -> todo fun?
    if  "(" in inp[0] and ")" in inp[0]: #TODO regex
        if '=' in inp[0]:
            # dest=inp[0].split('=')[0]
            comm=inp[0].split('=')[1].split('(')[0]
            args=[inp[0].split('=')[0]] + inp[0].split('(')[1].split(')')[0].split(',')
            opts=inp[1:]
        else:
            # dest=None
            comm=inp[0].split('(')[0]
            args=inp[0].split('(')[1].split(')')[0].split(',')
            opts=inp[1:]+['-printOnly']
    else:
        comm = inp[0]
        if len(inp)>1:
            # dest=inp[1]
            args = [x for x in inp[1:] if '-' not in x]
            opts = [x for x in inp[1:] if '-' in x]
        else:
            # dest=None
            args=[]
            opts=[]

    if comm in cmdict:
        try:
            # print("dest:"+str(dest))
            print("args:"+str(args))
            print("opts:"+str(opts))
            cmdict[comm].f(args=args, opts=opts, fsalst=fsalst, path=path)
        except ArgsException:
            print("ArgsExc")
            print("Help:")
            print(cmdict[comm].help)
            print(cmdict[comm].help_more)
        except BException:
            print("BExc, serotta, ma in un'altro modo")
    else:
        print("Unknown command")