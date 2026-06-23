"""
Code the Jackpot - Appendix 2: A Recommendation System for EuroJackpot "EuroNumbers"
Auto-extracted (book order). Full listings, nothing truncated.
"""


# ======================================================================
# Appendix 2: A Recommendation System for EuroJackpot "EuroNumbers"
# ======================================================================
import numpy as np

import pandas as pd

def calculate_percentiles_multi_columns(df, cols):

    """

    Spacing-based ranking for EuroNumbers across multiple columns.

    Parameters

    ----------

    df : pandas.DataFrame

        Historical draws. Must contain the columns in `cols`.

    cols : list[str]

        Columns that hold the EuroNumbers (e.g. ["n1", "n2"]).

    Returns

    -------

    table : pandas.DataFrame

        One row per EuroNumber with:

        - value      : the EuroNumber

        - count      : number of gap intervals

        - delay      : last gap (current waiting time)

        - median     : median gap

        - P75,P90,P95,P99,max : gap distribution summaries

        - Pct_score  : percentile of the last gap within its own gaps

        - Norm       : normalised count (%)

        - Prod       : Norm * Pct_score (main ranking score)

    """

    if df.empty:

        return pd.DataFrame(

            columns=[

                "value", "count", "delay", "median",

                "P75", "P90", "P95", "P99",

                "max", "Pct_score", "Norm", "Prod"

            ]

        )

    # Unique EuroNumbers in the given columns

    values = pd.unique(df[cols].values.ravel("K"))

    rows = []

    n = len(df)

    for v in values:

        # Positions where v appears in any of the columns

        mask = df[cols].isin([v]).any(axis=1).to_numpy()

        idx = np.flatnonzero(mask)         # 0..n-1 positions

        if idx.size == 0:

            continue

        # Gap sequence based on row positions

        diffs = [int(idx[0])]

        diffs += [int(idx[i] - idx[i - 1]) for i in range(1, len(idx))]

        diffs.append(int(n - idx[-1]))

        if len(diffs) <= 1:

            continue

        diffs_arr = np.asarray(diffs, dtype=float)

        delay = diffs[-1]

        count = len(diffs) - 1

        median = float(np.median(diffs_arr))

        P75, P90, P95, P99 = np.percentile(diffs_arr, [75, 90, 95, 99])

        max_gap = float(diffs_arr.max())

        # Simple percentile-of-score: fraction of gaps <= last gap

        pct_score = 100.0 * float(np.mean(diffs_arr <= delay))

        rows.append(

            dict(

                value=int(v),

                count=count,

                delay=int(delay),

                median=median,

                P75=float(P75),

                P90=float(P90),

                P95=float(P95),

                P99=float(P99),

                max=max_gap,

                Pct_score=pct_score,

            )

        )

    if not rows:

        return pd.DataFrame(

            columns=[

                "value", "count", "delay", "median",

                "P75", "P90", "P95", "P99",

                "max", "Pct_score", "Norm", "Prod"

            ]

        )

    res = pd.DataFrame(rows)

    # Normalised frequency and main ranking score

    res["Norm"] = 100.0 * res["count"] / res["count"].sum()

    res["Prod"] = res["Norm"] * res["Pct_score"]

    # Higher Prod → higher rank

    res = res.sort_values("Prod", ascending=False).reset_index(drop=True)

    return res

def norm01(s):

    """

    Normalise a pandas Series to [0, 1].

    If all values are equal, return 0.5 for all.

    """

    s = s.astype(float)

    lo = s.min()

    hi = s.max()

    if hi == lo:

        return pd.Series(0.5, index=s.index)

    return (s - lo) / (hi - lo)

def compute_K_map(df, cols, values=None):

    """

    Compute K = draws since last hit for each EuroNumber.

    Parameters

    ----------

    df : pandas.DataFrame

        Historical draws (only the history window you want to use).

    cols : list[str]

        Columns that hold the EuroNumbers (e.g. ["n1","n2"]).

    values : iterable or None

        If given, restrict the computation to these EuroNumbers;

        otherwise use all numbers appearing in the columns.

    Returns

    -------

    K_map : dict[int, int]

        Mapping number -> K (draws since last hit).

        Numbers never seen get K = len(df).

    """

    if values is None:

        values = sorted(pd.unique(df[cols].values.ravel("K")))

    last_seen = {int(v): None for v in values}

    # Walk through the history using row positions

    for pos, row in enumerate(df[cols].itertuples(index=False, name=None)):

        for v in row:

            if pd.isna(v):

                continue

            last_seen[int(v)] = pos

    n = len(df)

    K = {}

    for v in values:

        v = int(v)

        if last_seen[v] is None:

            K[v] = n          # never seen → maximally overdue

        else:

            K[v] = n - 1 - last_seen[v]  # draws since last hit

    return K

