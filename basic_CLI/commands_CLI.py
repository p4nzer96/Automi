from termcolor import colored
from basic_CLI.utils_CLI import *

from basic_CLI.load_CLI import load_CLI
# from basic_CLI.observer import nfa2dfa_CLI
from basic_CLI.savefsa import save_CLI
from basic_CLI.fsabuilder import build_CLI

from basic_CLI.cc_CLI import cc_CLI
from basic_CLI.trim_CLI import trim_CLI
from basic_CLI.fm_CLI import fm_CLI
from basic_CLI.diag_CLI import diag_CLI
from basic_CLI.nfa2dfa_CLI import nfa2dfa_CLI
from basic_CLI.hhat_CLI import hhat_CLI
from basic_CLI.compute_supervisor_CLI import compute_supervisor_CLI

from basic_CLI.analysis import reachability, coreachability, blocking, trim, dead, reverse

class command():
    def __init__(self, help, help_more, category, f):
        self.help=help
        self.help_more=help_more
        self.category=category
        self.f=f

def help(args,**kwargs):
    if len(args)>0 and args[0] in cmdict:
        print(cmdict[args[0]].help)
    else:
        commandstypes=['basic', 'functions', 'analysis']
        for ct in commandstypes:
            print(colored("-------------------------- "+ct+"  --------------------------\n", "green"))
            for key, value in cmdict.items():
                if value.category==ct: 
                    print("->"+ colored(key, "yellow"),end=':')
                    if len(key)<5:
                        print("\t",end='')
                    print("\t"+cmdict[key].help)

