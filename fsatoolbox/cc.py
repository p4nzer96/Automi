from fsatoolbox import fsa
from fsatoolbox.state import state
from fsatoolbox.utils.misc import v_print


def cc(G0, G1, verbose=False, name_style=1):
    """
    Function used to compute the concurrent composition between two FSAs

    Args:
        G0 (fsa): input FSA
        G1 (fsa): input FSA
        verbose (optional, bool): if true shows the steps followed by the algorithm. Defaults to False
        name_style(optional, int): Default=0, defines the style of the state label in the concurrent composition
        0 -> (AB), 1 -> (A, B)
    Returns: A FSA which represent the concurrent composition of the two FSA in input
    """

    CC = fsa()

    # The alphabet of the output NFA is the union of the two alphabets

    X = []
    delta = []

    # Union of the two alphabets
    CC.E = []

    for x in (G0.E + G1.E):
        if x not in CC.E:
            CC.E.append(x)

    if len(G0.x0) == 0 or len(G1.x0) == 0:
        raise TypeError("Initial states not set")

    # The initial state is obtained by the cartesian product of the two initial states

    Xnew = [[G0.x0[0], G1.x0[0]]]  # TODO multiple starting states?

    while len(Xnew) > 0:
        sel_state = Xnew[0]  # selecting a new state from Xnew
        sel_state_1 = sel_state[0]  # state 1
        sel_state_2 = sel_state[1]  # state 2

        if name_style == 0:

            v_print("\n ----- State: ({}{}) -----\n".format(sel_state_1.label, sel_state_2.label), verbose)

        elif name_style == 1:

            v_print("\n ----- State: ({}, {}) -----\n".format(sel_state_1.label, sel_state_2.label), verbose)

        else:
            raise ValueError("Name style not defined")

        for event in CC.E:
            v_print("Event: {}".format(event.label), verbose, end=' -> ')

            # Case: Private event to G0

            if event in G0.E and event not in G1.E:
                v_print("Private G0", verbose, end=' -> ')
                trans = G0.filter_delta(start=str(sel_state_1.label), transition=str(event.label))
                if not trans.empty:
                    for _, el in trans.iterrows():
                        v_print("{} {} {}".format(el['start'].label, el['transition'].label, el['end'].label), verbose)
                        newState = [el['end'], sel_state_2]
                        delta.append([sel_state, event, newState])
                        if newState not in X and newState not in Xnew:
                            Xnew.append(newState)
                else:
                    v_print("No transitions", verbose)

            # Case: Private event to G1

            elif event not in G0.E and event in G1.E:
                v_print("Private G1", verbose, end=' -> ')
                trans = G1.filter_delta(start=str(sel_state_2.label), transition=str(event.label))
                if not trans.empty:
                    for _, el in trans.iterrows():
                        v_print("{} {} {}".format(el['start'].label, el['transition'].label, el['end'].label), verbose)
                        newState = [sel_state_1, el['end']]
                        delta.append([sel_state, event, newState])
                        if newState not in X and newState not in Xnew:
                            Xnew.append(newState)
                else:
                    v_print("No transitions", verbose)

            # Case: Synchronized events

            else:
                v_print("Synchronized", verbose, end=' -> ')

                transG0 = G0.filter_delta(start=str(sel_state_1.label), transition=str(event.label))
                transG1 = G1.filter_delta(start=str(sel_state_2.label), transition=str(event.label))

                if not transG0.empty and not transG1.empty:
                    for _, el0 in transG0.iterrows():
                        for _, el1 in transG1.iterrows():
                            v_print("[{} {} {}".format(el0['start'].label, el0['transition'].label, el0['end'].label),
                                    verbose, end=" , ")
                            v_print("{} {} {}]".format(el1['start'].label, el1['transition'].label, el1['end'].label),
                                    verbose)
                            newState = [el0['end'], el1['end']]
                            delta.append([sel_state, event, newState])
                            if newState not in X and newState not in Xnew:
                                Xnew.append(newState)
                else:
                    v_print("No transitions", verbose)

        X.append(sel_state)
        Xnew.remove(sel_state)

    # Adding states in the CC FSA

    for x in X:

        if name_style == 0:
            label = "{}{}".format(x[0], x[1])
        elif name_style == 1:
            label = "({}, {})".format(x[0], x[1])

        new_state = state(label, False, False, False)

        # Final States

        if x[0].isFinal and x[1].isFinal:
            new_state.isFinal = True

        # Initial States

        if x[0].isInitial and x[1].isInitial:
            new_state.isInitial = True

        # Forbidden States

        if x[0].isForbidden or x[1].isForbidden:
            new_state.isForbidden = True

        CC.add_state(new_state)

    for el in delta:
        s_first_state = el[0][0]
        s_second_state = el[0][1]

        e_first_state = el[2][0]
        e_second_state = el[2][1]

        start_state = "({}, {})".format(s_first_state, s_second_state)
        end_state = "({}, {})".format(e_first_state, e_second_state)

        if name_style == 0:

            CC.add_transition(el[0][0].label + el[0][1].label, el[1].label, el[2][0].label + el[2][1].label)

        elif name_style == 1:

            CC.add_transition(start_state, el[1].label, end_state)

    return CC
