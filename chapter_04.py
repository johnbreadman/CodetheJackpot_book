"""
Code the Jackpot - Chapter 4 - Features Creation
Auto-extracted (book order). Full listings, nothing truncated.
"""


# ======================================================================
# Evaluating Filter Quality: The Role of Lift
# ======================================================================
def reducing_metrics(n, df, df_n, df1, df2):
    len_df = len(df)      # total combinations AFTER current filter
    len_df_n = len(df_n)  # historical hits AFTER current filter
    len_df1 = len(df1)    # total combinations BEFORE any filter
    len_df2 = len(df2)    # historical hits BEFORE any filter

    df_ratio = round(len_df / len_df1, 3) if len_df1 != 0 else 0
    df_n_ratio = round(len_df_n / len_df2, 3) if len_df2 != 0 else 0
    ratio_of_ratios = round(df_n_ratio / df_ratio, 3) if df_ratio != 0 else 0

    print(
        n,
        len_df, len_df_n,
        len_df1 - len_df,      # removed combos
        len_df2 - len_df_n,    # removed historical draws
        df_ratio, df_n_ratio,
        ratio_of_ratios
    )

import numpy as np

def compute_overall_lift(hist_full, total_full, hist_filtered, total_filtered):
    """
    Compute overall lift after applying one or more filters.

    hist_full      : original historical draws (df2)
    total_full     : original total combinations (df1)
    hist_filtered  : filtered historical draws
    total_filtered : filtered total combinations
    """
    N_hist_before = len(hist_full)
    N_all_before = len(total_full)
    N_hist_after = len(hist_filtered)
    N_all_after = len(total_filtered)

    if N_all_before == 0 or N_all_after == 0:
        return np.nan

    base_rate = N_hist_before / N_all_before
    filtered_rate = N_hist_after / N_all_after if N_all_after > 0 else np.nan

    if base_rate == 0:
        return np.nan

    return filtered_rate / base_rate

lift = compute_overall_lift(hist_df, total_df, hist_f, total_f)

print("Original space   :", len(total_df), "combinations,", len(hist_df), "historical draws")
print("Filtered space   :", len(total_f), "combinations,", len(hist_f), "historical draws")
print("Overall lift     :", round(lift, 3))

import pandas as pd
import numpy as np

def filter_with_lift(
    hist_df,
    total_df,
    range_filters=None,
    in_filters=None,
    not_in_filters=None,
    verbose=True
):
    """
    Apply filters on both the historical dataset and the total combinations dataset,
    and compute the overall lift.

    Parameters
    ----------
    hist_df : pd.DataFrame
        Historical draws.
    total_df : pd.DataFrame
        Total combinations.
    range_filters : dict, optional
        Dict of {column: (lower, upper)} for numeric range filters.
    in_filters : dict, optional
        Dict of {column: [allowed_values]}.
    not_in_filters : dict, optional
        Dict of {column: [forbidden_values]}.
    verbose : bool
        If True, print counts and lift.

    Returns
    -------
    hist_f : pd.DataFrame
        Filtered historical draws.
    total_f : pd.DataFrame
        Filtered total combinations.
    summary : dict
        Summary with counts and lift.
    """

    # Keep copies so we do not overwrite original data
    hist_f = hist_df.copy()
    total_f = total_df.copy()

    N_hist_before = len(hist_df)
    N_all_before = len(total_df)

    # 1) Range filters
    if range_filters is not None:
        for col, (low, high) in range_filters.items():
            if col in hist_f.columns and col in total_f.columns:
                hist_f = hist_f[hist_f[col].between(low, high)]
                total_f = total_f[total_f[col].between(low, high)]

    # 2) "IN" filters (keep only given values)
    if in_filters is not None:
        for col, values in in_filters.items():
            if col in hist_f.columns and col in total_f.columns:
                hist_f = hist_f[hist_f[col].isin(values)]
                total_f = total_f[total_f[col].isin(values)]

    # 3) "NOT IN" filters (drop given values)
    if not_in_filters is not None:
        for col, values in not_in_filters.items():
            if col in hist_f.columns and col in total_f.columns:
                hist_f = hist_f[~hist_f[col].isin(values)]
                total_f = total_f[~total_f[col].isin(values)]

    # Counts after filtering
    N_hist_after = len(hist_f)
    N_all_after = len(total_f)

    # Lift computation
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
        print("Base hit rate      :", round(summary["base_rate"], 10))
        print("Filtered hit rate  :", round(summary["filtered_rate"], 10))
        print("Lift               :", round(summary["lift"], 3))

    return hist_f, total_f, summary

