import copy

from fsatoolbox import fsa, analysis


def trim(fsa_obj: fsa):

    G = copy.deepcopy(fsa_obj)

    if G.is_Trim is None:
        analysis.get_trim_info(G)

    if G.is_Trim:
        return G

    for x in G.X:
        if not (x.is_Reachable and x.is_co_Reachable):
            G.remove_state(x)

    return G
