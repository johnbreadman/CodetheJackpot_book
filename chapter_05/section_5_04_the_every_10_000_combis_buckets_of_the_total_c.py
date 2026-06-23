"""
Code the Jackpot - 5.4. The Every 10,000 Combis Buckets of the Total Combinations Set
Auto-extracted (book order). Full listings, nothing truncated.
"""


# ======================================================================
# Code listing: n10000 binning and backtests
# ======================================================================
import pandas as pd
import numpy as np


def populate_bin_distribution_vectorized(
    data,
    stidx_column="stidx",
    bin_size=10000,
    last_bin_size=8760,
    new_column_name="n10000",
    total_combos=2118760,
):
    """
    Add a bin index and a 'times-used-so-far' counter to the historical draws.

    Each draw is placed in a bin of width `bin_size` on the stidx axis
    (with a shorter last bin). Within each bin, the new column shows
    how many earlier draws had already fallen in that same bin.
    """
    data = data.copy()

    # Set up bin edges along the stidx axis
    num_bins = (total_combos - last_bin_size) // bin_size + 1
    bin_edges = [i * bin_size for i in range(num_bins)] + [
        num_bins * bin_size + last_bin_size
    ]

    # Assign bin indices (0..num_bins-1)
    bin_idx = pd.cut(
        data[stidx_column],
        bins=bin_edges,
        right=False,      # [left, right) intervals
        labels=False
    ).astype("Int64")

    data["bin_idx"] = bin_idx

    # For each bin, cumcount gives how many previous rows shared that bin
    data[new_column_name] = data.groupby("bin_idx").cumcount()

    # Final counts per bin
    bin_counts = {i: 0 for i in range(num_bins)}
    vc = data["bin_idx"].value_counts().to_dict()
    for k, v in vc.items():
        if pd.isna(k):
            continue
        bin_counts[int(k)] = int(v)

    return data, bin_counts, bin_edges


def update_total_combinations_with_bin_counts_vectorized(
    total_combinations_df,
    bin_counts,
    bin_edges,
    stidx_column="stidx",
    new_column_name="n10000",
):
    """
    Add the final bin usage counter to every combination in the total
    combinations table, based on its stidx value.
    """
    df = total_combinations_df.copy()

    bin_idx = pd.cut(
        df[stidx_column],
        bins=bin_edges,
        right=False,
        labels=False
    ).astype("Int64")

    df["bin_idx"] = bin_idx

    df[new_column_name] = df["bin_idx"].map(
        lambda x: bin_counts.get(int(x), 0) if pd.notna(x) else 0
    ).astype(int)

    return df


def backtest_n10000_intervals(
    hist_df,
    stidx_column='stidx',
    bin_size=10000,
    last_bin_size=8760,
    total_combos=2118760,
    intervals=None,
    start_row=500
):
    """
    Backtest simple bin-based filters.

    Each draw is assigned to a bin of size `bin_size` on the stidx axis.
    Bins are tracked over time with a counter of how many draws have
    already fallen there.

    For each interval [L, U] in `intervals` we ask:

      - At each draw t, what fraction of the 2,118,760 combinations live
        in bins whose current count lies between L and U?

      - Did the t-th winning combination fall into one of those bins?

    We then compare the empirical hit rate to the average coverage
    fraction to get a lift score for each interval.
    """
    if intervals is None:
        # Example ranges; tune these after you look at the data
        intervals = [(0, 0), (1, 2), (3, 5), (6, 999)]

    hist_df = hist_df.sort_index()

    # Build bin sizes: all bins of length bin_size, last shorter bin
    num_bins = (total_combos - last_bin_size) // bin_size + 1
    bin_sizes = [bin_size] * num_bins
    bin_sizes[-1] = last_bin_size

    # Sanity check to avoid silent mistakes
    assert sum(bin_sizes) == total_combos

    # Current count of draws in each bin
    bin_counts = [0] * num_bins

    # Stats we collect per interval
    stats = {
        interval: {"hits": 0, "exposure": 0.0, "draws": 0}
        for interval in intervals
    }

    for t, row in enumerate(hist_df.itertuples()):
        stidx = getattr(row, stidx_column)

        # Integer division maps stidx -> bin_index (0..num_bins-1)
        bin_idx = stidx // bin_size
        if bin_idx >= num_bins:
            bin_idx = num_bins - 1

        if t >= start_row:
            for interval in intervals:
                L, U = interval

                # How many combinations live in bins with counts in [L, U]?
                total_in_bins = 0
                for b_idx, count in enumerate(bin_counts):
                    if L <= count <= U:
                        total_in_bins += bin_sizes[b_idx]

                coverage = total_in_bins / total_combos

                rec = stats[interval]
                rec["exposure"] += coverage

                # Did the upcoming draw fall into those bins?
                if L <= bin_counts[bin_idx] <= U:
                    rec["hits"] += 1

                rec["draws"] += 1

        # Now that draw t is processed, update its bin counter
        bin_counts[bin_idx] += 1

    # Prepare a summary table
    rows = []
    for interval, rec in stats.items():
        draws = rec["draws"]
        if draws == 0:
            continue

        avg_coverage = rec["exposure"] / draws
        hit_rate = rec["hits"] / draws
        lift = hit_rate / avg_coverage if avg_coverage > 0 else float("nan")

        rows.append(
            {
                "interval": interval,
                "draws": draws,
                "hits": rec["hits"],
                "hit_rate": hit_rate,
                "avg_coverage": avg_coverage,
                "lift": lift,
            }
        )

    return pd.DataFrame(rows)