range_filters = {
    "AC":  (20, 60),
    "Sum": (100, 200),
}

in_filters = {
    "Odd": [2, 3],
}

not_in_filters = {
    "Con": [4, 5],
}

hist_f, total_f, info = filter_with_lift(
    hist_df=hist_df,
    total_df=total_df,
    range_filters=range_filters,
    in_filters=in_filters,
    not_in_filters=not_in_filters,
    verbose=True,
)


# ======================================================================
# Comparing Filter Recipes: Strategic Choices
# ======================================================================
def calculate_delaypercent(df_n, df2):

    indices = list(df_n.index)

    indices_diffs = [indices[0]] + [indices[i] - indices[i - 1]

                                    for i in range(1, len(indices))] + [len(df2) - indices[-1]]

    print(len(indices))

    percentile_results = pd.DataFrame()

    stats_dict = {

        'column_name': 'termscombi',

        'emf': len(indices_diffs) - 1,

        'kath': indices_diffs[-1],

        'median': int(np.percentile(indices_diffs, 50)),

        'P75': int(np.percentile(indices_diffs, 75)),

        'P90': int(np.percentile(indices_diffs, 90)),

        'P95': int(np.percentile(indices_diffs, 95)),

        'P99': int(np.percentile(indices_diffs, 99)),

        'max': int(np.max(indices_diffs)),

        'Pct_score': int(stats.percentileofscore(indices_diffs, indices_diffs[-1]))

    }

    percentile_results = pd.concat(

        [percentile_results, pd.DataFrame([stats_dict])], ignore_index=True)

    print(percentile_results)

    print(indices_diffs[-20:])

    last_value = indices_diffs[-1:][0]

    unique_values = list(set(indices_diffs))

    percentile_results = pd.DataFrame()

    index_diff_dict = {}

    for v in unique_values:

        index_diff_dict[v] = [index for index,

                              value in enumerate(indices_diffs) if value == v]

    last_index_diffs = [index_diff_dict[last_value][0]] + [index_diff_dict[last_value][i] - index_diff_dict[last_value][i - 1]

                                                           for i in range(1, len(index_diff_dict[last_value]))] + [len(indices) - index_diff_dict[last_value][-1]]

    for v in index_diff_dict.keys():

        indices_diffs = [index_diff_dict[v][0]] + [index_diff_dict[v][i] - index_diff_dict[v][i - 1]

                                                   for i in range(1, len(index_diff_dict[v]))] + [len(indices) - index_diff_dict[v][-1]]

        # Calculate percentiles and other stats

        stats_dict = {

            'column_name': v,

            'emf': len(indices_diffs) - 1,

            'kath': indices_diffs[-1],

            'median': int(np.percentile(indices_diffs, 50)),

            'P75': int(np.percentile(indices_diffs, 75)),

            'P90': int(np.percentile(indices_diffs, 90)),

            'P95': int(np.percentile(indices_diffs, 95)),

            'P99': int(np.percentile(indices_diffs, 99)),

            'max': int(np.max(indices_diffs)),

            'Pct_score': int(stats.percentileofscore(indices_diffs, indices_diffs[-1]))

        }

        percentile_results = pd.concat(

            [percentile_results, pd.DataFrame([stats_dict])], ignore_index=True)

    percentile_results.sort_values(by=['kath', 'Pct_score'], ascending=[

                                   False, False], inplace=True)

    percentile_results['Norm'] = (

        100*percentile_results['emf']/percentile_results['emf'].sum()).astype(int)

    percentile_results = percentile_results.reset_index(drop=True)

    print(percentile_results)

    print(last_index_diffs[-20:])

    # Calculate percentiles and other stats

    stats_dict_last = {

        'column_name': last_value,

        'emf': len(last_index_diffs) - 1,

        'kath': last_index_diffs[-2],

        'median': int(np.percentile(last_index_diffs, 50)),

        'P75': int(np.percentile(last_index_diffs, 75)),

        'P90': int(np.percentile(last_index_diffs, 90)),

        'P95': int(np.percentile(last_index_diffs, 95)),

        'P99': int(np.percentile(last_index_diffs, 99)),

        'max': int(np.max(last_index_diffs)),

        'Pct_score': int(stats.percentileofscore(last_index_diffs, last_index_diffs[-2]))

    }

