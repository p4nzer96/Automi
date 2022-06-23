from basic_CLI.exceptions import ArgsException
from termcolor import colored
import os


def chdir(path, args,**kwargs):
    
    if len(args)<1:
        raise ArgsException()

    # Path is absolute
    if os.path.isabs(os.path.normpath(args[0])):
        if os.path.isdir(os.path.normpath(args[0])):
            path.data = os.path.normpath(args[0])
        else:
            print(colored("Invalid path", "red"))

        # Path is not absolute
    else:
        tail = os.path.normpath(args[0])
        head = path.data
        # Parsing the path
        parsed_path = os.path.split(tail)

        # ".." Escape character
        if ".." in parsed_path:
            if parsed_path == ("", ".."):
                new_path = os.path.split(head)[0]
            elif parsed_path[0] == ".." and parsed_path[1] != "":
                head = os.path.split(path)[0]
                tail = parsed_path[1]
                new_path = os.path.join(head, tail)
            else:
                print(colored("Invalid path", "red"))

        # "." Escape character
        elif "." in parsed_path:
            if parsed_path == ("", "."):
                new_path = head
            elif parsed_path[0] == "." and parsed_path[1] != "":
                tail = parsed_path[1]
                new_path = os.path.join(path.data, tail)
            else:
                print(colored("Invalid path", "red"))

        # No escape character
        else:
            new_path = os.path.join(head, tail)

        # Checking if new_path exists
        if os.path.isdir(new_path):
            path.data = new_path
        else:
            print(colored("Invalid path", "red"))

def showdir(path, **kwargs):
    print(path)

def ldir(path, **kwargs):
    print(colored("\nElements in: ", "yellow", attrs=["bold"]) + path.data + "\\\n")
    l = os.listdir(path.data + "\\")  # files only
    for el in l:
        print(el)

def show_CLI(args, fsalst, **kwargs):
    if len(args)<1: raise ArgsException()

    if args[0] not in fsalst:
        print(colored("Error, fsa doesn't exists", "red"))
        return

    print(fsalst[args[0]])

def list_CLI(fsalst, **kwargs):  # TODO add some stats?
    for key, value in fsalst.items():
        print(key)

def remove_CLI(args, fsalst):
    if len(args)<1: raise ArgsException()

    if args[0] not in fsalst:
        print("fsa not found")
        return

    del fsalst[args[0]]

def clear_CLI(fsalst, **kwargs):
    fsalst=dict()

def stupidf2(args,**kwargs):
    raise BException


