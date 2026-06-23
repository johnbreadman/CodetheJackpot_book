"""
Code the Jackpot - 5.5 The Hits with the 20 Previous Draws
Auto-extracted (book order). Full listings, nothing truncated.
"""


# ======================================================================
# 5.5 The Hits with the 20 Previous Draws
# ======================================================================

def co_common(st1, st2):
    """Number of common values between two 5-number rows."""
    return len(set(st1).intersection(set(st2)))

def rebuild_x_columns_hist(df_cols):
    """Rebuild x1..x20 for the historical draws dataframe.

    df_cols must contain columns 'st1'..'st5'.
    """
    for i in range(1, 21):
        df_cols[f'x{i}'] = [0] * i + [
            co_common(
                df_cols.loc[j, 'st1':'st5'],
                df_cols.loc[j - i, 'st1':'st5']
            )
            for j in range(i, len(df_cols))
        ]


def update_x_columns_total(df):
    """Shift x-columns one step to the right and recompute x1.

    df must contain 'st1'..'st5' and x1..x20 columns.
    """
    last = df.loc[len(df) - 1:, 'st1':'st5'].values.tolist()[0]

    # Shift x20 <- x19 <- ... <- x1
    for i in range(20, 1, -1):
        df[f'x{i}'] = df[f'x{i-1}']

    # Fresh x1 against the latest draw
    df['x1'] = [
        co_common(df.loc[j, 'st1':'st5'], last)
        for j in range(len(df))
    ]


def add_x_small_counts(df):
    x_cols = [f'x{i}' for i in range(1, 21)]

    # Count 0s, 1s, 2s across x1..x20
    df['0s'] = (df[x_cols] == 0).sum(axis=1)
    df['1s'] = (df[x_cols] == 1).sum(axis=1)
    df['2s'] = (df[x_cols] == 2).sum(axis=1)

    # How many x-columns are in {0,1,2}
    mask_small = df[x_cols].isin([0, 1, 2])
    df['20'] = mask_small.sum(axis=1)


def add_x_sums(df):
    cols_all = [f'x{i}' for i in range(1, 21)]
    df['x_sum'] = df[cols_all].sum(axis=1)

    cols_5 = [f'x{i}' for i in range(1, 6)]
    df['x_sum5'] = df[cols_5].sum(axis=1)

    cols_10 = [f'x{i}' for i in range(6, 11)]
    df['x_sum10'] = df[cols_10].sum(axis=1)

    cols_15 = [f'x{i}' for i in range(11, 16)]
    df['x_sum15'] = df[cols_15].sum(axis=1)

    cols_20 = [f'x{i}' for i in range(16, 21)]
    df['x_sum20'] = df[cols_20].sum(axis=1)


# ======================================================================
# Approach A: gap statistics for short xi patterns
# ======================================================================

from scipy import stats
import numpy as np
import pandas as pd

def calculate_column_statistics(df, target_columns):
    """
    Compute gap-based statistics for all unique value combinations
    across the given target_columns.
    """
    value_combinations = df[target_columns].apply(tuple, axis=1)
    unique_combinations = value_combinations.unique()

    statistics_results = pd.DataFrame()

    for combination in unique_combinations:
        indices = value_combinations[value_combinations == combination].index.tolist()

        # Gaps between hits of this combination, plus head and tail
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

    # Normalize by frequency and combine into a product score
    statistics_results['normalized_frequency'] = (
        100 * statistics_results['frequency'] / statistics_results['frequency'].sum()
    ).round(2)
    statistics_results['product_score'] = (
        statistics_results['normalized_frequency'] *
        statistics_results['percentile_score']
    ).round(2)

    statistics_results.sort_values(
        by='product_score', ascending=False, inplace=True
    )
    statistics_results.reset_index(drop=True, inplace=True)

    return statistics_results


# ======================================================================
# Approach B: working with the five x-sum blocks
# ======================================================================

def filter_bandA_and_no_heavy_overlaps(df):
    x_cols = [f'x{i}' for i in range(1, 21)]

    # Keep only rows with '20' in {19, 20}
    mask_bandA = df['20'].isin([19, 20])

    # Reject any row with xi >= 4
    mask_no_heavy = (df[x_cols].max(axis=1) <= 3)

    return df[mask_bandA & mask_no_heavy]


# ======================================================================
# Worked Example: Greedy Selection of "Cold" xi Columns
# ======================================================================

import pandas as pd
import numpy as np

# Load the dataset
df = pd.read_csv('data/total_nikstiles.csv', index_col=0)  # Skip header row
df = df[20:]  # Start from row 20 (21st draw)

# Extract x1-x20 columns
x_cols = [f'x{i}' for i in range(1, 21)]
x_data = df[x_cols].apply(pd.to_numeric, errors='coerce').astype(int)

# Calculate zero frequency for individual columns
zero_counts = (x_data <= 0).sum()
print("Individual zero frequencies:")
print(zero_counts.sort_values(ascending=False))
print("\n" + "-"*50 + "\n")

# Find best combination using greedy approach
selected_columns = []
remaining_columns = x_cols.copy()
current_data = x_data.copy()

val = 0  # this can be 0, 1, 2

for i in range(1, 7):
    best_col = None
    best_zeros = -1

    # Track progress
    print(f"Selecting column #{i}:")

    for col in remaining_columns:
        # Calculate zero frequency with current selection
        if selected_columns:
            temp_cols = selected_columns + [col]
            zero_freq = (current_data[temp_cols] <= val).all(axis=1).sum()
        else:
            zero_freq = (current_data[col] <= val).sum()

        print(f"- {col}: {zero_freq} rows with all <={val}")

        if zero_freq > best_zeros:
            best_zeros = zero_freq
            best_col = col

    selected_columns.append(best_col)
    remaining_columns.remove(best_col)

    # Filter to rows where all selected columns are <= val
    current_data = current_data[current_data[selected_columns].le(val).all(axis=1)]

    print(f"SELECTED: {best_col} ({best_zeros} rows)")
    print(f"Remaining rows: {len(current_data)}")
    print("-"*50)

print("\nFinal selected columns:")
print(selected_columns)


# ======================================================================
# What this script does
# ======================================================================

Individual zero frequencies:
x20    528
x17    526
x9     521
x12    521
x4     520
x15    519
x11    517
x1     516
x14    514
x16    514
x18    514
x2     512
x3     512
x10    508
x8     507
x13    506
x7     503
x6     502
x5     491
x19    489
dtype: int64


Selecting column #1:
...
SELECTED: x20 (528 rows)
Remaining rows: 528
--------------------------------------------------
Selecting column #2:
...
SELECTED: x4 (313 rows)
Remaining rows: 313
--------------------------------------------------
Selecting column #3:
...
SELECTED: x15 (194 rows)
Remaining rows: 194
--------------------------------------------------
Selecting column #4:
...
SELECTED: x19 (122 rows)
Remaining rows: 122
--------------------------------------------------
Selecting column #5:
...
SELECTED: x10 (80 rows)
Remaining rows: 80
--------------------------------------------------
Selecting column #6:
...
SELECTED: x7 (52 rows)
Remaining rows: 52
--------------------------------------------------

Final selected columns:
['x20', 'x4', 'x15', 'x19', 'x10', 'x7']
