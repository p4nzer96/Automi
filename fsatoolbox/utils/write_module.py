import json

from fsatoolbox.utils.filter_delta import filter_delta


def save_json(filename, X, E, delta):
    # Base dict structure
    fsa_dict = dict.fromkeys(["X", "E", "delta"])

    # Populating the states
    fsa_dict["X"] = dict.fromkeys([x.label for x in X])

    for x in X:

        state_properties = vars(x)
        dict_x = {}

        for prop in state_properties.keys():

            if state_properties[prop] is not None:
                dict_x[str(prop)] = state_properties[prop]

        fsa_dict["X"][x.label] = dict_x

    # Events
    fsa_dict["E"] = dict.fromkeys([e.label for e in E])

    for e in E:

        event_properties = vars(e)
        dict_e = {}

        for prop in event_properties.keys():

            if event_properties[prop] is not None:
                dict_e[str(prop)] = event_properties[prop]

        fsa_dict["E"][e.label] = dict_e

    # Delta
    fsa_dict["delta"] = dict.fromkeys(list(delta.index))

    for index, row in delta.iterrows():
        fsa_dict["delta"][index] = dict.fromkeys(["start", "fsa_event", "end"])

        fsa_dict["delta"][index]["start"] = row[0].label
        fsa_dict["delta"][index]["fsa_event"] = row[1].label
        fsa_dict["delta"][index]["end"] = row[2].label

    with open(filename, "w") as outfile:
        json.dump(fsa_dict, outfile, indent=4)


def save_txt(filename, X, E, delta):
    n_states = str(len(X))

    with open(filename, "w") as f:

        f.write(n_states)
        f.write("\n\n")

        event_dict = {}

        for event in E:

            if event.isControllable is True:
                controllable = "c"
            elif event.isControllable is False:
                controllable = "uc"
            else:
                controllable = ""

            if event.isObservable is True:
                observable = "o"
            elif event.isObservable is False:
                observable = "uo"
            else:
                observable = ""

            if event.isFault is True:
                fault = "f"
            elif event.isFault is False:
                fault = "uf"
            else:
                fault = ""

            event_dict[event] = {"isControllable": controllable, "isObservable": observable, "isFault": fault}

        for state in X:

            label = state.label
            initial_str = str(int(state.isInitial))
            final_str = str(int(state.isFinal))

            f.write(f'{label:<10}{initial_str:<10}{final_str:<10}\n')

            f_delta = filter_delta(delta, start=state)

            for _, trans in f_delta.iterrows():
                event = trans["transition"]

                e_label = event.label

                e_dict = event_dict[event]

                c_value = e_dict["isControllable"]
                o_value = e_dict["isObservable"]
                f_value = e_dict["isFault"]

                state = trans["end"]
                s_label = state.label

                f.write(f'{e_label:<10}{s_label:<10}{c_value:<10}{o_value:<10}{f_value:<10}\n')

            f.write("\n")