def select_seed_numbers(hist, cols=("n1", "n2"), top_seed=10):

    """

    Stage 1: spacing-based ranking, return the top_seed EuroNumbers.

    Returns

    -------

    seed : list[int]

        Top `top_seed` EuroNumbers by Prod.

    table : pandas.DataFrame

        Full spacing table from calculate_percentiles_multi_columns().

    """

    table = calculate_percentiles_multi_columns(hist, list(cols))

    seed = table["value"].head(top_seed).astype(int).tolist()

    return seed, table

def cut_to_6_kboost(hist, seed_values, cols=("n1", "n2")):

    """

    Stage 2: K-boost refinement from seed (size 10) down to 6 EuroNumbers.

    Parameters

    ----------

    hist : pandas.DataFrame

        History window used for K computation.

    seed_values : list[int]

        The seed EuroNumbers (e.g., length 10).

    cols : tuple[str, str]

        EuroNumber columns.

    Returns

    -------

    final6 : list[int]

        Final six EuroNumbers (most overdue within the seed).

    k_table : pandas.DataFrame

        DataFrame with columns: value, K, K_norm (sorted by K_norm desc).

    """

    K_map = compute_K_map(hist, list(cols), values=seed_values)

    df_seed = pd.DataFrame(

        {

            "value": [int(v) for v in seed_values],

            "K": [K_map[int(v)] for v in seed_values],

        }

    )

    df_seed["K_norm"] = norm01(df_seed["K"])

    df_seed = df_seed.sort_values("K_norm", ascending=False).reset_index(drop=True)

    final6 = df_seed["value"].head(6).tolist()

    return final6, df_seed

def backtest_euronumbers(df, start=100, window=None,

                         top_seed=10, cols=("n1", "n2")):

    """

    Walk-forward backtest for the 10→6 EuroNumbers strategy.

    Parameters

    ----------

    df : pandas.DataFrame

        Full historical dataset with EuroNumber columns `cols`.

    start : int

        First row index t at which to start testing. At time t,

        history is draws [0 .. t-1], and we predict draw t.

    window : int or None

        If None: use all draws [0 .. t-1] as history.

        If int: use rolling window [t-window .. t-1] as history.

    top_seed : int

        Size of the spacing-based seed (default 10).

    cols : tuple[str, str]

        EuroNumber columns, e.g. ("n1","n2").

    Returns

    -------

    bt_df : pandas.DataFrame

        One row per tested draw with:

        - t       : draw index that was predicted

        - window  : 0 for full-history, or the window size

        - hits    : number of correct EuroNumbers (0, 1 or 2)

        - n_hist  : number of draws in the history window

    """

    rows = []

    for t in range(start, len(df)):

        # History ends at t-1; next draw to predict is row t

        if window is None:

            hist = df.iloc[:t].copy()

        else:

            hist = df.iloc[max(0, t - window):t].copy()

        if hist.empty:

            continue

        # Reset index so internal spacing uses row positions 0..len(hist)-1

        hist = hist.reset_index(drop=True)

        seed, _ = select_seed_numbers(hist, cols=cols, top_seed=top_seed)

        pred6, _ = cut_to_6_kboost(hist, seed, cols=cols)

        nxt = set(df.iloc[t][list(cols)].astype(int).tolist())

        hits = len(nxt.intersection(pred6))

        rows.append(

            dict(

                t=int(t),

                window=0 if window is None else int(window),

                hits=int(hits),

                n_hist=len(hist),

            )

        )

    return pd.DataFrame(rows)

