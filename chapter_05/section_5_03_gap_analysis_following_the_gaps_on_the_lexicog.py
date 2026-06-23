"""
Code the Jackpot - 5.3 Gap Analysis: Following the Gaps on the Lexicographic Index
Auto-extracted (book order). Full listings, nothing truncated.
"""


# ======================================================================
# From Combination to Lexicographic Index
# ======================================================================
import math
from functools import lru_cache

@lru_cache(maxsize=None)
def A_optimized(n, r, k, l):
    # Helper: sum_{j=0..l-1} C(n-(j+1), r-k)
    # n: size of main number pool (e.g. 45 or 50)
    # r: numbers per combination (5)
    # k: position index (1..5)
    # l: how many initial values we skip at this position
    if l <= 0:
        return 0
    return sum(math.comb(n - (j + 1), r - k) for j in range(l))


def lex_index(st, n_main=50, r=5):
    # Compute lexicographic index (0-based) for a sorted combination 'st'.
    # st    : list/tuple with r sorted numbers, e.g. [3, 14, 22, 34, 45]
    # n_main: size of the main number pool (50 for EuroJackpot, 45 for Joker)
    # r     : numbers in a combination (5)
    st = sorted(st)
    a = A_optimized(n_main, r, 1, st[0] - 1)
    for k in range(1, len(st)):
        a += (
            A_optimized(n_main, r, k + 1, st[k] - 1)
            - A_optimized(n_main, r, k + 1, st[k - 1])
        )
    return a


def ensure_stidx(df_hist, n_main=50, r=5):
    # Add stidx column to df_hist if missing.
    # Assumes columns st1..st5 exist and df_hist is sorted by draw date.
    df = df_hist.copy()
    if 'stidx' not in df.columns:
        df['stidx'] = df[['st1', 'st2', 'st3', 'st4', 'st5']].apply(
            lambda row: lex_index(tuple(row.values), n_main=n_main, r=r),
            axis=1
        )
    return df


# ======================================================================
# Enclosing Gaps Around Each Draw
# ======================================================================
import numpy as np
import pandas as pd
from scipy.stats import percentileofscore

def compute_gap_table(data_subset, max_index):
    # Compute for each draw its enclosing gap (lowerbound, upperbound) and gap_size,
    # as well as the percentile of that gap size among all previous gaps.
    #
    # data_subset: DataFrame with ['st1','st2','st3','st4','st5','stidx'],
    #              sorted by draw order.
    # max_index : last lex index in the universe (e.g. C(50,5)-1 = 2_118_759).

    gap_sizes = []
    percentiles = []
    lower_bound_l = []
    upper_bound_l = []

    for i in range(1, len(data_subset)):
        current_stidx = data_subset['stidx'].iloc[i]
        previous_draws_subset = sorted(data_subset['stidx'].iloc[:i].values)

        # Find the indices that encompass the current index
        lower_bound = max(
            [idx for idx in previous_draws_subset if idx < current_stidx],
            default=0
        )
        upper_bound = min(
            [idx for idx in previous_draws_subset if idx > current_stidx],
            default=max_index
        )

        lower_bound_l.append(lower_bound)
        upper_bound_l.append(upper_bound)

        # Gap size between those bounds
        gap_size = upper_bound - lower_bound - 1
        gap_sizes.append(int(gap_size))

        # Percentile of the current gap size among previous gaps
        gaps_up_to_current = [
            previous_draws_subset[j+1] - previous_draws_subset[j] - 1
            for j in range(len(previous_draws_subset) - 1)
        ]
        if gaps_up_to_current:
            pct = percentileofscore(
                gaps_up_to_current, gap_size, kind='rank'
            )
        else:
            pct = 50.0

        percentiles.append(round(pct, 2))

    additional_data = pd.DataFrame({
        'lowerbound': lower_bound_l,
        'upperbound': upper_bound_l,
        'gap_size': gap_sizes,
        'percentile': percentiles
    }, index=data_subset.index[1:])

    additional_data = additional_data.fillna(0)
    data_subset_extended = pd.concat([data_subset, additional_data], axis=1)

    return data_subset_extended


# ======================================================================
# Percentile Bands and Next-Gap Hit Rates
# ======================================================================
# Assuming data_subset_extended is already built by compute_gap_table

lowgaprange = [np.nan] * 10
upgaprange = [np.nan] * 10
next_draw_in_range = [np.nan] * 10

