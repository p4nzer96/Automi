def get_reachability_info(fsa_obj, set_fsa=True):
    reachable_states = []  # List of reachable states

    try:
        initial_state = fsa_obj.x0[0]  # take the first initial state
    except IndexError:
        raise Exception("FSA has not initial state")

    end_algorithm_flag = 0
    reachable_states.append(initial_state)

    states_pool = [initial_state]  # States to analyze

    # check if x0 is not connected to any transitions
    out_transitions = fsa_obj.filter_delta(start=initial_state)

    if len(out_transitions) == 0:
        end_algorithm_flag = 1

    while end_algorithm_flag == 0:
        for x_state in states_pool:
            out_transitions = fsa_obj.filter_delta(start=x_state)  # Compute the out transition from the state
            for _, start_state in out_transitions.iterrows():

                end_state = start_state.end  # Get the "end state" from the current out transition

                if end_state not in reachable_states:  # If "end state" is not in reachable states list...
                    reachable_states.append(end_state)  # ...add it to the reachable states
                    states_pool.append(end_state)  # ... add it to the pool

            states_pool.remove(x_state)  # Remove the current state from pool

            # If the pool is empty, end the algorithm
            if len(states_pool) == 0:
                end_algorithm_flag = 1

        # Check the reachable states
    for x_states in fsa_obj.X:

        if x_states in reachable_states:
            x_states.is_Reachable = True

        else:
            x_states.is_Reachable = False

    # If all states are reachable, also the FSA is reachable
    is_reachable = all([x.is_Reachable for x in fsa_obj.X])

    # If set_fsa is True, write the reachability parameter into the fsa object
    if set_fsa is True:
        fsa_obj.is_Reachable = is_reachable

    return is_reachable, reachable_states


def get_co_reachability_info(fsa_obj, set_fsa=True):
    co_reachable_states = []  # List of co-reachable states
    final_states = []

    for x in fsa_obj.Xm:
        final_states.append(x)
        co_reachable_states.append(x)  # All final states are co-reachable
    end_algorithm_flag = 0

    states_pool = []  # States to analyze
    states_pool.extend(final_states)  # Add the final states to the pool of states

    # Check if there are no final states
    if len(fsa_obj.Xm) == 0:
        # Set all states to no co-reachable
        for x in fsa_obj.X:
            x.is_co_Reachable = False
        end_algorithm_flag = 1

    while end_algorithm_flag == 0:

        # For state in current end states list
        for x_state in states_pool:

            # List all transitions
            out_transitions = fsa_obj.filter_delta(end=x_state)

            # for each "end state" in transitions
            for _, end_state in out_transitions.iterrows():

                # Get the "start state"
                start_state = end_state.start

                # If "start state" is not in co-reachable states list
                if start_state not in co_reachable_states:
                    co_reachable_states.append(start_state)  # ...add it to the list
                    states_pool.append(start_state)  # ...add it to the pool

            states_pool.remove(x_state)  # Remove the current state from the pool
            if len(states_pool) == 0:
                end_algorithm_flag = 1

    # Set the co-reachability property

    for x_state in fsa_obj.X:

        if x_state in co_reachable_states:
            x_state.is_co_Reachable = True

        else:
            x_state.is_co_Reachable = False

    is_co_reachable = all([x.is_co_Reachable for x in fsa_obj.X])

    if set_fsa is True:
        fsa_obj.is_co_Reachable = is_co_reachable

    return is_co_reachable, co_reachable_states


def get_blockingness_info(fsa_obj, set_fsa=True):
    # Check if Reachable and Co-Reachable properties are set

    if fsa_obj.is_Reachable is None:
        get_reachability_info(fsa_obj)

    if fsa_obj.is_co_Reachable is None:
        get_co_reachability_info(fsa_obj)

    fsa_obj.is_Blocking = False

    for x_state in fsa_obj.X:

        if x_state.is_Reachable is True and x_state.is_co_Reachable is False:
            x_state.is_Blocking = True
        else:
            x_state.is_Blocking = False

    is_blocking = any([x.is_Blocking for x in fsa_obj.X]) is True

    if set_fsa is True:
        fsa_obj.is_Blocking = is_blocking

    return is_blocking, [x for x in fsa_obj.X if x.is_Blocking]


def get_trim_info(fsa_obj, set_fsa=True):
    # Check if Reachable and Co-Reachable properties are set

    if fsa_obj.is_Reachable is None:
        get_reachability_info(fsa_obj)
    if fsa_obj.is_co_Reachable is None:
        get_co_reachability_info(fsa_obj)

    if fsa_obj.is_Reachable is True and fsa_obj.is_co_Reachable is True:
        is_trim = True
    else:
        is_trim = False

    if set_fsa is True:
        fsa_obj.is_Trim = is_trim

    return is_trim


def get_deadness_info(fsa_obj):
    dead_states = []

    for x_state in fsa_obj.X:
        current_deltas = fsa_obj.filter_delta(start=x_state.label)

        if len(current_deltas) != 0:
            x_state.is_Dead = False
        else:
            x_state.is_Dead = True
            dead_states.append(x_state)

    return [x for x in fsa_obj.X if x.is_Dead is True]


def get_co_reachability_to_x0_info(fsa_obj):
    co_reachable_to_x0_states = []  # List of co-reachable states
    final_states = []

    for x in fsa_obj.x0:
        final_states.append(x)
        co_reachable_to_x0_states.append(x)  # All final states are co-reachable
    end_algorithm_flag = 0

    states_pool = []  # States to analyze
    states_pool.extend(final_states)  # Add the final states to the pool of states

    # Check if there are no final states
    if len(fsa_obj.Xm) == 0:
        # Set all states to no co-reachable
        for x in fsa_obj.X:
            x.is_co_Reachable_to_x0 = False
        end_algorithm_flag = 1

    while end_algorithm_flag == 0:

        # For state in current end states list
        for x_state in states_pool:

            # List all transitions
            out_transitions = fsa_obj.filter_delta(end=x_state)

            # for each "end state" in transitions
            for _, end_state in out_transitions.iterrows():

                # Get the "start state"
                start_state = end_state.start

                # If "start state" is not in co-reachable states list
                if start_state not in co_reachable_to_x0_states:
                    co_reachable_to_x0_states.append(start_state)  # ...add it to the list
                    states_pool.append(start_state)  # ...add it to the pool

            states_pool.remove(x_state)  # Remove the current state from the pool
            if len(states_pool) == 0:
                end_algorithm_flag = 1

    # Set the co-reachability property

    for x_state in fsa_obj.X:

        if x_state in co_reachable_to_x0_states:
            x_state.is_co_Reachable_to_x0 = True

        else:
            x_state.is_co_Reachable_to_x0 = False


def get_reversibility_info(fsa_obj, set_fsa=True):
    if fsa_obj.is_Reachable is None:
        get_reachability_info(fsa_obj)

    if any([x.is_co_Reachable_to_x0 is None for x in fsa_obj.X]):
        get_co_reachability_to_x0_info(fsa_obj)

    is_reversible = None

    for x_state in fsa_obj.X:
        if x_state.is_Reachable:
            if not x_state.is_co_Reachable_to_x0:
                is_reversible = False
                break
            else:
                is_reversible = True

    if set_fsa is True:
        fsa_obj.is_Reversible = is_reversible

    return is_reversible
