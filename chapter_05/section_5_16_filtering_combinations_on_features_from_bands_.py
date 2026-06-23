"""
Code the Jackpot - 5.16 Filtering Combinations on Features – from bands to reduced pools
Auto-extracted (book order). Full listings, nothing truncated.
"""


# ======================================================================
# 5.16.1 What is a feature band?
# ======================================================================
bands = {
    "Odd":    [2, 4],    # we keep combos with 2, 3 or 4 odd numbers
    "triades": [5, 10],  # draws with this triad count behaved well in backtests
    "xD1":    [0, 1],    # at most 1 number with digit sum 1
    "NB1":    [0.0, 3.0] # gap-based score band from 5.15
}


# ======================================================================
# 5.16.2 Where do the bands come from?
# ======================================================================
bands["NB1"] = [0.0, 3.0]


# ======================================================================
# 5.16.4 The general filtering engine
# ======================================================================
import numpy as np
import pandas as pd


def filter_with_lift(
    hist_df,
    total_df,
    range_filters=None,
    in_filters=None,
    not_in_filters=None,
    verbose=True,
):
    """
    Apply the same feature filters to both the historical dataset (hist_df)
    and the full combination dataset (total_df), then compute the lift.

    Parameters
    ----------
    hist_df : pd.DataFrame
        Historical draws (for example ~900 rows).
    total_df : pd.DataFrame
        Total combinations (2,118,760 rows or a reduced subset).
    range_filters : dict or None
        { column_name: (low, high) }   # numeric bands L <= col <= U
    in_filters : dict or None
        { column_name: [allowed_values, ...] }     # exact values to keep
    not_in_filters : dict or None
        { column_name: [forbidden_values, ...] }   # exact values to drop
    verbose : bool
        Print a summary if True.

    Returns
    -------
    hist_f : pd.DataFrame
        Filtered historical draws.
    total_f : pd.DataFrame
        Filtered total combinations.
    summary : dict
        Counts and lift info.
    """
    # Make copies to avoid mutating originals
    hist_f = hist_df.copy()
    total_f = total_df.copy()

    N_hist_before = len(hist_df)
    N_all_before = len(total_df)

    # 1) Apply numeric bands
    if range_filters is not None:
        for col, (low, high) in range_filters.items():
            if (col not in hist_f.columns) or (col not in total_f.columns):
                continue  # quietly ignore unknown columns

            hist_f = hist_f[hist_f[col].between(low, high)]
            total_f = total_f[total_f[col].between(low, high)]

    # 2) Apply "must be in this list" filters
    if in_filters is not None:
        for col, values in in_filters.items():
            if (col not in hist_f.columns) or (col not in total_f.columns):
                continue

            hist_f = hist_f[hist_f[col].isin(values)]
            total_f = total_f[total_f[col].isin(values)]

    # 3) Apply "must NOT be in this list" filters
    if not_in_filters is not None:
        for col, values in not_in_filters.items():
            if (col not in hist_f.columns) or (col not in total_f.columns):
                continue

            hist_f = hist_f[~hist_f[col].isin(values)]
            total_f = total_f[~total_f[col].isin(values)]

    # 4) Lift calculation
    N_hist_after = len(hist_f)
    N_all_after = len(total_f)

    if N_all_before == 0 or N_all_after == 0:
        base_rate = np.nan
        filtered_rate = np.nan
        lift = np.nan
    else:
        base_rate = N_hist_before / N_all_before
        filtered_rate = (N_hist_after / N_all_after) if N_all_after > 0 else np.nan
        lift = (filtered_rate / base_rate) if base_rate > 0 else np.nan

    summary = {
        "N_all_before": N_all_before,
        "N_hist_before": N_hist_before,
        "N_all_after": N_all_after,
        "N_hist_after": N_hist_after,
        "base_rate": base_rate,
        "filtered_rate": filtered_rate,
        "lift": lift,
    }

    if verbose:
        print("=== Filter summary ===")
        print("Total combinations : before =", N_all_before,
              " after =", N_all_after)
        print("Historical draws   : before =", N_hist_before,
              " after =", N_hist_after)
        print("Base hit rate      :", round(base_rate, 12))
        print("Filtered hit rate  :", round(filtered_rate, 12))
        print("Lift               :", round(lift, 3))

    return hist_f, total_f, summary


