"""
Code the Jackpot - 5.11 Draws Since Last Hit – the delay engine
Auto-extracted (book order). Full listings, nothing truncated.
"""


# ======================================================================
# Building the delay engine in Python
# ======================================================================

import numpy as np
import pandas as pd


def compute_k_features(hist_df, st_cols=('st1', 'st2', 'st3', 'st4', 'st5')):
    """
    Add k-features to hist_df for a 5/50 lottery.

    For each draw i, the function records:

      k1..k5   : draws since last hit for each of the 5 numbers
                 (measured just before draw i)
      k_min    : minimum of these five delays
      k_max    : maximum delay
      k_mean   : average delay

    The internal K-array keeps track of the current delay K(n) for
    all 50 numbers between draws.
    """

    df = hist_df.copy()

    # One K-slot per number 1..50, index 0 -> number 1, ..., index 49 -> number 50
    # K[n-1] = draws since last hit for number n, before the current draw.
    K = np.zeros(50, dtype=int)

    # Prepare columns
    k_cols = [f'k{i}' for i in range(1, 6)]
    for col in k_cols + ['k_min', 'k_max', 'k_mean']:
        df[col] = np.nan

    # Walk through draws in time order
    for idx, row in df.iterrows():
        nums = row[list(st_cols)].astype(int).values

        # Record delays for the 5 numbers based on current K
        current_k_values = []
        for pos, n in enumerate(nums, start=1):
            delay = int(K[n - 1])
            df.at[idx, f'k{pos}'] = delay
            current_k_values.append(delay)

        # Summary stats for this draw
        k_min = int(min(current_k_values))
        k_max = int(max(current_k_values))
        k_mean = float(np.mean(current_k_values))

        df.at[idx, 'k_min'] = k_min
        df.at[idx, 'k_max'] = k_max
        df.at[idx, 'k_mean'] = k_mean

        # Update K for the next draw:
        # 1) everyone waits one more draw
        K += 1
        # 2) numbers that just hit get reset to 0
        for n in nums:
            K[n - 1] = 0

    # Cast to nicer types
    df[k_cols + ['k_min', 'k_max']] = df[k_cols + ['k_min', 'k_max']].astype(int)
    df['k_mean'] = df['k_mean'].astype(float)

    return df


# ======================================================================
# A tiny backtest: are big-delay draws "special"?
# ======================================================================

def kmin_band_stats(hist_df, bins=(0, 6, 11, 9999)):
    """
    Group draws by k_min into delay bands and show simple stats.

    bins define the band edges. For example:
      (0, 6, 11, 9999) ->
        [0, 5]   => 'A:0-5'
        [6, 10]  => 'B:6-10'
        [11, ..] => 'C:11+'
    """

    df = hist_df.copy()

    labels = [f"A:{bins[0]}-{bins[1]-1}",
              f"B:{bins[1]}-{bins[2]-1}",
              f"C:{bins[2]}+"]

    df['k_band'] = pd.cut(df['k_min'],
                          bins=bins,
                          labels=labels,
                          right=False)

    band_counts = df['k_band'].value_counts().sort_index()

    print("=== k_min band counts ===")
    print(band_counts)
    print()

    # Rough idea of how often each band appears in time
    # by looking at average gap between hits of that band
    for band in labels:
        indices = df.index[df['k_band'] == band].to_list()
        if len(indices) < 2:
            print(f"{band}: too few occurrences for gap stats")
            continue

        gaps = [indices[0]] + [
            indices[i] - indices[i - 1] for i in range(1, len(indices))
        ]
        avg_gap = sum(gaps) / len(gaps)
        max_gap = max(gaps)

        print(f"{band}: occurrences={len(indices)}, "
              f"avg_gap={avg_gap:.1f} draws, max_gap={max_gap}")


# ======================================================================
# The compute_positioned_draws_since_last_hit function
# ======================================================================

def compute_positioned_draws_since_last_hit(df):
    """
    Given df with columns st1…st5, returns a DataFrame with columns K1…K5
    such that Kp at row i is the number of draws since the value in stp last
    appeared in position p (including the current draw; so a fresh hit → 0).
    """
    # Make a copy so we don't clobber the original
    df = df.reset_index(drop=True).copy()

    # Prepare the output
    ks = pd.DataFrame(index=df.index, columns=[f'K{p}' for p in range(1,6)], dtype=int)

    # For each position, we'll track the last index where each number appeared
    # last_seen[p] will be an array of length max_num+1, mapping number → last index
    max_num = df[['st1','st2','st3','st4','st5']].values.max()
    for pos in range(1,6):
        last_seen = np.full(max_num+1, -1, dtype=int)
        col = f'st{pos}'
        Kcol = f'K{pos}'

        # Walk through the draws in order
        for i, num in enumerate(df[col].astype(int)):
            prev_idx = last_seen[num]
            # if never seen before, we can define "draws since" = i (or you could use i+1)
            ks.at[i, Kcol] = i - prev_idx - 1 if prev_idx >= 0 else i
            # record that we just saw it here
            last_seen[num] = i

    return ks

# Usage
K = compute_positioned_draws_since_last_hit(hist_df)
hist_df = pd.concat([hist_df, K], axis=1)
