from pandas import DataFrame
from fsatoolbox import state, event


def filter_delta(delta: DataFrame, start=None, transition=None, end=None):
    filt_delta = delta

    if start:  # Starting fsa_state
        start = start.label if isinstance(start, state) else start  # If start is a State object, parse it
        condition = filt_delta["start"].apply(lambda x: x.label) == start
        filt_delta = filt_delta.loc[condition]

    if transition:  # Transition fsa_event
        transition = transition.label if isinstance(transition, event) else transition  # If transition is an Event
        # object, parse it
        condition = filt_delta["transition"].apply(lambda x: x.label) == transition
        filt_delta = filt_delta.loc[condition]

    if end:  # Ending fsa_state
        end = end.label if isinstance(end, state) else end  # If fsa_event is a fsa_state object, parse it
        condition = filt_delta["end"].apply(lambda x: x.label) == end
        filt_delta = filt_delta.loc[condition]

    return filt_delta
