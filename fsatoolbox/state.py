from dataclasses import dataclass


@dataclass
class state:
    label: str = None
    isInitial: bool = None
    isFinal: bool = None

    # Internal properties 

    is_Reachable: bool = None
    is_co_Reachable: bool = None
    is_Blocking: bool = None
    is_Dead: bool = None
    is_co_Reachable_to_x0: bool = None

    # Used for supervisory problems
    isForbidden: bool = None

    def __hash__(self):  # TODO: Improvement needed
        return hash(self.label)

    def __repr__(self):
        return self.label

    def __eq__(self, other):
        return self.label == other.label