def predict_next_euronumbers(df, window=None,

                             top_seed=10, cols=("n1", "n2")):

    """

    Operational function: predict the next six EuroNumbers.

    Parameters

    ----------

    df : pandas.DataFrame

        Full historical dataset up to the last available draw.

    window : int or None

        If None: use all history.

        If int: use only the last `window` draws.

    top_seed : int

        Size of the spacing-based seed (default 10).

    cols : tuple[str, str]

        EuroNumber columns.

    Returns

    -------

    final6 : list[int]

        Six recommended EuroNumbers for the next draw.

    seed : list[int]

        Top-seed EuroNumbers (length top_seed).

    spacing_table : pandas.DataFrame

        Full spacing ranking (all numbers) for the chosen history window.

    k_table : pandas.DataFrame

        K-boost ranking within the seed (10→6 step).

    """

    if window is None or window >= len(df):

        hist = df.copy()

    else:

        hist = df.iloc[-window:].copy()

    hist = hist.reset_index(drop=True)

    seed, spacing_table = select_seed_numbers(hist, cols=cols, top_seed=top_seed)

    final6, k_table = cut_to_6_kboost(hist, seed, cols=cols)

    return final6, seed, spacing_table, k_table

bt_150 = backtest_euronumbers(hist_df, start=150, window=150, top_seed=10, cols=("n1", "n2"))

import math

import numpy as np

import pandas as pd

def calculate_percentiles_multi_columns(df, cols):

    """

    Spacing-based ranking for EuroNumbers across multiple columns.

    Parameters

    ----------

    df : pandas.DataFrame

        Historical draws. Must contain the columns in `cols`.

    cols : list[str]

        Columns that hold the EuroNumbers (e.g. ["n1", "n2"]).

    Returns

    -------

    table : pandas.DataFrame

        One row per EuroNumber with:

        - value      : the EuroNumber

        - count      : number of gap intervals

        - delay      : last gap (current waiting time)

        - median     : median gap

        - P75,P90,P95,P99,max : gap distribution summaries

        - Pct_score  : percentile of the last gap within its own gaps

        - Norm       : normalised count (%)

        - Prod       : Norm * Pct_score (main ranking score)

    """

    if df.empty:

        return pd.DataFrame(

            columns=[

                "value", "count", "delay", "median",

                "P75", "P90", "P95", "P99",

                "max", "Pct_score", "Norm", "Prod"

            ]

        )

    # Unique EuroNumbers in the given columns

    values = pd.unique(df[cols].values.ravel("K"))

    rows = []

    n = len(df)

    for v in values:

        # Positions where v appears in any of the columns

        mask = df[cols].isin([v]).any(axis=1).to_numpy()

        idx = np.flatnonzero(mask)         # 0..n-1 positions

        if idx.size == 0:

            continue

        # Gap sequence based on row positions

        diffs = [int(idx[0])]

        diffs += [int(idx[i] - idx[i - 1]) for i in range(1, len(idx))]

        diffs.append(int(n - idx[-1]))

        if len(diffs) <= 1:

            continue

        diffs_arr = np.asarray(diffs, dtype=float)

        delay = diffs[-1]

        count = len(diffs) - 1

        median = float(np.median(diffs_arr))

        P75, P90, P95, P99 = np.percentile(diffs_arr, [75, 90, 95, 99])

        max_gap = float(diffs_arr.max())

        # Simple percentile-of-score: fraction of gaps <= last gap

        pct_score = 100.0 * float(np.mean(diffs_arr <= delay))

        rows.append(

            dict(

                value=int(v),

                count=count,

                delay=int(delay),

                median=median,

                P75=float(P75),

                P90=float(P90),

                P95=float(P95),

                P99=float(P99),

                max=max_gap,

                Pct_score=pct_score,

            )

        )

    if not rows:

        return pd.DataFrame(

            columns=[

                "value", "count", "delay", "median",

                "P75", "P90", "P95", "P99",

                "max", "Pct_score", "Norm", "Prod"

            ]

        )

    res = pd.DataFrame(rows)

    # Normalised frequency and main ranking score

    res["Norm"] = 100.0 * res["count"] / res["count"].sum()

    res["Prod"] = res["Norm"] * res["Pct_score"]

    # Higher Prod → higher rank

    res = res.sort_values("Prod", ascending=False).reset_index(drop=True)

    return res