for i in range(10, len(data_subset_extended)):
    # all gaps up to the current draw
    gaps_up_to_current = data_subset_extended['gap_size'].iloc[:i].fillna(0).values

    # lower and upper percentiles (here 3rd and 70th)
    lower_bound = np.percentile(gaps_up_to_current, 3)
    upper_bound = np.percentile(gaps_up_to_current, 70)

    lowgaprange.append(lower_bound)
    upgaprange.append(upper_bound)

    # check whether the gap size of the next draw falls inside this band
    next_gap_size = data_subset_extended['gap_size'].iloc[i]
    if lower_bound <= next_gap_size <= upper_bound:
        next_draw_in_range.append(1)
    else:
        next_draw_in_range.append(0)

data_subset_extended['lowgaprange'] = lowgaprange
data_subset_extended['upgaprange'] = upgaprange
data_subset_extended['next_draw_in_range'] = next_draw_in_range

print(data_subset_extended[['st1', 'st2', 'st3', 'st4', 'st5',
      'gap_size', 'lowgaprange', 'upgaprange', 'next_draw_in_range']].tail(50))
print(data_subset_extended.tail(100)['next_draw_in_range'].sum())
print(data_subset_extended['next_draw_in_range'].sum())


# ======================================================================
# Searching Over Bands and Window Sizes
# ======================================================================
import math
import itertools
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import percentileofscore

warnings.filterwarnings('ignore')

pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)

# =============================================================================
# CONFIGURATION
# =============================================================================

# Path to historical draws with columns: st1..st5, stidx
FILE_PATH = 'data/total_nikstiles.csv'

# EuroJackpot main numbers: 5 out of 50
N_MAIN = 50
R = 5
N_TOTAL = math.comb(N_MAIN, R)     # 2,118,760
MAX_INDEX = N_TOTAL - 1            # 2,118,759

# Band search configuration
BAND_SEARCH_START_IDX = 600        # from which draw index we trust the regime
WINDOW_SIZES = [None, 300, 500]    # None = full history, or rolling windows
BAND_WIDTHS = [50, 60, 67]         # percentile widths
PCT_STEP = 1                       # step for low_pct scan

# For lift evaluation on the static band
LIFT_START_IDXS = [500, 600]


# =============================================================================
# GAP TABLE CONSTRUCTION (lowerbound, upperbound, gap_size, percentile)
# =============================================================================

def compute_gap_table(data_subset, max_index):
    # Compute for each draw its enclosing gap (lowerbound, upperbound) and gap_size,
    # as well as the percentile of that gap size among all previous gaps.

    gap_sizes = []
    percentiles = []
    lower_bound_l = []
    upper_bound_l = []

    for i in range(1, len(data_subset)):
        current_stidx = data_subset['stidx'].iloc[i]
        previous_draws_subset = sorted(data_subset['stidx'].iloc[:i].values)

        lower_bound = max(
            [idx for idx in previous_draws_subset if idx < current_stidx],
            default=0
        )
        upper_bound = min(
            [idx for idx in previous_draws_subset if idx > current_stidx],
            default=max_index
        )

        lower_bound_l.append(lower_bound)
        upper_bound_l.append(upper_bound)

        gap_size = upper_bound - lower_bound - 1
        gap_sizes.append(int(gap_size))

        gaps_up_to_current = [
            previous_draws_subset[j+1] - previous_draws_subset[j] - 1
            for j in range(len(previous_draws_subset) - 1)
        ]
        if gaps_up_to_current:
            pct = percentileofscore(
                gaps_up_to_current, gap_size, kind='rank'
            )
        else:
            pct = 50.0

        percentiles.append(round(pct, 2))

    additional_data = pd.DataFrame({
        'lowerbound': lower_bound_l,
        'upperbound': upper_bound_l,
        'gap_size': gap_sizes,
        'percentile': percentiles
    }, index=data_subset.index[1:])

    additional_data = additional_data.fillna(0)
    data_subset_extended = pd.concat([data_subset, additional_data], axis=1)

    return data_subset_extended


# =============================================================================
# BAND HIT RATE ON GAP SIZES
# =============================================================================

def band_hit_rate(gap_series, low_pct, high_pct,
                  window_size=None, start_idx=10):
    # Measure how often the gap_size of draw i falls inside a band learned
    # from previous gaps.

    n = len(gap_series)
    hits = 0
    trials = 0

    for i in range(start_idx, n):
        if window_size is None:
            start = 1
        else:
            start = max(1, i - window_size)
        past = gap_series[start:i]
        if len(past) == 0:
            continue

        band_low = np.percentile(past, low_pct)
        band_high = np.percentile(past, high_pct)

        gap_i = gap_series[i]
        if band_low <= gap_i <= band_high:
            hits += 1
        trials += 1

    if trials == 0:
        return {
            'hit_rate': np.nan,
            'trials': 0,
            'band_width': high_pct - low_pct,
            'expected_random': (high_pct - low_pct) / 100.0,
            'score': np.nan,
        }

    hit_rate = hits / trials
    band_width = high_pct - low_pct
    expected_random = band_width / 100.0
    score = hit_rate / expected_random if expected_random > 0 else np.nan

    return {
        'hit_rate': hit_rate,
        'trials': trials,
        'band_width': band_width,
        'expected_random': expected_random,
        'score': score,
    }


