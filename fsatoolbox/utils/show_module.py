import numpy as np
from tabulate import tabulate

from fsatoolbox.utils.filter_delta import filter_delta


def show_full(X, E, delta):
    column_labels = ["X"] + [x.label for x in E]

    data = np.empty((len(X), len(E) + 1), dtype='U100')
    data[:, 0] = [x.label for x in X]

    event_table = np.empty((1, len(E)), dtype='U100')
    state_table = np.empty((1, len(X)), dtype='U100')

    for i, state in enumerate(X):
        for j, event in enumerate(E):

            filtered_events = filter_delta(delta, state, event)['end'].values
            end_labels = [x.label for x in filtered_events]
            string = ""

            if not end_labels:
                data[i, j + 1] = "-"
                continue

            for end in end_labels:

                if not string:

                    string += end

                else:

                    string += ", " + end

            data[i, j + 1] = string

    # Populating the column representing the properties of the states

    # TODO: Find a better solution

    for i, state in enumerate(X):

        props = ["isInitial", "isFinal"]
        props_label = ["I", "F"]
        true_props_label = []

        state_attr = vars(state)

        for idx, prop in enumerate(props):
            if state_attr[prop]:
                true_props_label.append(props_label[idx])

        if len(true_props_label) != 0:
            state_table[:, i] = ", ".join(true_props_label)

        else:
            state_table[:, i] = "-"

    # Populating the table representing the properties of the events

    for i, event in enumerate(E):

        string = ""

        if not event.isObservable:
            string += "U0"

        if not event.isControllable:

            if string:
                string += ", "

            string += "UC"

        if event.isFault:

            if string:
                string += ", "

            string += "F"

        if not string:

            event_table[:, i] = "-"

        else:

            event_table[:, i] = string

    table = tabulate(data, headers=column_labels, stralign="center", tablefmt='fancy_grid', maxcolwidths=16)
    event_properties = tabulate(event_table, headers=E, stralign="center", tablefmt='fancy_grid')
    state_properties = tabulate(state_table, headers=X, stralign="center", tablefmt='fancy_grid')

    text = "\nSummary:\n" + \
           table + \
           "\n\nEvent Properties:\n" + \
           event_properties + \
           "\nLegend: O: Observable, C: Controllable, F: Fault\n\n" + \
           "State Properties:\n" + \
           state_properties + \
           "\nLegend: I: Initial, F: Final\n "

    return text


def show_comp(X, E, delta):
    column_labels = ["X"] + [x.label for x in E]

    data = np.empty((len(X), len(E) + 1), dtype='U100')
    data[:, 0] = [x.label for x in X]

    for i, x in enumerate(X):

        props_list = []
        x_props = ""
        state_attr = vars(x)

        if state_attr["isInitial"]:
            props_list.append("I")
        if state_attr["isFinal"]:
            props_list.append("F")

        if len(props_list) != 0:
            x_props = ", ".join(props_list)
            x_props = "[{}]".format(x_props)

        data[0, i] += " {}".format(x_props)

    for i, e in enumerate(E):

        props_list = []
        e_props = ""
        ev_attr = vars(e)

        if not ev_attr["isControllable"]:
            props_list.append("UC")
        if not ev_attr["isObservable"]:
            props_list.append("UO")
        if ev_attr["isFault"]:
            props_list.append("F")

        if len(props_list) != 0:
            e_props = ", ".join(props_list)
            e_props = "[{}]".format(e_props)

        column_labels[i + 1] += " {}".format(e_props)

    for i, state in enumerate(X):
        for j, event in enumerate(E):

            filtered_events = filter_delta(delta, state, event)['end'].values
            end_labels = [x.label for x in filtered_events]
            string = ""

            if not end_labels:
                data[i, j + 1] = "-"
                continue

            for end in end_labels:

                if not string:

                    string += end

                else:

                    string += ", " + end

            data[i, j + 1] = string

    # Populating the column representing the properties of the states

    table = tabulate(data, headers=column_labels, stralign="center", tablefmt='fancy_grid', maxcolwidths=16)

    text = "\nSummary:\n" + table + \
           "\nState properties legend: I - Initial, F - Final\n" + \
           "Event properties legend: UC - Uncontrollable, UO - Unobservable, F - Fault\n"

    return text