def norm01(s):

    """

    Normalise a pandas Series to [0, 1].

    If all values are equal, return 0.5 for all.

    """

    s = s.astype(float)

    lo = s.min()

    hi = s.max()

    if hi == lo:

        return pd.Series(0.5, index=s.index)

    return (s - lo) / (hi - lo)

def compute_K_map(df, cols, values=None):

    """

    Compute K = draws since last hit for each EuroNumber.

    Parameters

    ----------

    df : pandas.DataFrame

        Historical draws (only the history window you want to use).

    cols : list[str]

        Columns that hold the EuroNumbers (e.g. ["n1","n2"]).

    values : iterable or None

        If given, restrict the computation to these EuroNumbers;

        otherwise use all numbers appearing in the columns.

    Returns

    -------

    K_map : dict[int, int]

        Mapping number -> K (draws since last hit).

        Numbers never seen get K = len(df).

    """

    if values is None:

        values = sorted(pd.unique(df[cols].values.ravel("K")))

    last_seen = {int(v): None for v in values}

    # Walk through the history using row positions

    for pos, row in enumerate(df[cols].itertuples(index=False, name=None)):

        for v in row:

            if pd.isna(v):

                continue

            last_seen[int(v)] = pos

    n = len(df)

    K = {}

    for v in values:

        v = int(v)

        if last_seen[v] is None:

            K[v] = n          # never seen → maximally overdue

        else:

            K[v] = n - 1 - last_seen[v]  # draws since last hit

    return K

def select_seed_numbers(hist, cols=("n1", "n2"), top_seed=10):

    """

    Stage 1: spacing-based ranking, return the top_seed EuroNumbers.

    Returns

    -------

    seed : list[int]

        Top `top_seed` EuroNumbers by Prod.

    table : pandas.DataFrame

        Full spacing table from calculate_percentiles_multi_columns().

    """

    table = calculate_percentiles_multi_columns(hist, list(cols))

    seed = table["value"].head(top_seed).astype(int).tolist()

    return seed, table

def cut_to_6_kboost(hist, seed_values, cols=("n1", "n2")):

    """

    Stage 2: K-boost refinement from seed (size 10) down to 6 EuroNumbers.

    Parameters

    ----------

    hist : pandas.DataFrame

        History window used for K computation.

    seed_values : list[int]

        The seed EuroNumbers (e.g., length 10).

    cols : tuple[str, str]

        EuroNumber columns.

    Returns

    -------

    final6 : list[int]

        Final six EuroNumbers (most overdue within the seed).

    k_table : pandas.DataFrame

        DataFrame with columns: value, K, K_norm (sorted by K_norm desc).

    """

    K_map = compute_K_map(hist, list(cols), values=seed_values)

    df_seed = pd.DataFrame(

        {

            "value": [int(v) for v in seed_values],

            "K": [K_map[int(v)] for v in seed_values],

        }

    )

    df_seed["K_norm"] = norm01(df_seed["K"])

    df_seed = df_seed.sort_values("K_norm", ascending=False).reset_index(drop=True)

    final6 = df_seed["value"].head(6).tolist()

    return final6, df_seed

def backtest_euronumbers(df, start=100, window=None,

                         top_seed=10, cols=("n1", "n2")):

    """

    Walk-forward backtest for the 10→6 EuroNumbers strategy.

    Parameters

    ----------

    df : pandas.DataFrame

        Full historical dataset with EuroNumber columns `cols`.

    start : int

        First row index t at which to start testing. At time t,

        history is draws [0 .. t-1], and we predict draw t.

    window : int or None

        If None: use all draws [0 .. t-1] as history.

        If int: use rolling window [t-window .. t-1] as history.

    top_seed : int

        Size of the spacing-based seed (default 10).

    cols : tuple[str, str]

        EuroNumber columns, e.g. ("n1","n2").

    Returns

    -------

    bt_df : pandas.DataFrame

        One row per tested draw with:

        - t       : draw index that was predicted

        - window  : 0 for full-history, or the window size

        - hits    : number of correct EuroNumbers (0, 1 or 2)

        - n_hist  : number of draws in the history window

    """

    rows = []

    for t in range(start, len(df)):

        # History ends at t-1; next draw to predict is row t

        if window is None:

            hist = df.iloc[:t].copy()

        else:

            hist = df.iloc[max(0, t - window):t].copy()

        if hist.empty:

            continue

        # Reset index so internal spacing uses row positions 0..len(hist)-1

        hist = hist.reset_index(drop=True)

        seed, _ = select_seed_numbers(hist, cols=cols, top_seed=top_seed)

        pred6, _ = cut_to_6_kboost(hist, seed, cols=cols)

        nxt = set(df.iloc[t][list(cols)].astype(int).tolist())

        hits = len(nxt.intersection(pred6))

        rows.append(

            dict(

                t=int(t),

                window=0 if window is None else int(window),

                hits=int(hits),

                n_hist=len(hist),

            )

        )

    return pd.DataFrame(rows)