cmdict={
    'chdir' : command(
        help=colored("chdir: ", "yellow", attrs=["bold"]) + "\tThis functions changes the default path",
        help_more=colored("Usage:", attrs=["bold"]) + "\n\tchdir newpath" +
        colored("\nExample:", attrs=["bold"]) + "\n\tchdir C:\\\\Automi" +
        colored("\nNotes: ", attrs=["bold"]) + "\n\t * In windows use \\\\ instead of \\ (ex. C:\\\\Automi) or put the path in brackets (ex. \"C:\\Automi\\\")", 
        category='basic', 
        f=chdir
    ),
    'showdir' : command(
        help=colored("showdir:", "yellow", attrs=["bold"]) + "Prints the current working directory", 
        help_more='',
        category='basic', 
        f=showdir
    ),
    'ldir' : command(
        help=colored("ldir: ", "yellow", attrs=["bold"]) + "\tShow files/dirs inside current working folder", 
        help_more='',
        category='basic', 
        f=ldir
    ),
    'load' : command(
        help=colored("load:", "yellow", attrs=["bold"]) + "\tThis functions loads a fsa from a file",
        help_more=colored("Usage:\n\t", attrs=["bold"]) + "load fsa_name path_to_file"+
        colored("\nExample:\n\t", attrs=["bold"]) + "load C:\\\\Automi\\\\Examples\\\\G0.fsa"+
        colored("\nNotes: ", attrs=["bold"]) + "\n\t * In windows use \\\\ instead of \\ (ex. C:\\\\Automi) or put the path in brackets (ex. \"C:\\Automi\\\")"+
        "\t * This function will load .fsa and .txt files", 
        category='basic', 
        f=load_CLI
    ),
    'save' : command(
        help=colored("save: ", "yellow", attrs=["bold"]) + "\tSaves a FSA to file",
        help_more=colored("Usage:", attrs=["bold"]) + "\n\tsave fsa_to_save path_to_file"+
        colored("\nExample:", attrs=["bold"]) + "\n\tsave G0 G0.fsa"+
        colored("\nNotes: ", attrs=["bold"]) + "\n\t * Only .fsa files currently supported", 
        category='basic', 
        f=save_CLI
    ),
    'build' : command(
        help=colored("build: ", "yellow", attrs=["bold"]) + "\tThis functions starts an interactive program to build a FSA",
        help_more=colored("Usage:", attrs=["bold"]) + "\n\tbuild fsa_name (ex: build G0)"+
        colored("\nExample:", attrs=["bold"]) + "\n\tbuild G0", 
        category='basic', 
        f=build_CLI
    ),
    'show' : command(
        help=colored("show: ", "yellow", attrs=["bold"]) + "\tPrints the structure of the FSA",
        help_more=colored("Usage:", attrs=["bold"]) + "\n\tshow fsa_name"+
        colored("\nExample:", attrs=["bold"]) + "\n\tshow G0", 
        category='basic', 
        f=show_CLI
    ),
    'list' : command(
        help=colored("list: ", "yellow", attrs=["bold"]) + "\tPrints the FSA currently loaded",
        help_more=colored("Usage:", attrs=["bold"]) + "\n\tlist", 
        category='basic', 
        f=list_CLI
    ),
    'remove' : command(
        help=colored("remove:", "yellow", attrs=["bold"]) + "\tRemoves a FSA",
        help_more=colored("Usage:", attrs=["bold"]) + "\n\tremove fsa_name"+
        colored("\nExample:", attrs=["bold"]) + "\n\tremove G0",
        category='basic', 
        f=remove_CLI
    ),
    'clear' : command(
        help=colored("\clear:", "yellow", attrs=["bold"]) + "\tRemoves all the FSAs",
        help_more='',
        category='basic', 
        f=clear_CLI
    ),
    'cc' : command(
        help=colored("cc: ", "yellow", attrs=["bold"]) + "\tThis functions computes the concurrent composition between two FSAs",
        help_more=colored("Usage:", attrs=["bold"]) +
        "\n\tcc outputname input1 input2" +
        colored("\nOptional arguments:", attrs=["bold"]) +
        "\n\t-v verbose output, this will print the steps of the algorithm" +
        colored("\nExample:", attrs=["bold"]) + "\n\tcc G2 G0 G1"
        ,
        category='functions', 
        f=cc_CLI
    ),
    'trim' : command(
        help=colored("trimfsa:", "yellow", attrs=["bold"]) + "This functions computes a trim of a FSA ",
        help_more=colored("Usage:", attrs=["bold"]) + "\n\ttrimfsa output input"+
                    colored("\nExample:", attrs=["bold"]) + "\n\ttrimfsa G2 G1"+
                    "\n\tcc outputname input1 input2" +
                    colored("\nOptional arguments:", attrs=["bold"]) +
                    "\n\t-v verbose output, this will print the steps of the algorithm" +
                    colored("\nExample:", attrs=["bold"]) + "\n\tcc G2 G0 G1",
        category='functions', 
        f=trim_CLI
    ),
    'fm' : command(
        help=colored("fm: ", "yellow", attrs=["bold"]) + "\tThis functions computes the fault monitor of the given fsa",
        help_more=colored("Usage:", attrs=["bold"]) + "\n\tfm outputname inputname"+
                    colored("\nExample:", attrs=["bold"]) + "\n\tfm F G0",
        category='functions',
        f=fm_CLI
    ),
    'diag' : command(
        help=colored("diag: ", "yellow", attrs=["bold"]) + "\tThis function computes the diagnoser of a fsa",
        help_more=colored("Usage:", attrs=["bold"]) + "\n\tdiag outputname inputname"+
                    colored("\nOptional arguments:", attrs=["bold"]) + "\n\t-v verbose output, this will print the steps of the algorithm"+
                    "\nExample:" + "\n\tdiag G1 G0",
        category='functions',
        f=diag_CLI
    ),
    'nfa2dfa' : command(
        help=colored("obs: ", "yellow", attrs=["bold"]) + "\tThis functions computes the equivalent DFA of the given NFA",
        help_more=colored("Usage:", attrs=["bold"]) + "\n\tobs outputname inputname"+
                    colored("\nExample:", attrs=["bold"]) + "\n\tobs G0 N0",
        category='functions',
        f=nfa2dfa_CLI
    ),
    'exth' : command(
        help=colored("exth: ", "yellow", attrs=["bold"]) + "\tThis functions computes the extended specification automaton, given the specification automaton H",
        help_more=colored("Usage:", attrs=["bold"]) + "\n\texth outputname inputname (Ex: exth H1 H) "+
                    colored("\nExample:", attrs=["bold"]) + "\n\texth H1 H",
        category='functions',
        f=hhat_CLI
    ),
    'supervisor' : command(
        help=colored("supervisor:", "yellow", attrs=["bold"]) + "This functions computes the supervisor of an automaton G, given the specification automaton H",
        help_more=colored("Usage:", attrs=["bold"]) + "\n\tsupervisor outputname automaton_name specif_automaton_name"+
                    colored("\nOptional arguments:", attrs=["bold"]) + "\n\t-v verbose output, this will print the steps of the algorithm"+
                    colored("\nExample:" + "\n\tsupervisor G0 H"),
        category='functions',
        f=compute_supervisor_CLI
    ),
    'reach' : command(
        help='This functions computes the reachability of a fsa',
        help_more=colored("Usage:", attrs=["bold"]) + "\n\treach fsa_name\n"+
                    colored("Example:", attrs=["bold"]) + "\n\treach G0",
        category='analysis',
        f=reachability
    ),
    'coreach' : command(
        help='This functions computes the co-reachability of a fsa',
        help_more=colored("Usage:", attrs=["bold"]) + "\n\tcoreach fsa_name\n"+
                    colored("Example:", attrs=["bold"]) + "\n\tcoreach G0",
        category='analysis',
        f=coreachability
    ),
    'blocking' : command(
        help='This functions computes if the fsa is blocking',
        help_more=colored("Usage:", attrs=["bold"]) + "\n\tblocking fsa_name\n"+
                    colored("Example:", attrs=["bold"]) + "\n\tblocking G0",
        category='analysis',
        f=blocking
    ),
    'trim' : command(
        help='This functions computes if the fsa is trim',
        help_more=colored("Usage:", attrs=["bold"]) + "\n\ttrim fsa_name\n"+
                    colored("Example:", attrs=["bold"]) + "\n\ttrim G0",
        category='analysis',
        f=trim
    ),
    'dead' : command(
        help='This functions computes if a fsa has dead states',
        help_more=colored("Usage:", attrs=["bold"]) + "\n\tdead fsa_name\n"+
                    colored("Example:", attrs=["bold"]) + "\n\tdead G0",
        category='analysis',
        f=dead
    ),
    'reverse' : command(
        help='This functions computes if the fsa is reversible',
        help_more=colored("Usage:", attrs=["bold"]) + "\n\treverse fsa_name\n"+
                    colored("Example:", attrs=["bold"]) + " \n\treverse G0",
        category='analysis',
        f=reverse
    ),
    'cmd2' : command(
        help='This function does nothing, but better (si rompe)',
        help_more='',
        category='No options here too', 
        f=stupidf2
    ),
    'help' : command(
        help='This function prints the help!', 
        help_more='',
        category='No options here too', 
        f=help
    )
}