print(stats_dict_last)


# ======================================================================
# Python Engine for Inherent Features
# ======================================================================
import numpy as np

import pandas as pd

from itertools import combinations

# ============================================================

# Global grid settings for EuroJackpot 1–50 laid out as 10×5

# ============================================================

GRID_ROWS = 10

GRID_COLS = 5

# ============================================================

# Helpers: number ↔ (row, col) on the 10×5 grid

# ============================================================

def number_to_row_col(n, rows=GRID_ROWS, cols=GRID_COLS):

    """

    Map a number n in 1..(rows*cols) to 1-based (row, col) indices.

    EuroJackpot main grid uses rows=10, cols=5.

    """

    n0 = int(n) - 1

    row = n0 // cols + 1       # 1..rows

    col = n0 % cols + 1        # 1..cols

    return row, col

# ============================================================

# 1. Basic arithmetic profile: Odd, Small, Sum, Span

# ============================================================

def basic_arithmetic_features(nums, small_threshold=25):

    """

    Basic arithmetic traits for a 5-number line:

        Odd   : count of odd numbers (0..5)

        Small : count of numbers <= small_threshold (0..5)

        Sum   : sum of the five numbers

        Span  : max - min

    """

    arr = np.sort(np.array(nums, dtype=int))

    odd = int(np.sum(arr % 2 == 1))

    small = int(np.sum(arr <= small_threshold))

    total_sum = int(arr.sum())

    span = int(arr[-1] - arr[0])

    return {

        "Odd": odd,

        "Small": small,

        "Sum": total_sum,

        "Span": span,

    }

# ============================================================

# 2. Grid footprint: Lines, Columns, L1..L10, C1..C5, LL, CC

# ============================================================

def grid_footprint_features(nums, rows=GRID_ROWS, cols=GRID_COLS):

    """

    Grid footprint of a 5-number line on the 10×5 ticket.

    Returns:

        Lines : number of distinct rows used

        Cols  : number of distinct columns used

        L1..L10 : counts per row

        C1..C5  : counts per column

        LL    : row pattern code as an integer, formed by concatenating L1..L10

        CC    : column pattern code as an integer, formed by concatenating C1..C5

    """

    arr = np.array(nums, dtype=int)

    # Convert to row/col (1-based), then to 0-based indices for bincount

    rc = [number_to_row_col(n, rows=rows, cols=cols) for n in arr]

    r_arr = np.array([r for (r, c) in rc], dtype=int) - 1

    c_arr = np.array([c for (r, c) in rc], dtype=int) - 1

    line_counts = np.bincount(r_arr, minlength=rows)   # length 10

    col_counts = np.bincount(c_arr, minlength=cols)    # length 5

    lines_used = int(np.count_nonzero(line_counts))

    cols_used = int(np.count_nonzero(col_counts))

    # LL as concatenation of digits L1..L10, CC as C1..C5

    ll_str = "".join(str(int(c)) for c in line_counts)

    cc_str = "".join(str(int(c)) for c in col_counts)

    # Convert to integer (leading zeros in string are fine)

    LL = int(ll_str)

    CC = int(cc_str)

    result = {

        "Lines": lines_used,

        "Cols": cols_used,

        "LL": LL,

        "CC": CC,

    }

    # Attach L1..L10 and C1..C5

    for i, cnt in enumerate(line_counts, start=1):

        result[f"L{i}"] = int(cnt)

    for j, cnt in enumerate(col_counts, start=1):

        result[f"C{j}"] = int(cnt)

    return result