def predict_next_euronumbers(df, window=None,

                             top_seed=10, cols=("n1", "n2")):

    """

    Operational function: predict the next six EuroNumbers.

    Parameters

    ----------

    df : pandas.DataFrame

        Full historical dataset up to the last available draw.

    window : int or None

        If None: use all history.

        If int: use only the last `window` draws.

    top_seed : int

        Size of the spacing-based seed (default 10).

    cols : tuple[str, str]

        EuroNumber columns.

    Returns

    -------

    final6 : list[int]

        Six recommended EuroNumbers for the next draw.

    seed : list[int]

        Top-seed EuroNumbers (length top_seed).

    spacing_table : pandas.DataFrame

        Full spacing ranking (all numbers) for the chosen history window.

    k_table : pandas.DataFrame

        K-boost ranking within the seed (10→6 step).

    """

    if window is None or window >= len(df):

        hist = df.copy()

    else:

        hist = df.iloc[-window:].copy()

    hist = hist.reset_index(drop=True)

    seed, spacing_table = select_seed_numbers(hist, cols=cols, top_seed=top_seed)

    final6, k_table = cut_to_6_kboost(hist, seed, cols=cols)

    return final6, seed, spacing_table, k_table

# Random baseline probabilities for hits when picking 6 EuroNumbers

# uniformly at random out of 12.

RANDOM_P = {

    0: 15/66,   # P(0 hits)

    1: 36/66,   # P(1 hit)

    2: 15/66,   # P(2 hits)

}

def significance_label(p):

    """

    Map a p-value to a qualitative significance label.

    """

    if p < 0.001:

        return "Very strong evidence"

    elif p < 0.01:

        return "Strong evidence"

    elif p < 0.05:

        return "Moderate evidence"

    else:

        return "Not statistically significant"

def summarize_and_test(bt_df, label="window"):

    """

    Summarise hit distribution and test against the random 6-number baseline.

    Returns a dictionary with all key statistics so we can collect them

    across multiple window lengths.

    """

    n = len(bt_df)

    counts = bt_df["hits"].value_counts().reindex([0, 1, 2], fill_value=0)

    props = counts / n

    avg_hits = (counts[1] + 2 * counts[2]) / n

    # Expected counts under the random baseline

    exp_counts = pd.Series({k: RANDOM_P[k] * n for k in [0, 1, 2]})

    # Chi-square goodness-of-fit statistic (df = 2)

    chi2 = (((counts - exp_counts) ** 2) / exp_counts).sum()

    # For df = 2, the chi-square distribution is exactly exponential with mean 2,

    # so the tail probability (p-value) is exp(-chi2 / 2).

    p_value = math.exp(-chi2 / 2.0)

    sig = significance_label(p_value)

    print(f"=== {label} ===")

    print("Counts (0, 1, 2 hits):")

    print(counts.to_string())

    print("\\nProportions:")

    print(props.round(4).to_string())

    print(f"\\nAverage hits per draw: {avg_hits:.3f}")

    print(f"Chi-square vs random baseline: {chi2:.2f}")

    print(f"Exact p-value (df=2): {p_value:.2e}  →  {sig}")

    print()

    return {

        "label": label,

        "n_draws": n,

        "avg_hits": avg_hits,

        "chi2": chi2,

        "p_value": p_value,

        "significance": sig,

        "count_0": int(counts[0]),

        "count_1": int(counts[1]),

        "count_2": int(counts[2]),

    }

# Load the full EuroJackpot history (adapt the file name)

hist_df = pd.read_csv('data/total_nikstiles.csv',index_col=0)

# Keep only the EuroNumber columns and ensure they are integers

