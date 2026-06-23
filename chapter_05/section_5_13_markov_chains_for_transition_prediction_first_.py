"""
Code the Jackpot - 5.13 Markov Chains for Transition Prediction – first-order, single column
Auto-extracted (book order). Full listings, nothing truncated.
"""


# ======================================================================
# 5.13.2 Predicting from the last state: last_state_markov_prediction
# ======================================================================

def last_state_markov_prediction(data, column_name, n_predictions=5):
    """
    Generates a Markov Chain transition matrix for a specified column and predicts the
    top n most probable next states for the last observed state in the column.

    Parameters:
        data (DataFrame): The dataset containing the column of interest.
        column_name (str): The name of the column to analyse with a Markov Chain.
        n_predictions (int): Number of most probable predictions to return for the last state.

    Returns:
        list: A list of the top n predictions for the last observed state.
    """
    # Extract the specified column
    series = data[column_name].dropna().astype(int)

    # Get unique states in the column
    states = series.unique()

    # Build a transition matrix for the column (counts)
    transition_matrix = pd.DataFrame(0, index=states, columns=states)

    # Populate the transition matrix with counts
    for (current, nxt) in zip(series[:-1], series[1:]):
        transition_matrix.loc[current, nxt] += 1

    # Convert counts to probabilities row-wise
    transition_matrix = transition_matrix.div(
        transition_matrix.sum(axis=1), axis=0
    ).fillna(0)

    # Get the last observed state
    last_state = series.iloc[-1]

    # Generate predictions for the last state
    probable_states = transition_matrix.loc[last_state].nlargest(n_predictions)
    top_predictions = probable_states[probable_states > 0].index.tolist()

    return top_predictions

last_state_predictions = last_state_markov_prediction(df_n, 'st1', n_predictions=10)print(last_state_predictions)


# ======================================================================
# 5.13.3 Rolling backtest: backtest_markov_chain
# ======================================================================

def backtest_markov_chain(data, col, start_row=100, n_predictions=10):
    """
    Perform a backtest on the Markov Chain for a given column starting from the specified row.
    Records the predictions and actual outcomes for each step.

    Parameters:
        data (DataFrame): The dataset containing the column of interest.
        col (str): The column name to analyse.
        start_row (int): The row index to start the backtest from.
        n_predictions (int): Number of most probable predictions to use.

    Returns:
        DataFrame: A DataFrame with columns:
                   'current_state', 'predictions',
                   'actual_next_value', 'is_in_predictions'.
    """
    results = []

    # Loop through each row starting from start_row
    for i in range(start_row, len(data) - 1):
        # Use history up to i (inclusive) to build the transition matrix
        series_subset = data[col][:i + 1].astype(int)

        # States and empty transition matrix
        states = series_subset.unique()
        transition_matrix_subset = pd.DataFrame(0, index=states, columns=states)

        # Populate the transition matrix for the subset
        for (current, nxt) in zip(series_subset[:-1], series_subset[1:]):
            transition_matrix_subset.loc[current, nxt] += 1

        # Convert counts to probabilities
        transition_matrix_subset = transition_matrix_subset.div(
            transition_matrix_subset.sum(axis=1), axis=0
        ).fillna(0)

        # Current state is the last value in the subset
        current_state = series_subset.iloc[-1]

        # Predict the top N most probable next states
        probable_states = transition_matrix_subset.loc[current_state].nlargest(
            n_predictions
        )
        top_predictions = probable_states[probable_states > 0].index.tolist()

        # Actual next value (row i+1)
        actual_next_value = data[col].iloc[i + 1]

        # Did we catch it?
        is_in_predictions = actual_next_value in top_predictions

        # Store the result
        results.append({
            'current_state': current_state,
            'predictions': top_predictions,
            'actual_next_value': actual_next_value,
            'is_in_predictions': is_in_predictions,
        })

    results_df = pd.DataFrame(results)
    return results_df

backtest_results = backtest_markov_chain(    df_n,    col='st1',    start_row=len(df_n) - 300,    n_predictions=10)hit_rate = backtest_results['is_in_predictions'].value_counts() / len(backtest_results)print(hit_rate)
