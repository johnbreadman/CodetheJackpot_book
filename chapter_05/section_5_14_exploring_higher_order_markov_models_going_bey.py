"""
Code the Jackpot - 5.14 Exploring Higher-Order Markov Models – going beyond and why that's risky
Auto-extracted (book order). Full listings, nothing truncated.
"""


# ======================================================================
# 5.14.1 Predicting from a sequence of length n
# ======================================================================

def last_state_higher_order_markov_prediction(
    data,
    column_name,
    n_predictions=5,
    order=1
):
    """
    Higher-order Markov prediction for a single column.

    Parameters:
        data (DataFrame): The dataset containing the column of interest.
        column_name (str): The name of the column to analyse.
        n_predictions (int): Number of most probable predictions to return.
        order (int): The order of the Markov Chain
                     (1 for first-order, 2 for second-order, etc.).

    Returns:
        list: A list of the top n predictions for the last observed sequence.
    """
    # Extract the specified column
    series = data[column_name].dropna().astype(int)

    # Transition counts: key = state tuple of length `order`
    transition_counts = {}

    # Walk through all possible state → next transitions
    for i in range(len(series) - order):
        current_state = tuple(series[i:i + order])
        next_state = series[i + order]

        if current_state not in transition_counts:
            transition_counts[current_state] = {}

        if next_state not in transition_counts[current_state]:
            transition_counts[current_state][next_state] = 0

        transition_counts[current_state][next_state] += 1

    # Convert counts to probabilities
    transition_probs = {
        state: {
            nxt: count / sum(next_states.values())
            for nxt, count in next_states.items()
        }
        for state, next_states in transition_counts.items()
    }

    # Last observed sequence of length `order`
    last_state = tuple(series.iloc[-order:])

    # Predictions for that sequence
    if last_state in transition_probs:
        probable_states = pd.Series(transition_probs[last_state]).nlargest(
            n_predictions
        )
        top_predictions = probable_states[probable_states > 0].index.tolist()
    else:
        # We have never seen this exact sequence before
        top_predictions = []

    return top_predictions

last_state_predictions_order_n = last_state_higher_order_markov_prediction(    df_n,    column_name='20',    n_predictions=1,    order=3)print(last_state_predictions_order_n)


# ======================================================================
# 5.14.2 Backtesting higher-order chains: backtest_higher_order_markov_chain
# ======================================================================

def backtest_higher_order_markov_chain(
    data,
    col,
    start_row=100,
    n_predictions=10,
    order=1
):
    """
    Backtest a higher-order Markov Chain for a given column.

    Parameters:
        data (DataFrame): The dataset containing the column of interest.
        col (str): The column to analyse.
        start_row (int): Row index to start the backtest from.
        n_predictions (int): Number of most probable predictions to use.
        order (int): The order of the Markov Chain.

    Returns:
        DataFrame: A DataFrame recording the backtest with columns:
                   'current_state', 'predictions',
                   'actual_next_value', 'is_in_predictions'.
    """
    results = []

    # Loop through each row starting from start_row
    for i in range(start_row, len(data) - 1):
        # Series up to current row
        series_subset = data[col][:i + 1].astype(int)

        # Transition counts for this subset
        transition_counts = {}

        for j in range(len(series_subset) - order):
            current_state = tuple(series_subset[j:j + order])
            next_state = series_subset[j + order]

            if current_state not in transition_counts:
                transition_counts[current_state] = {}

            if next_state not in transition_counts[current_state]:
                transition_counts[current_state][next_state] = 0

            transition_counts[current_state][next_state] += 1

        # Convert counts to probabilities
        transition_probs = {
            state: {
                nxt: count / sum(next_states.values())
                for nxt, count in next_states.items()
            }
            for state, next_states in transition_counts.items()
        }

        # Current state: last `order` elements
        current_state = tuple(series_subset.iloc[-order:])

        # Predict the top N next states
        if current_state in transition_probs:
            probable_states = pd.Series(
                transition_probs[current_state]
            ).nlargest(n_predictions)
            top_predictions = probable_states[probable_states > 0].index.tolist()
        else:
            top_predictions = []

        # Actual next value
        actual_next_value = data[col].iloc[i + 1]

        # Check if we caught it
        is_in_predictions = actual_next_value in top_predictions

        results.append({
            'current_state': current_state,
            'predictions': top_predictions,
            'actual_next_value': actual_next_value,
            'is_in_predictions': is_in_predictions,
        })

    results_df = pd.DataFrame(results)
    return results_df

backtest_results_order_n = backtest_higher_order_markov_chain(    df_n,    col='20',    start_row=len(df_n) - 500,    n_predictions=1,    order=3)hit_rate = backtest_results_order_n['is_in_predictions'].value_counts() / len(backtest_results_order_n)print(hit_rate)