hist_df = hist_df[["n1", "n2"]].dropna().astype(int)

# Windows to test: full history + several rolling windows

windows = [None, 50, 100, 150, 200, 250]

results = []

for W in windows:

    if W is None:

        start = 100          # first test draw index for full history

        label = "Full history (start=100)"

    else:

        start = W            # first test draw uses a full W-draw window

        label = f"Rolling window {W} draws"

    bt = backtest_euronumbers(

        hist_df,

        start=start,

        window=W,

        top_seed=10,

        cols=("n1", "n2"),

    )

    res = summarize_and_test(bt, label=label)

    res["window"] = W if W is not None else -1  # use -1 to denote full history

    results.append(res)

# Collect all results in a DataFrame for convenient inspection

results_df = pd.DataFrame(results)

print("=== Summary over all window lengths ===")

print(results_df[

    ["label", "n_draws", "avg_hits", "chi2", "p_value", "significance"]

])

# Automatic choice of the best window according to the rule:

# 1) Prefer windows with p < 0.01 (strong or very strong evidence).

# 2) Among them, pick the one with highest average hits.

# 3) Break ties using chi2 (larger is better).

candidates = results_df[results_df["p_value"] < 0.01].copy()

if candidates.empty:

    # Relax threshold to p < 0.05

    candidates = results_df[results_df["p_value"] < 0.05].copy()

if candidates.empty:

    # No statistically significant window; pick by smallest p-value

    best = results_df.sort_values(["p_value", "avg_hits"], ascending=[True, False]).iloc[0]

    print("\\nNo window achieved clear statistical significance;")

    print("choosing the best available window by smallest p-value:")

else:

    # Sort by avg_hits (descending) then chi2 (descending)

    best = candidates.sort_values(["avg_hits", "chi2"], ascending=[False, False]).iloc[0]

    print("\\nChoosing the best window among statistically significant candidates:")

    print(best[["label", "avg_hits", "chi2", "p_value", "significance",'window']])

    predict_next_euronumbers(hist_df, window=best['window'], top_seed=10, cols=("n1", "n2"))

import numpy as np

import pandas as pd

def time_split_lift_test(

    hist_df,

    total_df,

    range_filters=None,

    in_filters=None,

    not_in_filters=None,

    split_ratio=0.5,

):

    """

    Check if a given filter recipe has stable lift in early vs late history.

    Parameters

    ----------

    hist_df : pd.DataFrame

        Historical draws with all feature columns.

    total_df : pd.DataFrame

        All possible 5-of-50 combinations with the same feature columns.

    range_filters, in_filters, not_in_filters :

        Filter dictionaries as used in the main chapters.

    split_ratio : float

        Fraction of history to use as 'early' segment (for example 0.5 → first half).

    """

    # Split history into early and late segments

    n_hist = len(hist_df)

    split_idx = int(n_hist * split_ratio)

    hist_early = hist_df.iloc[:split_idx].copy()

    hist_late  = hist_df.iloc[split_idx:].copy()

    print(f"Total draws: {n_hist}")

    print(f"Early segment : 0 .. {split_idx-1}  (size={len(hist_early)})")

    print(f"Late  segment : {split_idx} .. {n_hist-1} (size={len(hist_late)})")

    print()

    # Helper wrapper to call your filter function from the main text

    from your_module import filter_with_lift  # adjust import as needed

    def _run_filter(hdf, label):

        hist_f, total_f, info = filter_with_lift(

            hist_df=hdf,

            total_df=total_df,

            range_filters=range_filters,

            in_filters=in_filters,

            not_in_filters=not_in_filters,

            verbose=False,

        )

        lift = info["lift"]

        print(f"[{label}] N_hist_after={info['N_hist_after']}, "

              f"N_all_after={info['N_all_after']}, lift={lift:.3f}")

        return lift, info

    print("=== Time-split lift test ===")

    lift_early, info_early = _run_filter(hist_early, "EARLY")

    lift_late,  info_late  = _run_filter(hist_late,  "LATE")

    # Full history for comparison

    hist_full_f, total_full_f, info_full = filter_with_lift(

        hist_df=hist_df,

        total_df=total_df,

        range_filters=range_filters,

        in_filters=in_filters,

        not_in_filters=not_in_filters,

        verbose=False,

    )

    lift_full = info_full["lift"]

    print(f"[FULL]  N_hist_after={info_full['N_hist_after']}, "

          f"N_all_after={info_full['N_all_after']}, lift={lift_full:.3f}")

    return {

        "lift_early": lift_early,

        "lift_late": lift_late,

        "lift_full": lift_full,

        "info_early": info_early,

        "info_late": info_late,

        "info_full": info_full,

    }

