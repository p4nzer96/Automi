import json
import pandas as pd
from fsatoolbox import event, state
from fsatoolbox.utils import load_module
from fsatoolbox.utils.filter_delta import filter_delta
from fsatoolbox.utils.show_module import show_full, show_comp
from fsatoolbox.utils.write_module import save_txt, save_json


class StateNotFoundExc(Exception):
    pass


class EventNotFoundExc(Exception):
    pass


class TransitionNotFoundExc(Exception):
    pass


class fsa:
    """
    Class used to represent a Finite State Automaton (FSA)

    Parameters
    ----------
    X : list of State objects
        the set of states of which the automaton is composed
    E : list of event objects
        the alphabet of the automaton
    delta : DataFrame
        the transition relation / function of the automaton
    """

    def __init__(self, X=None, E=None, delta=pd.DataFrame(columns=["start", "transition", "end"]),
                 **kwargs) -> None:

        self._X = X if X else []  # States
        self._E = E if E else []  # Alphabet
        self._delta = delta  # Delta relation
        self._x0 = []  # Initial states
        self._Xm = []  # Final states

        self._update_fsa()  # Init fsa (set final and initial states)

        # Optional: Name of the FSA

        self._name = kwargs.get('name') if kwargs.get('name') else object.__repr__(self)

        # FSA properties

        self.is_Reachable = None
        self.is_co_Reachable = None
        self.is_Blocking = None
        self.is_Trim = None
        self.is_Reversible = None

    def __repr__(self):

        rep = "\nFSA: " + self._name + "\n" + self.showfsa()
        return rep

    @property
    def X(self):
        return self._X

    @X.setter
    def X(self, value):
        for x in value:
            if x in self._X:
                self.add_state(x)
            else:
                self.remove_state(x)

    @property
    def E(self):
        return self._E

    @E.setter
    def E(self, value):
        for e in value:
            if e not in self._E:
                self.add_event(e)
            else:
                self.remove_event(e)

    @property
    def delta(self):
        return self._delta

    @delta.setter
    def delta(self, value):
        self._delta = value

    @property
    def x0(self):
        return self._x0

    @property
    def Xm(self):
        return self._Xm

    @classmethod
    def from_file(cls, filename, **kwargs):

        """
        Generates a FSA from file

        Args:
            filename (str): the path of the .json file containing the definition of the FSA


        Returns:
            fsa: An instance of FSA

        """

        # Load from file

        X = []  # States
        E = []  # Alphabet
        x0 = []  # Initial states
        Xm = []  # Final states

        # File opening

        jsonObject = load_module.loadfile(filename)

        if jsonObject is None:
            raise TypeError

        # Reading states and properties

        state_properties = {"isInitial": None, "isFinal": None}

        for state_name in jsonObject['X']:
            for prop in state_properties.keys():

                if prop in jsonObject['X'][state_name]:
                    state_properties[prop] = jsonObject['X'][state_name][prop]

            # Creating the state
            State = state(state_name,
                          state_properties["isInitial"],
                          state_properties["isFinal"])

            if state_properties["isInitial"]:  # If the state is initial, add it to initial states
                x0.append(State)

            if state_properties["isFinal"]:  # If the state is final, add it to final states
                Xm.append(State)

            # Add the state to X
            X.append(State)

        event_properties = {"isObservable": None, "isControllable": None, "isFault": None}

        # Reading events and properties

        for event_name in jsonObject['E']:
            for prop in event_properties.keys():
                if prop in jsonObject['E'][event_name]:
                    event_properties[prop] = jsonObject['E'][event_name][prop]  # Is observable?

            # Creating the event
            Event = event(event_name,
                          event_properties["isObservable"],
                          event_properties["isControllable"],
                          event_properties["isFault"])

            E.append(Event)

        data = []

        # Reading delta

        for key in jsonObject['delta']:

            start_state = jsonObject['delta'][key]['start']  # Start state

            if start_state not in [s.label for s in X]:  # Check if start state is in X
                raise ValueError("Invalid start state")

            else:

                idx = [x.label for x in X].index(start_state)
                i_state = X[idx]

            transition = jsonObject['delta'][key]['event']  # Transition

            if transition not in [e.label for e in E]:  # Check if transition is in E
                raise ValueError("Invalid event")

            else:

                idx = [x.label for x in E].index(transition)
                trans = E[idx]

            end_state = jsonObject['delta'][key]['end']

            if end_state not in [s.label for s in X]:  # Check if end state is in X
                raise ValueError("Invalid end state")

            else:

                idx = [x.label for x in X].index(end_state)
                f_state = X[idx]

            data.append([i_state, trans, f_state])

        delta = pd.DataFrame(data, columns=["start", "transition", "end"])

        if kwargs.get("name"):
            fsa_name = kwargs.get("name")
            return cls(X, E, delta, name=fsa_name)

        return cls(X, E, delta)

    def to_file(self, filename):

        if filename[-4:].lower() == ".txt":
            save_txt(filename, self.X, self.E, self.delta)
        elif filename[-5:].lower() == ".json":
            save_json(filename, self.X, self.E, self.delta)
        else:
            print("Unspecified file type: default saving to json")
            save_json(filename, self.X, self.E, self.delta)

    def showfsa(self, style=1):

        """
        Shows a graphical representation of the FSA

        Returns:
            str: String that show the fsa structure

        """

        if style == 0:
            text = show_full(self._X, self._E, self._delta)
        elif style == 1:
            text = show_comp(self._X, self._E, self._delta)
        else:
            raise ValueError

        return text

    def filter_delta(self, start=None, transition=None, end=None):
        """
        Filters the delta by starting state, transition or ending state

        Args:
            start (state, optional): starting state. Defaults to None.
            transition (Event, optional): transition event. Defaults to None.
            end (Event, optional): ending state. Defaults to None.

        Returns:
            DataFrame: Filtered delta according to filter passed as argument of the function
        """

        return filter_delta(self.delta, start, transition, end)

    def add_state(self, new_state, isInitial=None, isFinal=None, isForbidden=None):

        """
        Adds a state to the FSA

        Args:
            new_state (state): The new state to be added
            isInitial (bool, optional): determines if the state is initial
            isFinal (bool, optional): determines if the state is final
            isForbidden(bool, optional): determines if the state is forbidden
        """

        self._update_fsa()

        if isinstance(new_state, state):  # if state is an instance of state

            if new_state not in self.X:

                self.X.append(new_state)

                if new_state.isFinal:
                    self.Xm.append(new_state)

                if new_state.isInitial:
                    self.x0.append(new_state)

            else:

                print("Error: We cannot have two states with the same label")
                return

        elif isinstance(new_state, str):  # if state is a string

            if new_state not in [x.label for x in self.X]:

                new_state = state(new_state, isInitial, isFinal, isForbidden)
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

    def remove_state(self, fsa_state):
        """
        Removes a state or a list of states from the FSA
        Args:
            fsa_state (state): state/s to remove
        """

        fsa_state = self._state_parser(fsa_state)

        if fsa_state is None or fsa_state not in self.X:
            raise StateNotFoundExc("Error: state not in X")

        for x in self._X:
            if x == fsa_state:
                self._X.remove(x)

        if not self._delta.empty:
            self._delta.drop(self.delta[((self._delta.start == fsa_state) |
                                         (self._delta.end == fsa_state))].index, inplace=True)

        self._update_fsa()

    def change_state_props(self, fsa_state, **kwargs):
        """
        Changes the properties of a state

        Args:
            state (state): state of which you want to change the properties
            **kwargs (): properties
        """

        fsa_state = self._state_parser(fsa_state)

        if fsa_state not in self._X:
            raise StateNotFoundExc(Exception)

        for prop in kwargs.keys():
            setattr(fsa_state, prop, kwargs[prop])

        self._update_fsa()

    def add_event(self, new_event, isObservable=None, isControllable=None, isFault=None):
        """
        Adds an event to the FSA

        Args:
            new_event (event): Event to be added to the FSA
            isObservable (bool, optional): Specifies if the event is observable. Defaults to None
            isControllable (bool, optional): Specifies if the event is controllable. Defaults to None
            isFault (bool, optional): Specifies if the event is aa fault event. Defaults to None
        """

        if isinstance(new_event, event):  # if event is an instance of Event

            if new_event not in self.E:
                self.E.append(new_event)

            else:

                print("Error: We cannot have two events with the same label")
                return

        elif isinstance(new_event, str):  # if event is a string

            if new_event not in [x.label for x in self.E]:

                new_event = event(new_event, isObservable, isControllable, isFault)
                self.E.append(new_event)

            else:

                print("Error: We cannot have two events with the same label")
                return

        else:

            raise ValueError

    def remove_event(self, fsa_event):
        """
        Removes an event or a list of events from the FSA
        Args:
            fsa_event (event): event/S to remove
        """

        fsa_event = self._event_parser(fsa_event)

        if fsa_event is None or fsa_event not in self.E:
            raise EventNotFoundExc("Error: event not in alphabet")

        for e in self._E:
            if e == fsa_event:
                self._E.remove(e)

        if not self._delta.empty:
            self._delta.drop(self.delta[(self._delta.transition == fsa_event)], inplace=True)

        self._update_fsa()

    def change_event_props(self, fsa_event, **kwargs):
        """
        Changes the properties of an event

        Args:
            fsa_event (event): event of which you want to change the properties
            **kwargs (): properties
        """

        fsa_event = self._event_parser(fsa_event)

        if fsa_event not in self._E:
            raise EventNotFoundExc(Exception)

        for prop in kwargs.keys():
            setattr(fsa_event, prop, kwargs[prop])

        self._update_fsa()

    def add_transition(self, initial_state, tr_event, end_state):

        """
        Adds a transition to the delta relation/function

        Args:
            initial_state (state, optional): initial state
            tr_event (event, optional): transition
            end_state (state, optional): ending state
        """

        # Initial State

        try:

            if isinstance(initial_state, state):
                initial_state = initial_state.label

            idx = [x.label for x in self.X].index(initial_state)
            i_state = self.X[idx]

        except (ValueError, TypeError):

            print("Error: starting state not in X")
            return

        # Transition

        try:

            if isinstance(tr_event, event):
                tr_event = tr_event.label

            idx = [e.label for e in self.E].index(tr_event)
            transition = self.E[idx]

        except (ValueError, TypeError):

            print("Error: event not in E")
            return

        # Final State

        try:

            if isinstance(end_state, state):
                end_state = end_state.label

            idx = [x.label for x in self.X].index(end_state)
            e_state = self.X[idx]

        except (ValueError, TypeError):

            print("Error: end state not in X")
            return

        temp_df = pd.DataFrame([[i_state, transition, e_state]], columns=["start", "transition", "end"])
        self.delta = pd.concat([self.delta, temp_df], axis=0, ignore_index=True) \
            .drop_duplicates().reset_index(drop=True)

        self._update_fsa()

    def remove_transition(self, start, fsa_event, end):
        """
        Removes a transition to the delta relation/function

        Args:
            start (state, optional): initial state
            event (event, optional): transition
            end (state, optional): ending state
        """

        start = self._state_parser(start)
        fsa_event = self._event_parser(fsa_event)
        end = self._state_parser(end)

        transition = self.delta[((self._delta.start == start) &
                                 (self._delta.transition == fsa_event) &
                                 (self._delta.end == end))]

        if transition.empty:
            raise TransitionNotFoundExc("Error: transition not in delta")

        self._delta.drop(transition.index, inplace=True)

        self._update_fsa()

    # Internal Methods -------------------------------------------------------------

    def _state_parser(self, states: object):
        """
        Parse a state from string to the corresponding object
        Args:
            states (str): A string that represents a state
        Returns:
              Corresponding state object
        """
        if isinstance(states, list):
            parsed_states = []
            for x in states:
                if isinstance(x, state):
                    parsed_states.append(x)
                elif isinstance(x, str):
                    for fsa_x in self.X:
                        if x == fsa_x.label:
                            parsed_states.append(fsa_x)
                else:
                    raise TypeError
            return parsed_states
        elif isinstance(states, str):
            for fsa_x in self.X:
                if states == fsa_x.label:
                    return fsa_x
        elif isinstance(states, state):
            return states
        else:
            raise TypeError

    def _event_parser(self, events: object):
        """
        Parse a state from string to the corresponding object
        Args:
            events (str): A string that represents an event
        Returns:
            Corresponding event object
        """

        if isinstance(events, list):
            parsed_events = []
            for e in events:
                if isinstance(e, event):
                    parsed_events.append(e)
                elif isinstance(e, str):
                    for fsa_x in self.X:
                        if e == fsa_x.label:
                            parsed_events.append(fsa_x)
                else:
                    raise TypeError
            return parsed_events
        elif isinstance(events, str):
            for fsa_e in self.E:
                if events == fsa_e.label:
                    return fsa_e
        elif isinstance(events, event):
            return events
        else:
            raise TypeError

    def _update_fsa(self):
        """
        Refreshes FSA (updates states properties, x0 and Xm)
        """
        self._x0 = []
        for x in self._X:
            if x.isInitial is True:
                self._x0.append(x)

        self._Xm = []
        for x in self._X:
            if x.isFinal is True:
                self._Xm.append(x)

        self.is_Reachable = None
        self.is_co_Reachable = None
        self.is_Trim = None
        self.is_Blocking = None
        self.is_Reversible = None