# ============================================================

# 3. Consecutive numbers + OSLCC fingerprint

# ============================================================

def consecutive_and_shape_features(sorted_nums, basic_dict, grid_dict):

    """

    For a sorted 5-number line, compute:

        Con   : number of consecutive pairs (gap=1)

        OSLCC : 5-digit shape code combining

                O = Odd

                S = Small

                L = Lines

                C = Cols

                C = Con

    """

    arr = np.array(sorted_nums, dtype=int)

    diffs = np.diff(arr)  # length 4

    con = int(np.sum(diffs == 1))

    O = basic_dict["Odd"]

    S = basic_dict["Small"]

    L = grid_dict["Lines"]

    C = grid_dict["Cols"]

    # OSLCC = O S L C Con as a 5-digit code

    OSLCC = int(10000 * O + 1000 * S + 100 * L + 10 * C + con)

    return {

        "Con": con,

        "OSLCC": OSLCC,

    }

# ============================================================

# 4. Difference structure: D1..D4, sameDs, Diffcombi, OddDs, SmallDs, Df<10, AC

# ============================================================

def difference_features(sorted_nums,

                        small_diff_threshold=23,

                        tight_threshold=10):

    """

    For sorted 5-number line:

        D1..D4      : consecutive gaps

        sameDs      : count of distinct values among D1..D4

        Diffcombi   : integer code formed as two-digit blocks D1D2D3D4 (e.g. [1,11,1,16] -> 01011116)

        OddDs       : how many gaps are odd

        SmallDs     : how many gaps are <= small_diff_threshold (default 23)

        Df<10       : how many gaps are <= tight_threshold (default 10)

    """

    arr = np.array(sorted_nums, dtype=int)

    diffs = np.diff(arr)

    if diffs.size != 4:

        raise ValueError("Expected 5 numbers to compute 4 consecutive differences.")

    D1, D2, D3, D4 = map(int, diffs)

    unique_gaps = set(int(d) for d in diffs)

    sameDs = len(unique_gaps)

    # Encode as two-digit blocks, e.g. [1,11,1,16] -> "01011116"

    diff_str = "".join(f"{int(d):02d}" for d in diffs)

    Diffcombi = int(diff_str)

    oddDs = int(np.sum(diffs % 2 == 1))

    smallDs = int(np.sum(diffs <= small_diff_threshold))

    df_lt_10 = int(np.sum(diffs <= tight_threshold))

    return {

        "D1": D1,

        "D2": D2,

        "D3": D3,

        "D4": D4,

        "sameDs": sameDs,

        "Diffcombi": Diffcombi,

        "OddDs": oddDs,

        "SmallDs": smallDs,

        "Df<10": df_lt_10,

    }

def arithmetic_complexity(sorted_nums):

    """

    Arithmetic Complexity (AC) for a 5-number line, defined as:

        AC = (# of distinct positive pairwise differences) - (r - 1)

    where r is the number of numbers (5 here).

    """

    arr = np.array(sorted_nums, dtype=int)

    r = arr.size

    if r < 2:

        return {"AC": 0}

    diffs = set()

    # all positive pairwise differences

    for i, j in combinations(range(r), 2):

        d = int(arr[j] - arr[i])

        if d > 0:

            diffs.add(d)

    ac_value = int(len(diffs) - (r - 1))

    return {"AC": ac_value}