# ======================================================================
# 5.16.5 Turning a bands dictionary into filters
# ======================================================================
def bands_to_range_filters(bands):
    """
    Convert a bands dictionary like:

        bands = {
            "Odd":    [2, 4],
            "triades": [5, 10],
            "xD1":    [0, 1],
        }

    into the {col: (L, U)} form expected by filter_with_lift.
    """
    if bands is None:
        return None

    range_filters = {}
    for col, band in bands.items():
        if band is None or len(band) != 2:
            continue
        low, high = band
        range_filters[col] = (low, high)
    return range_filters

def run_feature_filter(
    hist_df,
    total_df,
    bands,
    include_values=None,
    exclude_values=None,
    export_path=None,
    verbose=True,
):
    """
    Apply feature bands and value-based filters to hist_df and total_df.

    Parameters
    ----------
    hist_df, total_df : DataFrames
        Historical draws and full space with feature columns.
    bands : dict
        { feature_name: [L, U], ... }
    include_values : dict or None
        { feature_name: [allowed_values, ...], ... }
    exclude_values : dict or None
        { feature_name: [forbidden_values, ...], ... }
    export_path : str or None
        If given, save the filtered total_df (only 5-number columns by default)
        to this CSV file.
    verbose : bool
        If True, print report and lift.

    Returns
    -------
    hist_f, total_f, summary
    """
    range_filters = bands_to_range_filters(bands)

    hist_f, total_f, summary = filter_with_lift(
        hist_df=hist_df,
        total_df=total_df,
        range_filters=range_filters,
        in_filters=include_values,
        not_in_filters=exclude_values,
        verbose=verbose,
    )

    # Optional: export the reduced pool for the next draw
    if export_path is not None:
        cols_to_save = [c for c in ["st1", "st2", "st3", "st4", "st5"] if c in total_f.columns]
        # You can of course keep more columns if you want
        total_f[cols_to_save].to_csv(export_path, index=False)
        if verbose:
            print(f"Filtered pool saved to: {export_path}")

    return hist_f, total_f, summary

bands = {
    "Odd":     [2, 4],
    "Sum":     [100, 200],
    "AC":      [0, 15],
    "NB1":     [0.0, 3.0],
    "triades": [4, 9],
}

include_values = {
    # Only keep combinations whose HCFS_code is one of these patterns
    "HCFS_code": [2102, 2012, 1112],
}

exclude_values = {
    # Throw away combinations with too many consecutive numbers
    "Con": [3, 4, 5],
}

hist_f, total_f, info = run_feature_filter(
    hist_df=hist_df,
    total_df=total_df,
    bands=bands,
    include_values=include_values,
    exclude_values=exclude_values,
    export_path="data/ej_reduced_pool_next_draw.csv",
    verbose=True,
)

print("Space fraction:", info["N_all_after"] / info["N_all_before"])
print("Lift:", round(info["lift"], 3))


# ======================================================================
# 5.16.6 Filtering on specific values: must-have and must-avoid
# ======================================================================
# Keep only certain shapes and delay patterns
include_values = {
    "OSLCC":   [34231, 33321, 33221],
    "combiDx": [2102, 1101],
}

# Throw away combinations that are too symmetrical
exclude_values = {
    "compl": [3],   # drop combis with 3 complementary pairs
    "HS":    [2],   # maybe you hate draws with two horizontal symmetries
}

hist_f, total_f, info = run_feature_filter(
    hist_df,
    total_df,
    bands=bands,
    include_values=include_values,
    exclude_values=exclude_values,
    export_path=None,
)