# -------------------------------------------------------------------
# Example usage
# -------------------------------------------------------------------

# 1. Add bin info and n10000 to the historical draws
# df_hist is your full EuroJackpot history with a 'stidx' column

df_hist = pd.read_csv('data/total_nikstiles.csv',index_col=0)
df_hist_bins, bin_counts, bin_edges = populate_bin_distribution_vectorized(df_hist)

# 2. Paint the same feature on the total combinations table
total_combinations_df = pd.read_csv('data/totalcombinations.csv', index_col=0)
total_combinations_df = update_total_combinations_with_bin_counts_vectorized(
     total_combinations_df, bin_counts, bin_edges
 )

# 3. Backtest bin intervals on recent history
# For example, focus on the last 300 draws, but still let counts
# accumulate from the very beginning:

start_row = max(400, len(df_hist) - 300)
intervals = [(x1, x2) for x1 in range(10) for x2 in range(12) if x1<=x2]
summary_bins = backtest_n10000_intervals(
     df_hist,
     stidx_column='stidx',
     intervals=intervals,
     start_row=100
 )
print(summary_bins.sort_values(by='lift', ascending=False))


import numpy as np
import pandas as pd
from scipy import stats


def calculate_column_statistics(df, target_columns):
    """
    Your original function, unchanged.
    """
    value_combinations = df[target_columns].apply(tuple, axis=1)
    unique_combinations = value_combinations.unique()
    last_combination = value_combinations.iloc[-1]

    combination_indices = {
        combination: value_combinations[value_combinations == combination].index.tolist()
        for combination in unique_combinations
    }

    statistics_results = pd.DataFrame()

    for combination, indices in combination_indices.items():
        index_differences = [indices[0]] +             [indices[i] - indices[i - 1] for i in range(1, len(indices))] +             [len(df) - indices[-1]]

        stats_dict = {
            'combination': combination,
            'frequency': len(indices),
            'last_gap': index_differences[-1],
            'median_gap': int(np.percentile(index_differences, 50)),
            'p75_gap': int(np.percentile(index_differences, 75)),
            'p90_gap': int(np.percentile(index_differences, 90)),
            'p95_gap': int(np.percentile(index_differences, 95)),
            'p99_gap': int(np.max(index_differences)),
            'max_gap': int(np.max(index_differences)),
            'percentile_score': int(
                stats.percentileofscore(index_differences, index_differences[-1])
            )
        }

        statistics_results = pd.concat(
            [statistics_results, pd.DataFrame([stats_dict])],
            ignore_index=True
        )

    statistics_results['normalized_frequency'] = (
        100 * statistics_results['frequency'] /
        statistics_results['frequency'].sum()
    ).round(2)

    statistics_results['product_score'] = (
        statistics_results['normalized_frequency'] *
        statistics_results['percentile_score']
    ).round(2)

    statistics_results.sort_values(
        by='product_score',
        ascending=False,
        inplace=True
    )
    statistics_results.reset_index(drop=True, inplace=True)

    return statistics_results