# ============================================================

# 5. Symmetry and complementary pairs: HS, VS, compl

# ============================================================

def _sym_horizontal(n, rows=GRID_ROWS, cols=GRID_COLS):

    """

    Horizontal symmetry: mirror around vertical axis through column 3.

    Column indices 1↔5, 2↔4, 3 stays.

    """

    row, col = number_to_row_col(n, rows=rows, cols=cols)

    col_mirror = cols + 1 - col

    return (row - 1) * cols + col_mirror

def _sym_vertical(n, rows=GRID_ROWS, cols=GRID_COLS):

    """

    Vertical symmetry: mirror around horizontal line between rows 5 and 6.

    Row indices 1↔10, 2↔9, 3↔8, 4↔7, 5↔6.

    """

    row, col = number_to_row_col(n, rows=rows, cols=cols)

    row_mirror = rows + 1 - row

    return (row_mirror - 1) * cols + col

def symmetry_and_complement_features(nums,

                                     rows=GRID_ROWS,

                                     cols=GRID_COLS):

    """

    For a 5-number line, compute:

        HS    : count of horizontal symmetric pairs

        VS    : count of vertical symmetric pairs

        compl : count of complementary pairs (n, 51-n)

    """

    arr = np.sort(np.array(nums, dtype=int))

    present = set(arr.tolist())

    HS_pairs = 0

    VS_pairs = 0

    compl_pairs = 0

    for a in arr:

        a = int(a)

        # horizontal

        b_h = _sym_horizontal(a, rows=rows, cols=cols)

        if b_h in present and a < b_h:

            HS_pairs += 1

        # vertical

        b_v = _sym_vertical(a, rows=rows, cols=cols)

        if b_v in present and a < b_v:

            VS_pairs += 1

        # complementary (central symmetry): n ↔ 51-n

        b_c = 51 - a

        if b_c in present and a < b_c:

            compl_pairs += 1

    return {

        "HS": int(HS_pairs),

        "VS": int(VS_pairs),

        "compl": int(compl_pairs),

    }

# ============================================================

# 6. Digit-sum groups: xD1..xD13 and SD

# ============================================================

def digit_sum_features(nums, max_sd=13):

    """

    Digit-sum features for a 5-number line.

        xDk : how many numbers have digit sum == k  (k=1..max_sd)

        SD  : how many digit-sum groups appear at least once

    """

    arr = np.array(nums, dtype=int)

    digit_sums = [sum(int(d) for d in str(int(x))) for x in arr]

    counts = [digit_sums.count(sd) for sd in range(1, max_sd + 1)]

    result = {}

    for sd_val, cnt in enumerate(counts, start=1):

        result[f"xD{sd_val}"] = int(cnt)

    # number of groups with count > 0

    sd_groups = int(sum(1 for cnt in counts if cnt > 0))

    result["SD"] = sd_groups

    return result

# ============================================================

# 7. One-line wrapper: compute all inherent features

# ============================================================

def compute_inherent_features_for_line(st_values):

    """

    Compute the full inherent feature fingerprint for a single line.

    st_values: iterable of the 5 main numbers (st1..st5).

    Returns a dict with:

        Odd, Small, Sum, Span,

        Lines, Cols, L1..L10, C1..C5, LL, CC,

        Con, OSLCC,

        D1..D4, sameDs, Diffcombi, OddDs, SmallDs, Df<10, AC,

        HS, VS, compl,

        xD1..xD13, SD

    """

    arr = np.sort(np.array(st_values), axis=None)

    basic = basic_arithmetic_features(arr)

    grid = grid_footprint_features(arr)

    cons = consecutive_and_shape_features(arr, basic, grid)

    diff = difference_features(arr)

    ac = arithmetic_complexity(arr)

    sym = symmetry_and_complement_features(arr)

    digits = digit_sum_features(arr)

    features = {}

    features.update(basic)

    features.update(grid)

    features.update(cons)

    features.update(diff)

    features.update(ac)

    features.update(sym)

    features.update(digits)

    return features

