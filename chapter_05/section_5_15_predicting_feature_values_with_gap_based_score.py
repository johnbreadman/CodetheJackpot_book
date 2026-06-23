"""
Code the Jackpot - 5.15 Predicting Feature Values with Gap-Based Scores
Auto-extracted (book order). Full listings, nothing truncated.
"""


# ======================================================================
# Building prediction lists per feature
# ======================================================================
pred_dict_all = {}
for col in cols:
    stats_df = calculate_column_statistics(df2, [col])
    top_states = stats_df['combination'][:cols[col]]
    pred_dict_all[col] = [tpl[0] for tpl in top_states]


# ======================================================================
# Code listing
# ======================================================================
import numpy as np
import pandas as pd
from scipy import stats

def calculate_column_statistics(df, target_columns):
    """
    Compute statistical insights for all unique combinations of values across specified columns.
    In this book we call it once per feature column.
    """
    # Extract tuples of values from the specified columns
    value_combinations = df[target_columns].apply(tuple, axis=1)
    unique_combinations = value_combinations.unique()

    # Dictionary to store indices for each unique combination
    combination_indices = {
        combination: value_combinations[value_combinations == combination].index.tolist()
        for combination in unique_combinations
    }

    # Initialize a DataFrame to store the statistical results
    statistics_results = pd.DataFrame()

    # Compute statistics for each unique combination
    for combination, indices in combination_indices.items():
        index_differences = (
            [indices[0]] +
            [indices[i] - indices[i - 1] for i in range(1, len(indices))] +
            [len(df) - indices[-1]]
        )

        stats_dict = {
            'combination': combination,
            'frequency': len(indices),
            'last_gap': index_differences[-1],
            'median_gap': int(np.percentile(index_differences, 50)),
            'p75_gap': int(np.percentile(index_differences, 75)),
            'p90_gap': int(np.percentile(index_differences, 90)),
            'p95_gap': int(np.percentile(index_differences, 95)),
            'p99_gap': int(np.percentile(index_differences, 99)),
            'max_gap': int(np.max(index_differences)),
            'percentile_score': int(
                stats.percentileofscore(index_differences, index_differences[-1])
            ),
        }

        statistics_results = pd.concat(
            [statistics_results, pd.DataFrame([stats_dict])],
            ignore_index=True
        )

    # Normalise frequency and compute product scores
    statistics_results['normalized_frequency'] = (
        100 * statistics_results['frequency'] / statistics_results['frequency'].sum()
    ).round(2)

    statistics_results['product_score'] = (
        statistics_results['normalized_frequency'] *
        statistics_results['percentile_score']
    ).round(2)

    # Sort by product score and reset index
    statistics_results.sort_values(by='product_score', ascending=False, inplace=True)
    statistics_results.reset_index(drop=True, inplace=True)

    return statistics_results


# How many states to keep per feature column
cols = {
    'st1': 13, 'st2': 13, 'st3': 13, 'st4': 13, 'st5': 13,
    'E3': 7, 'E4': 2,
    'Odd': 4, 'Small': 4,
    'Lines': 3, 'Cols': 3,
    'Syn': 2, 'OSLCS': 20,
    'L1': 3, 'L2': 3, 'L3': 3, 'L4': 3, 'L5': 3, 'L6': 3, 'L7': 3, 'L8': 3, 'L9': 3, 'L10': 3,
    'LL': 20,
    'C1': 3, 'C2': 3, 'C3': 3, 'C4': 3, 'C5': 3,
    'CC': 20,
    'SD': 3,
    'xD1': 2, 'xD2': 3, 'xD3': 3, 'xD4': 3, 'xD5': 3, 'xD6': 3, 'xD7': 3, 'xD8': 3, 'xD9': 3,
    'xD10': 2, 'xD11': 2, 'xD12': 2, 'xD13': 2,
    'D1': 13, 'D2': 13, 'D3': 13, 'D4': 13,
    'D<=10': 3, 'D<=20': 2,
    'AC': 3, 'sameDs': 2, 'last6': 4,
    'x1': 2, 'x2': 2, 'x3': 2, 'x4': 2, 'x5': 2, 'x6': 2, 'x7': 2, 'x8': 2, 'x9': 2, 'x10': 2,
    'x11': 2, 'x12': 2, 'x13': 2, 'x14': 2, 'x15': 2, 'x16': 2, 'x17': 2, 'x18': 2, 'x19': 2, 'x20': 2,
    '0s': 8, '1s': 7, '2s': 4, '20': 2,
    'triades': 5,
    'k1': 13, 'k2': 13, 'k3': 13, 'k4': 13, 'k5': 13,
    'N1': 3, 'N2': 3, 'N3': 3, 'N4': 3, 'N5': 3,
    'NB1': 4, 'NB2': 4, 'NB3': 4, 'NB4': 4, 'NB': 20,
    'combist1': 13, 'combist2': 13, 'combist3': 13, 'combist4': 13, 'combist5': 13,
    'n10000': 7, 'pattern': 6, 'stidx': 20
}


# Build the prediction dictionary from df2 (hist_df.copy())
pred_dict_all = {}
for col in cols:
    stats_df = calculate_column_statistics(df2, [col])
    top_states = stats_df['combination'][:cols[col]]
    pred_dict_all[col] = [tpl[0] for tpl in top_states]