def backtest_n10000_spacing_topk(
    df_hist,
    start_row=100,
    top_k=7,
    stidx_column='stidx',
    bin_size=10000,
    last_bin_size=8760,
    total_combos=2118760,
):
    """
    Backtest a spacing-based predictor on the n10000 sequence.

    Procedure:
      1. Maintain bin_counts over the stidx axis (10,000-sized bins).
      2. For each draw t:
         - n10000[t] = current count of its bin (before increment).
         - After prediction, increment that bin's count.

      3. For each t >= start_row:
         - Build a small DataFrame with the history of n10000 values
           up to t-1.
         - Run calculate_column_statistics on ['n10000'].
         - Take the top_k best-scored values (0,1,2,...) as the
           "predicted" n10000 states for draw t.
         - Check if actual n10000[t] is in that set.
         - Compute coverage_t: fraction of the 2,118,760 combinations that
           live in bins whose current count (n10000 value) is one
           of those top_k values.
         - Accumulate hits and coverage.

      4. Return a one-row DataFrame with hit rate, average coverage
         and lift.
    """
    df_hist = df_hist.copy()
    df_hist = df_hist.sort_index()

    n_draws = len(df_hist)

    # ------------------------------------------------------------------
    # 1. Bin model over stidx
    # ------------------------------------------------------------------
    # How many bins?
    num_bins = (total_combos - last_bin_size) // bin_size + 1

    # Size of each bin
    bin_sizes = [bin_size] * num_bins
    bin_sizes[-1] = last_bin_size

    # Sanity check
    assert sum(bin_sizes) == total_combos

    # Map each draw to its bin index
    stidx_values = df_hist[stidx_column].to_numpy()
    bin_idx_for_draws = stidx_values // bin_size
    bin_idx_for_draws = np.clip(bin_idx_for_draws, 0, num_bins - 1)

    # Current counts per bin
    bin_counts = [0] * num_bins

    # Sequence of n10000 values per draw
    n_history = []

    # ------------------------------------------------------------------
    # 2. Warm-up: process draws up to start_row without predictions
    # ------------------------------------------------------------------
    warmup_limit = min(start_row, n_draws)
    for t in range(warmup_limit):
        b_idx = int(bin_idx_for_draws[t])
        current_n = bin_counts[b_idx]       # count BEFORE increment
        n_history.append(current_n)
        bin_counts[b_idx] += 1

    # ------------------------------------------------------------------
    # 3. Prediction loop
    # ------------------------------------------------------------------
    hits = 0
    draws = 0
    exposure_sum = 0.0  # sum of coverage over all prediction steps

    for t in range(start_row, n_draws):
        b_idx = int(bin_idx_for_draws[t])

        # Actual n10000 for this draw (before update)
        actual_n = bin_counts[b_idx]

        # Build DataFrame from history of n10000 up to t-1
        hist_df_for_stats = pd.DataFrame(
            {"n10000": n_history},
            copy=False
        )

        # Run your spacing-based ranking
        stats_df = calculate_column_statistics(
            hist_df_for_stats,
            ["n10000"]
        )

        # Take the top_k candidate n10000 values
        top_combinations = stats_df["combination"].head(top_k).tolist()
        top_values = [comb[0] for comb in top_combinations]

        # Coverage at this moment: how many combinations live in bins
        # whose current count is in top_values?
        total_selected = 0
        for bb, count in enumerate(bin_counts):
            if count in top_values:
                total_selected += bin_sizes[bb]
        coverage_t = total_selected / total_combos

        # Update backtest counters
        draws += 1
        exposure_sum += coverage_t
        if actual_n in top_values:
            hits += 1

        # Append current n10000 to history and update its bin
        n_history.append(actual_n)
        bin_counts[b_idx] += 1

    # ------------------------------------------------------------------
    # 4. Aggregate results
    # ------------------------------------------------------------------
    if draws == 0:
        return pd.DataFrame(
            [{
                "start_row": start_row,
                "top_k": top_k,
                "draws": 0,
                "hits": 0,
                "hit_rate": np.nan,
                "avg_coverage": np.nan,
                "lift": np.nan
            }]
        )

    hit_rate = hits / draws
    avg_coverage = exposure_sum / draws
    lift = hit_rate / avg_coverage if avg_coverage > 0 else np.nan

    result = pd.DataFrame(
        [{
            "start_row": start_row,
            "top_k": top_k,
            "draws": draws,
            "hits": hits,
            "hit_rate": hit_rate,
            "avg_coverage": avg_coverage,
            "lift": lift,
        }]
    )

    return result

result_top7 = backtest_n10000_spacing_topk(
    df_hist,
    start_row=700,
    top_k=7,
    stidx_column='stidx',
    bin_size=10000,
    last_bin_size=8760,
    total_combos=2118760
)

print(result_top7)