# ============================================================

# 8. DataFrame-level wrappers for hist_df and total_df

# ============================================================

def add_inherent_features(df, st_cols=("st1", "st2", "st3", "st4", "st5")):

    """

    Given a DataFrame with columns st1..st5, compute all inherent features

    for every row and return a new DataFrame with extra columns added.

    This works for both:

        - hist_df  : historical draws

        - total_df : all combinations

    """

    feature_rows = []

    # iterate over all lines

    for _, row in df.loc[:, st_cols].iterrows():

        nums = [row[c] for c in st_cols]

        feature_rows.append(compute_inherent_features_for_line(nums))

    feat_df = pd.DataFrame(feature_rows, index=df.index)

    df_out = df.copy()

    for col in feat_df.columns:

        df_out[col] = feat_df[col]

    return df_out

# ============================================================

# 9. Helper to update hist_df after a new draw

# ============================================================

def update_hist_after_new_draw(hist_df,

                               new_draw,

                               st_cols=("st1", "st2", "st3", "st4", "st5"),

                               reset_index=False):

    """

    Append a new draw to hist_df and compute inherent features for that draw.

    Parameters

    ----------

    hist_df : existing historical DataFrame (already with or without feature columns)

    new_draw : either

        - dict with keys st1..st5 (and optionally other fields like 'date'),

        - or a list/tuple of 5 integers for st1..st5.

    st_cols : names of the 5 main number columns.

    reset_index : if True, reset index after concatenation.

    Returns

    -------

    hist_updated : DataFrame with the new row and all inherent features filled

                   for that row.

    """

    # Build a one-row DataFrame for the new draw

    if isinstance(new_draw, dict):

        new_row_df = pd.DataFrame([new_draw])

        # Make sure st1..st5 exist

        missing = [c for c in st_cols if c not in new_row_df.columns]

        if missing:

            raise ValueError(f"new_draw dict is missing keys: {missing}")

    else:

        # Assume it's an iterable of 5 numbers

        if len(new_draw) != 5:

            raise ValueError("new_draw sequence must have length 5.")

        new_row_df = pd.DataFrame([list(new_draw)], columns=list(st_cols))

    # Compute inherent features for the new row only

    new_row_df = add_inherent_features(new_row_df, st_cols=st_cols)

    # Concatenate with existing history

    hist_updated = pd.concat([hist_df, new_row_df], axis=0)

    if reset_index:

        hist_updated = hist_updated.reset_index(drop=True)

    return hist_updated

# ============================================================

# 10. Helper to fill feature columns on total_df (all 5/50 combos)

# ============================================================

def build_total_features(total_df,

                         st_cols=("st1", "st2", "st3", "st4", "st5")):

    """

    Given total_df with all 2,118,760 combinations (or any reduced subset),

    return a copy with all inherent feature columns added.

    Inherent features do not depend on history, so you only need to run this

    once for a given total_df structure.

    """

    return add_inherent_features(total_df, st_cols=st_cols)


# ======================================================================
# Hot, Cold, Fast, and Slow (HCFS)
# ======================================================================
import numpy as np
import pandas as pd