import numpy as np

import pandas as pd

def backtest_strategy(

    hist_df: pd.DataFrame,

    strategy_fn,

    target_cols=("n1", "n2"),

    start_index: int = 50,

):

    """

    Walk-forward backtest of a strategy that predicts numbers for each draw.

    Parameters

    ----------

    hist_df : DataFrame

        Historical draws.

    strategy_fn : callable

        Function taking hist_df_up_to_t and returning an iterable of predicted numbers.

    target_cols : tuple of str

        Columns to check hits against (for example ('n1','n2') or ('st1',...,'st5')).

    start_index : int

        First draw index to start evaluating (we need some burn-in history).

    Returns

    -------

    eval_df : DataFrame

        One row per evaluated draw with:

        - draw_index

        - actual_set

        - predicted_set

        - hits

    """

    records = []

    for idx in range(start_index, len(hist_df)):

        hist_past = hist_df.iloc[:idx]

        row      = hist_df.iloc[idx]

        # Actual numbers for this draw

        actual = {int(row[c]) for c in target_cols}

        # Strategy prediction

        pred = set(int(x) for x in strategy_fn(hist_past))

        hits = len(actual & pred)

        records.append(

            {

                "draw_index": idx,

                "actual_set": actual,

                "pred_set": pred,

                "hits": hits,

            }

        )

    eval_df = pd.DataFrame(records)

    return eval_df

def monte_carlo_shuffle_backtest(

    eval_df: pd.DataFrame,

    n_trials: int = 1000,

    random_state: int | None = 42,

):

    """

    Monte Carlo permutation test: shuffle which actual draw is paired

    with which prediction and see how often we reach the real total hits.

    Parameters

    ----------

    eval_df : DataFrame

        Output of backtest_strategy().

    n_trials : int

        Number of shuffle trials.

    random_state : int or None

        Seed for reproducibility.

    Returns

    -------

    result : dict

        Contains real_total_hits, mean_mc, std_mc, z_score,

        one-sided p-value, and the array of mc_totals.

    """

    rng = np.random.default_rng(random_state)

    # Real performance

    real_total_hits = eval_df["hits"].sum()

    # Extract lists of sets to speed up intersection computations

    preds   = eval_df["pred_set"].tolist()

    actuals = eval_df["actual_set"].tolist()

    n       = len(eval_df)

    mc_totals = np.empty(n_trials, dtype=float)

    for t in range(n_trials):

        # Randomly permute which actual draw is paired with which prediction

        perm = rng.permutation(n)

        shuffled_actuals = [actuals[i] for i in perm]

        # Recompute hits under this random pairing

        hits_shuffled = [

            len(preds[k] & shuffled_actuals[k])

            for k in range(n)

        ]

        mc_totals[t] = np.sum(hits_shuffled)

    mean_mc = mc_totals.mean()

    std_mc  = mc_totals.std(ddof=1)

    if std_mc > 0:

        z_score = (real_total_hits - mean_mc) / std_mc

    else:

        z_score = np.nan

    # One-sided p-value: how often random >= real?

    p_one_sided = float((mc_totals >= real_total_hits).mean())

    result = {

        "real_total_hits": real_total_hits,

        "mean_mc": mean_mc,

        "std_mc": std_mc,

        "z_score": z_score,

        "p_one_sided": p_one_sided,

        "mc_totals": mc_totals,

    }

    print("=== Monte Carlo shuffle test ===")

    print(f"Real total hits     : {real_total_hits}")

    print(f"MC mean total hits  : {mean_mc:.3f}")

    print(f"MC std total hits   : {std_mc:.3f}")

    print(f"Z-score             : {z_score:.3f}")

    print(f"One-sided p-value   : {p_one_sided:.4f}")

    print("(Fraction of shuffles with total_hits >= real_total_hits)")

    return result
