"""
Code the Jackpot - 5.0 Chapter 5 - intro
Auto-extracted (book order). Full listings, nothing truncated.
"""


# ======================================================================
# Chapter 5 – Strategies for Winning
# ======================================================================
import numpy as np

import pandas as pd

from collections import Counter

def compute_frequency_table(

    hist_df: pd.DataFrame,

    cols=('st1', 'st2', 'st3', 'st4', 'st5')

) -> pd.DataFrame:

    """

    Count how many times each main number appears in the given draws.

    Parameters

    ----------

    hist_df : DataFrame

        Historical draws (or a subset of them).

    cols : tuple of str

        Columns that hold the 5 main numbers.

    Returns

    -------

    freq_df : DataFrame

        Columns:

          - number: 1..50

          - hits:   total appearances in `cols`

          - rel_freq: hits / number of draws

    """

    # Flatten all main numbers into a single 1D array

    values = hist_df.loc[:, cols].to_numpy().ravel()

    counts = Counter(values)

    rows = []

    n_draws = len(hist_df)

    for n in range(1, 51):

        h = counts.get(n, 0)

        rows.append((n, h, h / n_draws if n_draws > 0 else 0.0))

    freq_df = pd.DataFrame(rows, columns=["number", "hits", "rel_freq"])

    freq_df = freq_df.sort_values(["hits", "number"], ascending=[False, True]).reset_index(drop=True)

    return freq_df

freq_full = compute_frequency_table(hist_df)print(freq_full.head(10))

def split_into_three_groups(freq_df: pd.DataFrame):

    """

    Split numbers into 3 groups based on descending hit counts.

    Returns

    -------

    groups : dict

        {

          "G1": set of top 17 numbers,

          "G2": set of next 17,

          "G3": set of bottom 16

        }

    """

    numbers_sorted = freq_df["number"].tolist()

    g1 = set(numbers_sorted[:17])

    g2 = set(numbers_sorted[17:34])

    g3 = set(numbers_sorted[34:])

    return {"G1": g1, "G2": g2, "G3": g3}

from collections import defaultdict

import numpy as np

def backtest_frequency_groups(

    hist_df: pd.DataFrame,

    start_draw: int = 100,

    cols=('st1', 'st2', 'st3', 'st4', 'st5')

) -> tuple[pd.DataFrame, pd.DataFrame]:

    """

    Backtest frequency-based ranking from `start_draw` onward.

    For each draw t >= start_draw:

      - Build frequency ranking on draws [0..t-1]

      - Split numbers into 3 groups G1,G2,G3 (17,17,16)

      - Count hits of the actual draw t in each group.

    Parameters

    ----------

    hist_df : DataFrame

        Full history of draws in time order.

    start_draw : int

        First draw index to evaluate (0-based).

    cols : tuple of str

        Columns containing the main numbers.

    Returns

    -------

    hits_log : DataFrame

        One row per evaluated draw:

          - draw_idx

          - hits_G1, hits_G2, hits_G3

    summary : DataFrame

        Summary per group with observed hits, expected hits and lift.

    """

    records = []

    n_total_draws = len(hist_df)

    for t in range(start_draw, n_total_draws):

        past = hist_df.iloc[:t]

        current = hist_df.iloc[t]

        # Build current frequency ranking

        freq_df = compute_frequency_table(past, cols=cols)

        groups = split_into_three_groups(freq_df)

        # Current drawn numbers as a set

        draw_nums = set(int(current[c]) for c in cols)

        hits_G1 = len(draw_nums & groups["G1"])

        hits_G2 = len(draw_nums & groups["G2"])

        hits_G3 = len(draw_nums & groups["G3"])

        records.append({

            "draw_idx": t,

            "hits_G1": hits_G1,

            "hits_G2": hits_G2,

            "hits_G3": hits_G3

        })

    hits_log = pd.DataFrame(records)

    # --- Summary and lift calculation ---

    num_eval_draws = len(hits_log)

    group_sizes = {"G1": 17, "G2": 17, "G3": 16}

    total_numbers = 50

    numbers_drawn = len(cols)  # 5

    rows_sum = []

    for g in ["G1", "G2", "G3"]:

        col_name = f"hits_{g}"

        total_hits = hits_log[col_name].sum()

        avg_hits_per_draw = total_hits / num_eval_draws

        # Baseline expectation for random numbers:

        # each number has probability 5/50 per draw,

        # group of size S expected hits = S * 5/50

        expected_hits_per_draw = group_sizes[g] * numbers_drawn / total_numbers

        lift = avg_hits_per_draw / expected_hits_per_draw if expected_hits_per_draw > 0 else np.nan

        rows_sum.append({

            "group": g,

            "size": group_sizes[g],

            "avg_hits_per_draw": avg_hits_per_draw,

            "expected_hits_per_draw": expected_hits_per_draw,

            "lift": lift

        })

    summary = pd.DataFrame(rows_sum)

    return hits_log, summary

import math

def summarize_patterns(

    hits_log: pd.DataFrame,

    group_sizes: dict = None,

    total_numbers: int = 50,

    k: int = 5

) -> pd.DataFrame:

    """

    Count the distribution of (hits_G1, hits_G2, hits_G3) patterns and

    compute lift for each pattern based on combinatorial baseline.

    Parameters

    ----------

    hits_log : DataFrame

        Must contain columns: "hits_G1", "hits_G2", "hits_G3".

    group_sizes : dict, optional

        Sizes of each group, e.g. {"G1": 17, "G2": 17, "G3": 16}.

        If None, defaults to that.

    total_numbers : int

        Total number of main numbers (default 50).

    k : int

        Numbers drawn per draw (default 5).

    Returns

    -------

    pattern_counts : DataFrame

        Columns:

          - pattern      : (h1, h2, h3)

          - count        : how many draws with this pattern

          - rel_freq     : empirical frequency

          - baseline_prob: combinatorial probability under random grouping

          - lift         : rel_freq / baseline_prob

    """

    if group_sizes is None:

        group_sizes = {"G1": 17, "G2": 17, "G3": 16}

    # Empirical pattern frequencies

    pattern_counts = (

        hits_log

        .assign(pattern=lambda df: list(zip(df["hits_G1"], df["hits_G2"], df["hits_G3"])))

        .groupby("pattern")

        .size()

        .reset_index(name="count")

        .sort_values("count", ascending=False)

    )

    total_draws = pattern_counts["count"].sum()

    pattern_counts["rel_freq"] = pattern_counts["count"] / total_draws

    # Combinatorial baseline: number of combinations with pattern (h1,h2,h3)

    total_combos = math.comb(total_numbers, k)

    baseline_probs = []

    lifts = []

    for pattern, rel_f in zip(pattern_counts["pattern"], pattern_counts["rel_freq"]):

        h1, h2, h3 = pattern

        combos_pattern = (

            math.comb(group_sizes["G1"], h1) *

            math.comb(group_sizes["G2"], h2) *

            math.comb(group_sizes["G3"], h3)

        )

        baseline_prob = combos_pattern / total_combos if total_combos > 0 else np.nan

        baseline_probs.append(baseline_prob)

        if baseline_prob > 0:

            lifts.append(rel_f / baseline_prob)

        else:

            lifts.append(np.nan)

    pattern_counts["baseline_prob"] = baseline_probs

    pattern_counts["lift"] = lifts

    return pattern_counts