def update_Numb3rs(df):
    """
    Build the per-number status table (numb3rs) for a 5/50 game.

    df: historical draws with columns [Date, st1, st2, st3, st4, st5, ...]

    Returns a DataFrame with columns:
      No, Freq, Delay, Norm, FS, HC, HCFS
    """
    # Structure per number: [No, Freq, Delay, Norm]
    hcfs = np.zeros((50, 4), dtype=float)
    hcfs[:, 0] = np.arange(1, 51)  # numbers 1..50

    # Walk through all draws in order
    for _, row in df.iterrows():
        # increase Delay for all numbers
        hcfs[:, 2] += 1

        # update counts and reset Delay for drawn numbers
        drawn_numbers = row[['st1', 'st2', 'st3', 'st4', 'st5']].astype(int).values - 1
        hcfs[drawn_numbers, 1] += 1
        hcfs[drawn_numbers, 2] = 0

    total_draws = df.shape[0]

    # Norm is the average spacing between hits for each number
    norms = np.where(hcfs[:, 1] > 0, total_draws / hcfs[:, 1], 0)
    hcfs[:, 3] = norms

    numb3rs = pd.DataFrame(hcfs, columns=['No', 'Freq', 'Delay', 'Norm'])
    numb3rs[['No', 'Freq', 'Delay']] = numb3rs[['No', 'Freq', 'Delay']].astype(int)

    # mean frequency across all numbers
    mean_freq = numb3rs['Freq'].mean()

    # Fast / Slow based on Freq
    numb3rs['FS'] = np.where(numb3rs['Freq'] > mean_freq, 'F', 'S')

    # Hot / Cold based on Delay vs Norm
    numb3rs['HC'] = np.where(
        (numb3rs['Norm'] > 0) & (numb3rs['Delay'] < numb3rs['Norm']),
        'H',
        'C'
    )

    numb3rs['HCFS'] = numb3rs['HC'] + numb3rs['FS']

    return numb3rs


# ======================================================================
# Synthetic Combination Codes (HCFS, combiDx, combiKx)
# ======================================================================
def create_combi_column(df_, column_name, window=20):
    """
    For each row i >= window, look back `window` rows in `column_name` and
    count how many times the current value appears in the last 5, 10, 15 and
    20 rows. These four counts are concatenated into a 4-digit integer.

    Example: counts = (2, 1, 0, 2) -> combi = 2102
    """
    combi = [0] * len(df_)

    for i in range(window, len(df_)):
        current_value = df_.loc[i, column_name]
        previous_values = df_.loc[i-window:i-1, column_name]

        # Counts inside sliding subwindows
        count_1_5  = int(previous_values.tail(5).eq(current_value).sum())
        count_1_10 = int(previous_values.tail(10).eq(current_value).sum())
        count_1_15 = int(previous_values.tail(15).eq(current_value).sum())
        count_1_20 = int(previous_values.tail(20).eq(current_value).sum())

        combi[i] = int(f"{count_1_5}{count_1_10}{count_1_15}{count_1_20}")

    return combi


# ======================================================================
# Updating hist_df and total_df After a New Draw
# ======================================================================
import numpy as np
import pandas as pd

# 1) D-values for a single row
def compute_D_values(row, st_cols=('st1', 'st2', 'st3', 'st4', 'st5')):
    nums = row[list(st_cols)].astype(int).values
    nums = np.sort(nums)
    diffs = np.diff(nums)  # length 4
    return diffs  # array([D1, D2, D3, D4])


# 2) Update x1..x20 and Dx1..Dx20 for the last row of hist_df
def update_overlap_features(hist_df, n_prev=20, st_cols=('st1', 'st2', 'st3', 'st4', 'st5')):
    idx = len(hist_df) - 1
    if idx <= 0:
        return hist_df

    current = hist_df.iloc[idx]
    current_set = set(current[list(st_cols)].astype(int).values)
    current_D = compute_D_values(current, st_cols=st_cols)
    current_D_set = set(current_D.tolist())

    for k in range(1, n_prev + 1):
        col_x = f"x{k}"
        col_Dx = f"Dx{k}"

        if idx - k < 0:
            hist_df.loc[idx, col_x] = np.nan
            hist_df.loc[idx, col_Dx] = np.nan
            continue

        prev = hist_df.iloc[idx - k]
        prev_set = set(prev[list(st_cols)].astype(int).values)
        prev_D = compute_D_values(prev, st_cols=st_cols)
        prev_D_set = set(prev_D.tolist())

        hist_df.loc[idx, col_x] = len(current_set & prev_set)
        hist_df.loc[idx, col_Dx] = len(current_D_set & prev_D_set)

    return hist_df