def search_best_gap_band(gap_series,
                         window_sizes,
                         band_widths,
                         pct_step=1,
                         start_idx=600):
    # Scan over window sizes and percentile bands to find bands that
    # capture upcoming gap sizes especially often compared with their width.

    records = []
    n = len(gap_series)

    for window_size in window_sizes:
        for band_width in band_widths:
            max_low_pct = 100 - band_width
            for low_pct in range(0, max_low_pct + 1, pct_step):
                high_pct = low_pct + band_width

                stats = band_hit_rate(
                    gap_series=gap_series,
                    low_pct=low_pct,
                    high_pct=high_pct,
                    window_size=window_size,
                    start_idx=start_idx
                )

                records.append({
                    'window_size': window_size if window_size is not None else 0,
                    'low_pct': low_pct,
                    'high_pct': high_pct,
                    'band_width': stats['band_width'],
                    'hit_rate': stats['hit_rate'],
                    'expected_random': stats['expected_random'],
                    'score': stats['score'],
                    'trials': stats['trials'],
                })

    results_df = pd.DataFrame(records)
    results_df = results_df.dropna(subset=['score'])
    results_df = results_df.sort_values('score', ascending=False)

    best_row = results_df.iloc[0]
    return results_df, best_row


# =============================================================================
# FULL COMBINATION UNIVERSE AND GAP-BAND MARKING
# =============================================================================

def generate_full_combinations(n_main=50, r=5):
    # Generate the full combination universe for a 5-out-of-n_main game.
    combos = itertools.combinations(range(1, n_main + 1), r)
    df_total = pd.DataFrame(combos, columns=[f"st{i}" for i in range(1, r + 1)])
    df_total['stidx'] = df_total.index  # lexicographic by construction
    return df_total


def mark_combinations_in_gap_band(df_total, df_hist, gap_low, gap_high, max_index):
    # Mark combinations whose stidx lies inside gaps whose size is in [gap_low, gap_high].

    df = df_total.copy()

    if 'stidx' not in df.columns:
        df['stidx'] = df.index

    drawn_indices = sorted(df_hist['stidx'].astype(int).values)

    df['drawn'] = df['stidx'].isin(drawn_indices).astype(int)
    df['in_valid_gap'] = 0

    # Gaps between historical draws
    for i in range(1, len(drawn_indices)):
        lower_idx = drawn_indices[i - 1]
        upper_idx = drawn_indices[i]
        gap_size = upper_idx - lower_idx - 1

        if gap_low <= gap_size <= gap_high:
            mask = (
                (df['stidx'] > lower_idx) &
                (df['stidx'] < upper_idx) &
                (df['drawn'] == 0)
            )
            df.loc[mask, 'in_valid_gap'] = 1

    # Tail gap from last draw to end of universe
    final_gap_size = max_index - drawn_indices[-1]  # inclusive tail
    if gap_low <= final_gap_size <= gap_high:
        mask = (
            (df['stidx'] > drawn_indices[-1]) &
            (df['stidx'] <= max_index) &
            (df['drawn'] == 0)
        )
        df.loc[mask, 'in_valid_gap'] = 1

    return df


# =============================================================================
# LIFT EVALUATION FOR A GAP-SIZE BAND
# =============================================================================

def evaluate_gap_band_lift(data_ext, df_total, gap_low, gap_high, start_idx=500):
    # Evaluate lift for a given gap-size band [gap_low, gap_high].

    p_space = (df_total['in_valid_gap'] == 1).mean()

    mask_draws = (
        (data_ext['gap_size'] >= gap_low) &
        (data_ext['gap_size'] <= gap_high)
    )

    mask_draws_recent = mask_draws.iloc[start_idx:]
    p_draws = mask_draws_recent.mean()

    hits = mask_draws_recent.sum()
    total_eval = len(mask_draws_recent)

    edge_ratio = p_draws / p_space if p_space > 0 else float('nan')

    print(f"--- Lift for gap-size band [{gap_low}, {gap_high}] with start_idx={start_idx} ---")
    print(f"Universe kept (in_valid_gap=1): {p_space:.6f} ({p_space*100:.4f}%)")
    print(f"Draws with gap_size in band:   {hits}/{total_eval} ({p_draws*100:.4f}%)")
    print(f"Lift (p_draws / p_space):      {edge_ratio:.3f}")
    print()

    return {
        'gap_low': gap_low,
        'gap_high': gap_high,
        'start_idx': start_idx,
        'p_space': p_space,
        'p_draws': p_draws,
        'edge_ratio': edge_ratio,
        'hits': int(hits),
        'total_draws_eval': int(total_eval),
    }


