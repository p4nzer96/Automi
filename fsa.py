import json
import pandas as pd
from event import Event
from state import State


class FSA:

    def __init__(self, X=None, E=None, delta=None, x0=None, Xm=None) -> None:

        self.X = X  # States
        self.E = E  # Alphabet
        self.delta = delta  # Delta relation
        self.x0 = x0  # Initial states
        self.Xm = Xm  # Final states

    @classmethod
    def fromfile(cls, filename):

        # Load from file

        X = []  # States
        E = []  # Alphabet
        x0 = []  # Initial states
        Xm = []  # Final states

        # File opening

        with open(filename) as jsonFile:
            jsonObject = json.load(jsonFile)

        # Reading states and properties

        for key in jsonObject['X']:
            st_label = key  # State name

            if 'isInit' in jsonObject['X'][key]:
                isInit = eval(jsonObject['X'][key]['isInit'])  # Is the state initial?
            else:
                isInit = None
            if 'isFinal' in jsonObject['X'][key]:
                isFinal = eval(jsonObject['X'][key]['isFinal'])  # Is the state final?
            else:
                isFinal = None

            state = State(st_label, bool(isInit), bool(isFinal))

            if isInit:  # If the state is initial, add it to initial states
                x0.append(state)

            if isFinal:  # If the state is final, add it to final states
                Xm.append(state)
            X.append(state)

        # Reading events and properties

        for key in jsonObject['E']:
            ev_label = key  # Event name

            if 'isObservable' in jsonObject['E'][key]:
                observable = eval(jsonObject['E'][key]['isObservable'])  # Is observable?
            else:
                observable = None
            if 'isControllable' in jsonObject['E'][key]:
                controllable = eval(jsonObject['E'][key]['isControllable'])  # Is controllable?
            else:
                controllable = None
            if 'isFaulty' in jsonObject['E'][key]:
                fault = eval(jsonObject['E'][key]['isFault'])  # Is faulty?
            else:
                fault = None

            E.append(Event(ev_label, bool(observable), controllable, fault))

        data = []

        # Reading delta

        for key in jsonObject['delta']:

            start_state = jsonObject['delta'][key]['start']  # Start state

            if start_state not in [s.label for s in X]:  # Check if start state is in X
                raise ValueError("Invalid start state")

            transition = jsonObject['delta'][key]['name']  # Transition

            if transition not in [e.label for e in E]:  # Check if transition is in E
                raise ValueError("Invalid event")

            end_state = jsonObject['delta'][key]['ends']

            if end_state not in [s.label for s in X]:  # Check if end state is in X
                raise ValueError("Invalid end state")

            data.append([start_state, transition, end_state])

        delta = pd.DataFrame(data, columns=["start", "transition", "end"])

        return cls(X, E, delta, x0, Xm)

    def print_X(self):

        states = [x.label for x in self.X]
        print(states)

    def print_E(self):

        events = [x.label for x in self.E]
        print(events)

    def print_delta(self):

        print(self.delta)

    def filter_delta(self, start=None, transition=None, end=None):
        
        if start:
            filt_delta = self.delta.loc[(self.delta["start"] == start)]

        if start:
            filt_delta = self.delta.loc[(self.delta["transition"] == transition)]

        if end:
            filt_delta = self.delta.loc[(self.delta["end"] == end)]

        return filt_delta

    def print_x0(self):

        in_states = [x.label for x in self.x0]
        print(in_states)

    def print_Xm(self):

        fin_states = [x.label for x in self.Xm]
        print(fin_states)

    def add_state(self, state, isInitial=None, isFinal=None):

        if isinstance(state, State):

            if state.label not in [x.label for x in self.X]:

                self.X.append(state)

                if state.isFinal:
                    self.Xm.append(state)

                if state.isInitial:
                    self.x0.append(state)

            else:

                print("Error: We cannot have two states with the same label")
                return

        elif isinstance(state, str):

            if state not in [x.label for x in self.X]:

                new_state = State(state, isInitial, isFinal)

                self.X.append(new_state)

                if new_state.isFinal:
                    self.Xm.append(new_state)

                if new_state.isInitial:
                    self.x0.append(new_state)

            else:

                print("Error: We cannot have two states with the same label")
                return

        else:

            raise ValueError

    def add_event(self, event, isObservable=None, isControllable=None, isFault=None):

        if isinstance(event, Event):

            if event not in [e.label for e in self.E]:

                self.E.append(event)

            else:

                print("Error: We cannot have two states with the same label")
                return

        elif isinstance(event, str):

            if event not in [x.label for x in self.E]:

                new_event = Event(event, isObservable, isControllable, isFault)

                self.E.append(new_event)

            else:

                print("Error: We cannot have two states with the same label")
                return

        else:

            raise ValueError