# 3) Update k1..k5 (draws since last hit for each drawn number)
def update_k_values(hist_df, st_cols=('st1', 'st2', 'st3', 'st4', 'st5')):
    idx = len(hist_df) - 1
    if idx < 0:
        return hist_df

    current = hist_df.iloc[idx]
    prev = hist_df.iloc[:idx]

    nums = current[list(st_cols)].astype(int).values

    for pos, n in enumerate(nums, start=1):
        if prev.empty:
            k = idx + 1
        else:
            mask = (prev[list(st_cols)] == n).any(axis=1)
            indices = np.where(mask.values)[0]
            if len(indices) == 0:
                k = idx + 1
            else:
                last_hit = indices[-1]
                k = idx - last_hit
        hist_df.loc[idx, f"k{pos}"] = int(k)

    # Optional: aggregate statistics
    k_values = [hist_df.loc[idx, f"k{p}"] for p in range(1, 6)]
    hist_df.loc[idx, "k_min"] = int(min(k_values))
    hist_df.loc[idx, "k_max"] = int(max(k_values))
    hist_df.loc[idx, "k_mean"] = float(np.mean(k_values))

    return hist_df


# 4) Update combiDx and combiKx for the last row
def update_combi_codes(hist_df):
    idx = len(hist_df) - 1
    if idx < 20:
        return hist_df

    for col_name, combi_col in [("Dx", "combiDx"), ("kx", "combiKx")]:
        if col_name not in hist_df.columns:
            continue

        # Build the combi value only for last row using the same logic
        window = 20
        current_value = hist_df.loc[idx, col_name]
        prev_vals = hist_df.loc[idx-window:idx-1, col_name]

        c5  = int(prev_vals.tail(5).eq(current_value).sum())
        c10 = int(prev_vals.tail(10).eq(current_value).sum())
        c15 = int(prev_vals.tail(15).eq(current_value).sum())
        c20 = int(prev_vals.tail(20).eq(current_value).sum())

        hist_df.loc[idx, combi_col] = int(f"{c5}{c10}{c15}{c20}")

    return hist_df


# 5) Apply HCFS to all combinations in total_df
def apply_HCFS_to_total(total_df, numb3rs, st_cols=('st1', 'st2', 'st3', 'st4', 'st5')):
    """
    total_df: all 5/50 combinations with at least columns st1..st5.
    numb3rs: per-number table from update_Numb3rs (must contain No and HCFS).
    """
    state_map = numb3rs.set_index('No')['HCFS'].to_dict()

    def encode_row(row):
        tags = [state_map[int(row[c])] for c in st_cols]
        # counts in fixed HF/HS/CF/CS order
        cnt = {'HF': 0, 'HS': 0, 'CF': 0, 'CS': 0}
        for t in tags:
            cnt[t] += 1
        code = int(f"{cnt['HF']}{cnt['HS']}{cnt['CF']}{cnt['CS']}")
        pattern = ''.join(tags)
        return pd.Series({'HCFS_pattern': pattern, 'HCFS_code': code})

    total_df[['HCFS_pattern', 'HCFS_code']] = total_df.apply(encode_row, axis=1)
    return total_df


# 6) High-level update after appending a new draw row to hist_df
def update_after_new_draw(hist_df, total_df):
    """
    Call this after you append the new EuroJackpot draw to hist_df.
    It updates dynamic features in hist_df and then refreshes HCFS-based
    columns in total_df.
    """
    # Rebuild numb3rs from the updated history
    numb3rs = update_Numb3rs(hist_df)

    # Overlaps and k-values for the last row
    hist_df = update_overlap_features(hist_df, n_prev=20)
    hist_df = update_k_values(hist_df)

    # If you maintain Dx and kx columns, update their combi codes
    hist_df = update_combi_codes(hist_df)

    # Refresh HCFS-based features for the full combination space
    total_df = apply_HCFS_to_total(total_df, numb3rs)

    return hist_df, total_df, numb3rs