# =============================================================================
# MAIN RUN
# =============================================================================

def main():
    # 1. Load historical data and construct gap table
    data = pd.read_csv(FILE_PATH)
    data_subset = data[['st1', 'st2', 'st3', 'st4', 'st5', 'stidx']]

    data_ext = compute_gap_table(data_subset, max_index=MAX_INDEX)

    gap_series = data_ext['gap_size'].fillna(0).values
    n_draws = len(data_ext)
    print(f"Number of draws in history: {n_draws}")

    # 2. Baseline: global 3rd–70th percentile band over all gaps
    global_low = int(round(np.percentile(gap_series[1:], 3)))
    global_high = int(round(np.percentile(gap_series[1:], 70)))
    print(f"Global baseline band (3rd–70th pct): [{global_low}, {global_high}]")

    hits = 0
    trials = 0
    for i in range(10, n_draws):
        past = gap_series[1:i]
        if len(past) == 0:
            continue
        band_low = np.percentile(past, 3)
        band_high = np.percentile(past, 70)
        gap_i = gap_series[i]
        if band_low <= gap_i <= band_high:
            hits += 1
        trials += 1
    if trials > 0:
        hit_rate_baseline = hits / trials
        print(f"Baseline hit rate (3–70 pct band): {hit_rate_baseline*100:.2f}% "
              f"over {trials} draws
")

    # 3. Search over window sizes and percentile bands
    print("Running search over percentile bands and window sizes ...")
    results_df, best_row = search_best_gap_band(
        gap_series=gap_series,
        window_sizes=WINDOW_SIZES,
        band_widths=BAND_WIDTHS,
        pct_step=PCT_STEP,
        start_idx=BAND_SEARCH_START_IDX
    )

    print("Top 10 configurations by score (hit_rate / expected_random):")
    print(results_df.head(10))
    print("
Best configuration selected:")
    print(best_row)
    print()

    best_window = int(best_row['window_size'])
    best_low_pct = best_row['low_pct']
    best_high_pct = best_row['high_pct']

    # 4. Derive a concrete gap-size band from the last window using best config
    if best_window > 0:
        past_for_band = gap_series[-best_window:]
    else:
        past_for_band = gap_series[1:]  # full history except first

    best_gap_low = int(round(np.percentile(past_for_band, best_low_pct)))
    best_gap_high = int(round(np.percentile(past_for_band, best_high_pct)))

    print(f"Concrete band from best config: [{best_gap_low}, {best_gap_high}]")
    print()

    # 5. Generate full combination universe and mark gap-band membership
    print("Generating full combination universe and marking valid gaps ...")
    df_total = generate_full_combinations(n_main=N_MAIN, r=R)

    df_total = mark_combinations_in_gap_band(
        df_total=df_total,
        df_hist=data_ext,
        gap_low=best_gap_low,
        gap_high=best_gap_high,
        max_index=MAX_INDEX
    )

    valid_count = (df_total['in_valid_gap'] == 1).sum()
    p_space = valid_count / len(df_total)
    print(f"Combinations in best gap band: {valid_count} "
          f"({p_space*100:.4f}% of universe)")
    print()

    # 6. Lift evaluation for the band from the search and for the baseline band
    print("=== Lift evaluation for band from search ===")
    for start_idx in LIFT_START_IDXS:
        _ = evaluate_gap_band_lift(
            data_ext=data_ext,
            df_total=df_total,
            gap_low=best_gap_low,
            gap_high=best_gap_high,
            start_idx=start_idx
        )

    print("=== Lift evaluation for global 3–70 baseline band ===")
    df_total_baseline = mark_combinations_in_gap_band(
        df_total=df_total,
        df_hist=data_ext,
        gap_low=global_low,
        gap_high=global_high,
        max_index=MAX_INDEX
    )
    for start_idx in LIFT_START_IDXS:
        _ = evaluate_gap_band_lift(
            data_ext=data_ext,
            df_total=df_total_baseline,
            gap_low=global_low,
            gap_high=global_high,
            start_idx=start_idx
        )

    results_df.to_csv('gap_band_search_results.csv', index=False)
    df_total.to_csv('total_combinations_with_gap_flag_searchband.csv', index=False)
    df_total_baseline.to_csv('total_combinations_with_gap_flag_baseline.csv', index=False)


if __name__ == '__main__':
    main()
