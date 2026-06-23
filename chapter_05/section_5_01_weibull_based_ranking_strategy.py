"""
Code the Jackpot - 5.1.3 Weibull-based ranking strategy
Auto-extracted (book order). Full listings, nothing truncated.
"""


# ======================================================================
# Code listing – Weibull-based ranking and backtest
# ======================================================================
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import entropy
from reliability.Fitters import Fit_Weibull_2P


def build_inter_hit_gaps(df, columns=('st1', 'st2', 'st3', 'st4', 'st5'),
                         max_number=50):
    """
    For each number in 1..max_number, build a list of gaps (in draws)
    between consecutive hits, plus the gap from the last hit up to the
    end of the DataFrame.
    """
    cols = list(columns)
    values = df[cols].to_numpy()
    N = values.shape[0]

    hit_gaps = {}

    for number in range(1, max_number + 1):
        hit_indices = np.where((values == number).any(axis=1))[0].tolist()

        if hit_indices:
            hit_indices = sorted(hit_indices)

            gaps = []
            gaps.append(hit_indices[0])

            for i in range(1, len(hit_indices)):
                gaps.append(hit_indices[i] - hit_indices[i - 1])

            gaps.append((N - 1) - hit_indices[-1])
        else:
            gaps = [N]

        hit_gaps[number] = gaps

    return hit_gaps


def compute_weibull_table(hit_gaps, min_failures=3):
    """
    Given a dict {number: gaps}, fit a two-parameter Weibull distribution
    to the finished gaps (all entries except the last) for each number
    that has at least `min_failures` finished gaps.

    Returns a DataFrame with columns:
      st, emf, trials, Pr, median, P75, P90, P95, P99, Pct_score, PCT, nPr
    """
    rows = []

    for number, gaps in hit_gaps.items():
        if len(gaps) < 2:
            continue

        data_f = gaps[:-1]
        current_gap = gaps[-1]

        if len(data_f) < min_failures:
            continue

        median = int(np.percentile(data_f, 50))
        P75   = int(np.percentile(data_f, 75))
        P90   = int(np.percentile(data_f, 90))
        P95   = int(np.percentile(data_f, 95))
        P99   = int(np.percentile(data_f, 99))

        pct_score = float(stats.percentileofscore(data_f, current_gap))

        if len(data_f) > 2:
            fit = Fit_Weibull_2P(
                failures=data_f,
                show_probability_plot=False,
                print_results=False
            )
            ps = 1.0 - np.exp(-np.power((current_gap / fit.alpha), fit.beta))
            Pr = float(ps)
        else:
            Pr = 1.0

        rows.append({
            'st':        int(number),
            'emf':       int(len(data_f)),
            'trials':    int(current_gap),
            'Pr':        Pr,
            'median':    median,
            'P75':       P75,
            'P90':       P90,
            'P95':       P95,
            'P99':       P99,
            'Pct_score': pct_score
        })

    results = pd.DataFrame(rows)

    if results.empty:
        return results

    results['PCT'] = results['emf'] / results['emf'].sum()
    results['nPr'] = results['Pr'] / results['Pr'].sum()

    return results


def weibull_ranking_for_history(df, columns=('st1', 'st2', 'st3', 'st4', 'st5'),
                                max_number=50, min_failures=3):
    """
    Compute Weibull-based metrics for the whole history and return:

    - results table with columns above
    - weibull_rank      (numbers sorted by Pr, then by emf)
    - percentile_rank   (numbers sorted by Pct_score, then by emf)
    """
    hit_gaps = build_inter_hit_gaps(df, columns=columns, max_number=max_number)
    results = compute_weibull_table(hit_gaps, min_failures=min_failures)

    if results.empty:
        return results, [], []

    weibull_rank = results.sort_values(
        by=['Pr', 'emf'], ascending=[False, False]
    )['st'].tolist()

    percentile_rank = results.sort_values(
        by=['Pct_score', 'emf'], ascending=[False, False]
    )['st'].tolist()

    return results, weibull_rank, percentile_rank


def calc_combination_prob(combo, weibull_table):
    """
    Given a 5-number combination and the Weibull results table,
    compute the product of Pr values for these numbers.
    """
    combo = list(combo)
    probs = []

    for n in combo:
        row = weibull_table.loc[weibull_table['st'] == n, 'Pr']
        if not row.empty:
            probs.append(float(row.iloc[0]))

    if not probs:
        return 0.0

    probs = np.array(probs, dtype=float)
    return float(np.prod(probs))


def calc_combination_entropy(combo, weibull_table):
    """
    Shannon entropy of the Pr values within a combination.
    """
    combo = list(combo)
    probs = []

    for n in combo:
        row = weibull_table.loc[weibull_table['st'] == n, 'Pr']
        if not row.empty:
            probs.append(float(row.iloc[0]))

    if not probs:
        return 0.0

    probs = np.array(probs, dtype=float)
    probs = probs / probs.sum()

    return float(entropy(probs))


def weibull_backtest(
    df,
    columns=('st1', 'st2', 'st3', 'st4', 'st5'),
    max_number=50,
    window=500,
    min_failures=3,
    n_random=200,
    random_state=None,
):
    """
    Rolling backtest with random baselines.

    For each draw t in the last `window` draws:
      - use only draws before t as history,
      - fit Weibull per number,
      - build three selection sets based on gap position,
      - measure how many hits each set gets in the actual draw at t,
      - compute combination scores for draw t and the next 3 draws,
      - simulate random subsets of the same size as each set and
        accumulate their hit distributions as a baseline.
    """
    N = len(df)
    cols = list(columns)

    start_index = max(1, N - window - 3)
    end_index = N - 3

    hits_set1 = np.zeros(6, dtype=int)
    hits_set2 = np.zeros(6, dtype=int)
    hits_set3 = np.zeros(6, dtype=int)

    rand_hits_set1 = np.zeros(6, dtype=int)
    rand_hits_set2 = np.zeros(6, dtype=int)
    rand_hits_set3 = np.zeros(6, dtype=int)

    set_size_rows = []
    combo_rows = []

    rng = np.random.default_rng(random_state)
    all_numbers = np.arange(1, max_number + 1)

    for t in range(start_index, end_index):
        history = df.iloc[:t].reset_index(drop=True)

        current = df.iloc[t][cols].values.astype(int)
        next1  = df.iloc[t + 1][cols].values.astype(int)
        next2  = df.iloc[t + 2][cols].values.astype(int)
        next3  = df.iloc[t + 3][cols].values.astype(int)

        hit_gaps = build_inter_hit_gaps(
            history, columns=columns, max_number=max_number
        )
        res = compute_weibull_table(hit_gaps, min_failures=min_failures)

        if res.empty:
            continue

        mean_pct = res['Pct_score'].mean()
        std_pct  = res['Pct_score'].std()

        set1 = set(
            res[res['trials'] < res['P75']]
            .sort_values(by=['Pr', 'Pct_score'], ascending=[False, False])['st']
        )

        set2 = set(
            res[res['trials'] < res['median']]
            .sort_values(by=['Pr', 'Pct_score'], ascending=[False, False])['st']
        )

        set3 = set(
            res[
                (res['Pct_score'] >= mean_pct - std_pct) &
                (res['Pct_score'] <= mean_pct + std_pct)
            ]
            .sort_values(by=['Pr', 'Pct_score'], ascending=[False, False])['st']
        )

        size1 = len(set1)
        size2 = len(set2)
        size3 = len(set3)

        set_size_rows.append({
            'draw_index': t,
            'size_set1': size1,
            'size_set2': size2,
            'size_set3': size3,
        })

        h1 = sum(n in set1 for n in current)
        h2 = sum(n in set2 for n in current)
        h3 = sum(n in set3 for n in current)

        hits_set1[h1] += 1
        hits_set2[h2] += 1
        hits_set3[h3] += 1

        if 0 < size1 < max_number:
            for _ in range(n_random):
                rand_subset = rng.choice(all_numbers, size=size1, replace=False)
                r_h = sum(n in rand_subset for n in current)
                rand_hits_set1[r_h] += 1

        if 0 < size2 < max_number:
            for _ in range(n_random):
                rand_subset = rng.choice(all_numbers, size=size2, replace=False)
                r_h = sum(n in rand_subset for n in current)
                rand_hits_set2[r_h] += 1

        if 0 < size3 < max_number:
            for _ in range(n_random):
                rand_subset = rng.choice(all_numbers, size=size3, replace=False)
                r_h = sum(n in rand_subset for n in current)
                rand_hits_set3[r_h] += 1

        score_current = calc_combination_prob(current, res)
        score_next1   = calc_combination_prob(next1, res)
        score_next2   = calc_combination_prob(next2, res)
        score_next3   = calc_combination_prob(next3, res)

        combo_rows.append({
            'draw_index': t,
            'score_current': score_current,
            'score_next1':   score_next1,
            'score_next2':   score_next2,
            'score_next3':   score_next3,
        })

    combo_scores = pd.DataFrame(combo_rows)
    set_sizes = pd.DataFrame(set_size_rows)

    return {
        'hits_set1': hits_set1,
        'hits_set2': hits_set2,
        'hits_set3': hits_set3,
        'rand_hits_set1': rand_hits_set1,
        'rand_hits_set2': rand_hits_set2,
        'rand_hits_set3': rand_hits_set3,
        'set_sizes': set_sizes,
        'combo_scores': combo_scores,
    }


if __name__ == "__main__":
    pd.set_option('display.max_columns', 300)
    pd.set_option('display.max_rows', 300)

    df_n = pd.read_csv('total_nikstiles.csv', index_col=0)
    df_main = df_n.loc[:, 'st1':'st5'].reset_index(drop=True)

    print("Loading EuroJackpot data from: total_nikstiles.csv")

    weibull_results, weibull_rank, percentile_rank = weibull_ranking_for_history(
        df_main,
        columns=('st1', 'st2', 'st3', 'st4', 'st5'),
        max_number=50,
        min_failures=3,
    )

    print("Weibull ranking (Pr):", weibull_rank)
    print("Percentile ranking (Pct_score):", percentile_rank)

    backtest_res = weibull_backtest(
        df_main,
        columns=('st1', 'st2', 'st3', 'st4', 'st5'),
        max_number=50,
        window=500,
        min_failures=3,
        n_random=500,
        random_state=42,
    )

    print("Real hits Set 1:", backtest_res['hits_set1'])
    print("Random hits Set 1:", backtest_res['rand_hits_set1'])
    print("Real hits Set 2:", backtest_res['hits_set2'])
    print("Random hits Set 2:", backtest_res['rand_hits_set2'])
    print("Real hits Set 3:", backtest_res['hits_set3'])
    print("Random hits Set 3:", backtest_res['rand_hits_set3'])
    print(backtest_res['set_sizes'].describe())


# ======================================================================
# Full code listing
# ======================================================================

import pandas as pd
import numpy as np
from scipy.stats import percentileofscore
from collections import Counter
from math import comb


def calculate_percentiles_multi_columns(data_frame, columns):
    """
    For a given history of draws and a set of columns (for example st1..st5),
    compute spacing-based statistics for each distinct number that appears
    in those columns.

    Returns a DataFrame with one row per number, containing:
      - value:       the number itself
      - co:          number of hit-intervals
      - delay:       current tail gap (draws since last appearance)
      - median,P75,P90,P95,P99,max: summary stats of the spacing series
      - Pct_score:   percentile of the current delay within this number's spacings
      - Norm:        share (in %) of total 'co' across all numbers
      - Prod:        Norm * Pct_score, used for ranking
    """

    # Basic validation
    if not all(column in data_frame.columns for column in columns):
        missing_columns = [c for c in columns if c not in data_frame.columns]
        raise ValueError(f"Columns {missing_columns} not found in DataFrame")

    # All distinct values appearing in the selected columns
    unique_values = pd.unique(data_frame[columns].values.ravel('K'))

    index_diff_dict = {}

    # Build spacing series for each distinct number
    for value in unique_values:
        # Rows where `value` appears in any of the columns
        mask = data_frame[columns].isin([value]).any(axis=1)
        indices = data_frame.index[mask].tolist()

        if len(indices) == 0:
            continue

        # Spacings:
        #   - from start to first hit
        #   - between consecutive hits
        #   - from last hit to end of DataFrame
        index_diffs = (
            [indices[0]] +
            [indices[i] - indices[i - 1] for i in range(1, len(indices))] +
            [len(data_frame) - indices[-1]]
        )
        index_diff_dict[value] = index_diffs

    results = pd.DataFrame()

    # Turn spacing series into statistics per number
    for key, index_diffs in index_diff_dict.items():
        if len(index_diffs) > 1:
            delay_now = index_diffs[-1]
            stats_dict = {
                'value': int(key),
                'co': len(index_diffs) - 1,
                'delay': int(delay_now),
                'median': int(np.percentile(index_diffs, 50)),
                'P75': int(np.percentile(index_diffs, 75)),
                'P90': int(np.percentile(index_diffs, 90)),
                'P95': int(np.percentile(index_diffs, 95)),
                'P99': int(np.percentile(index_diffs, 99)),
                'max': int(np.max(index_diffs)),
                'Pct_score': int(round(percentileofscore(index_diffs, delay_now)))
            }
            results = pd.concat(
                [results, pd.DataFrame([stats_dict])],
                ignore_index=True
            )

    if results.empty:
        return results

    # Share of total activity (co)
    results['Norm'] = (100 * results['co'] / results['co'].sum()).astype(float).round(2)
    # Combined score: active and stretched
    results['Prod'] = results['Norm'] * results['Pct_score']
    # Sort by Prod descending
    results.sort_values(by='Prod', ascending=False, inplace=True)
    results.reset_index(drop=True, inplace=True)

    return results


def split_groups_from_prod(results, group_sizes=(17, 17, 16)):
    """
    Given a results DataFrame sorted by Prod and a tuple of group sizes,
    return a dict of sets { 'G1': {numbers}, 'G2': {...}, 'G3': {...} }.
    """
    if results.empty:
        raise ValueError("Empty results passed to split_groups_from_prod.")

    values_sorted = results['value'].tolist()
    g1_size, g2_size, g3_size = group_sizes

    if g1_size + g2_size + g3_size > len(values_sorted):
        raise ValueError("Group sizes exceed number of available values.")

    G1 = set(values_sorted[:g1_size])
    G2 = set(values_sorted[g1_size:g1_size + g2_size])
    G3 = set(values_sorted[g1_size + g2_size:g1_size + g2_size + g3_size])

    return {'G1': G1, 'G2': G2, 'G3': G3}


def _pattern_probability(pattern, group_sizes, total_numbers=50):
    """
    Baseline probability of a pattern (k1,k2,k3) under uniform random draws
    of 5 numbers from total_numbers, split into groups with sizes in
    group_sizes (for example (17,17,16)).
    """
    k1, k2, k3 = pattern
    s1, s2, s3 = group_sizes

    if k1 + k2 + k3 != 5:
        return 0.0

    numerator = (
        comb(s1, k1) *
        comb(s2, k2) *
        comb(s3, k3)
    )
    denominator = comb(total_numbers, 5)

    return numerator / denominator if denominator > 0 else 0.0


def backtest_spacing_percentile_ranking(
    df_hist,
    columns=('st1', 'st2', 'st3', 'st4', 'st5'),
    start_idx=300,
    group_sizes=(17, 17, 16),
    total_numbers=50
):
    """
    Backtest the spacing-percentile ranking with rolling history.

    For each draw t from start_idx to the last row:
      - use draws [0..t-1] to compute spacing-based stats and Prod ranking,
      - split numbers into G1,G2,G3 of sizes group_sizes,
      - count hits of the actual draw t in each group.

    Returns:
      hits_log:      DataFrame with hits per draw per group
      group_stats:   DataFrame with avg hits, expected hits, and lift per group
      pattern_stats: DataFrame with pattern counts, empirical freq,
                     baseline prob, and pattern lift
    """

    if len(df_hist) <= start_idx:
        raise ValueError("History too short for given start_idx.")

    records = []

    # Loop over evaluation draws
    for t in range(start_idx, len(df_hist)):
        # History up to but not including draw t
        hist_t = df_hist.iloc[:t]

        # Compute spacing-based stats and Prod ranking
        stats_t = calculate_percentiles_multi_columns(hist_t, list(columns))
        if stats_t.empty:
            continue

        groups = split_groups_from_prod(stats_t, group_sizes=group_sizes)

        # Actual draw at time t
        draw_nums = set(int(x) for x in df_hist.loc[df_hist.index[t], list(columns)])

        hits_G1 = len(draw_nums & groups['G1'])
        hits_G2 = len(draw_nums & groups['G2'])
        hits_G3 = len(draw_nums & groups['G3'])

        records.append({
            'draw_idx': df_hist.index[t],
            'hits_G1': hits_G1,
            'hits_G2': hits_G2,
            'hits_G3': hits_G3
        })

    hits_log = pd.DataFrame.from_records(records)

    # Group-level stats: average hits, expectation, lift
    group_stats = []

    # Expectation under uniform random draws of 5 numbers
    exp_G1 = group_sizes[0] * 5.0 / total_numbers
    exp_G2 = group_sizes[1] * 5.0 / total_numbers
    exp_G3 = group_sizes[2] * 5.0 / total_numbers

    avg_G1 = hits_log['hits_G1'].mean()
    avg_G2 = hits_log['hits_G2'].mean()
    avg_G3 = hits_log['hits_G3'].mean()

    group_stats.append({
        'group': 'G1',
        'size': group_sizes[0],
        'avg_hits_per_draw': avg_G1,
        'expected_hits_per_draw': exp_G1,
        'lift': avg_G1 / exp_G1 if exp_G1 > 0 else np.nan
    })
    group_stats.append({
        'group': 'G2',
        'size': group_sizes[1],
        'avg_hits_per_draw': avg_G2,
        'expected_hits_per_draw': exp_G2,
        'lift': avg_G2 / exp_G2 if exp_G2 > 0 else np.nan
    })
    group_stats.append({
        'group': 'G3',
        'size': group_sizes[2],
        'avg_hits_per_draw': avg_G3,
        'expected_hits_per_draw': exp_G3,
        'lift': avg_G3 / exp_G3 if exp_G3 > 0 else np.nan
    })

    group_stats = pd.DataFrame(group_stats)

    # Pattern-level stats
    pattern_counter = Counter()
    for _, row in hits_log.iterrows():
        pattern = (int(row['hits_G1']),
                   int(row['hits_G2']),
                   int(row['hits_G3']))
        pattern_counter[pattern] += 1

    total_draws = len(hits_log)
    pattern_records = []

    for pattern, count in pattern_counter.items():
        emp_freq = count / total_draws if total_draws > 0 else 0.0
        base_prob = _pattern_probability(pattern, group_sizes, total_numbers=total_numbers)
        lift = emp_freq / base_prob if base_prob > 0 else np.nan

        pattern_records.append({
            'pattern': pattern,
            'count': count,
            'empirical_freq': emp_freq,
            'baseline_prob': base_prob,
            'lift': lift
        })

    pattern_stats = pd.DataFrame(pattern_records).sort_values(
        by='lift', ascending=False
    ).reset_index(drop=True)

    return hits_log, group_stats, pattern_stats


# ======================================================================
# Code Listing
# ======================================================================
import numpy as np
import pandas as pd

def co_common(remaining_numbers, draw_numbers):
    """
    Count how many numbers from `draw_numbers` are present
    in the iterable `remaining_numbers`.
    """
    rem_set = set(remaining_numbers)
    return sum(1 for x in draw_numbers if x in rem_set)


def greedy_elimination_pool(draw_data, target_count, cols=('st1', 'st2', 'st3', 'st4', 'st5')):
    """
    Greedy elimination of numbers 1..50 based on history coverage.

    Parameters
    ----------
    draw_data : DataFrame
        Historical draws with columns st1..st5.
    target_count : int
        How many numbers we want to keep at the end (size of survivor pool).
    cols : tuple of str
        Columns that contain the 5 main numbers.

    Returns
    -------
    eliminated_numbers : list of int
        Numbers removed in order (first removed = most redundant).
    survivors : list of int
        Numbers that survived to the end (coverage core), sorted.
    """
    draws = draw_data.loc[:, cols].astype(int).to_numpy()

    # number_stats[i, 0] = number (1..50 or 0 if eliminated)
    # number_stats[i, 1..6] = counts of draws with 0..5 numbers still covered
    number_stats = np.zeros((50, 7), dtype=int)
    number_stats[:, 0] = np.arange(1, 51)

    eliminated_numbers = []
    numbers_to_eliminate = 50 - target_count

    for _ in range(numbers_to_eliminate):
        # For each not-yet-eliminated number, simulate removing it
        for idx in range(50):
            if number_stats[idx, 0] == 0:
                continue  # already eliminated

            temp_remaining = number_stats[:, 0].copy()
            temp_remaining[idx] = 0  # simulate elimination
            rem = temp_remaining[temp_remaining != 0]

            # For each draw, count how many of its 5 numbers remain
            for row in draws:
                common_count = co_common(rem, row)  # 0..5
                number_stats[idx, common_count + 1] += 1

        # Choose the number to eliminate:
        # 1) max times we still see full coverage (5/5)
        # 2) if tie, max times we see 4/5
        full_cov = number_stats[:, 6]
        max_full = full_cov.max()
        candidates = np.where(full_cov == max_full)[0]

        if len(candidates) > 1:
            # break ties with 4/5 coverage (column 5)
            four_cov = number_stats[candidates, 5]
            best_idx_local = candidates[np.argmax(four_cov)]
        else:
            best_idx_local = candidates[0]

        # Mark eliminated and reset stats for next round
        eliminated_numbers.append(int(number_stats[best_idx_local, 0]))
        number_stats[best_idx_local, 0] = 0
        number_stats[:, 1:7] = 0

    # Anything not zero in column 0 is a survivor
    survivors = sorted(int(x) for x in number_stats[:, 0] if x != 0)

    return eliminated_numbers, survivors


def greedy_coverage_ranking(draw_data, cols=('st1', 'st2', 'st3', 'st4', 'st5')):
    """
    Build a full 1..50 ranking from the greedy elimination process.

    We run the elimination until only 1 number remains.
    The last survivor is the top-ranked number.
    Reversing the elimination order + the last survivor gives a full ranking.

    Returns
    -------
    ranking : list of int
        Numbers 1..50 sorted from strongest (index 0) to weakest.
    """
    eliminated, survivors = greedy_elimination_pool(
        draw_data,
        target_count=1,
        cols=cols
    )

    # With target_count=1 there is exactly one survivor.
    last_survivor = survivors[0]

    # eliminated = [worst, ..., second_best]
    # So reversed(eliminated) = [second_best, ..., worst]
    ranking = [last_survivor] + list(reversed(eliminated))
    return ranking


# ======================================================================
# Splitting the Ranking into 17–17–16 Groups
# ======================================================================
def split_greedy_groups(ranking):
    """
    Split a full 50-number ranking into three sets:
    G1 (top 17), G2 (next 17), G3 (bottom 16).
    """
    assert len(ranking) == 50
    g1 = set(ranking[:17])
    g2 = set(ranking[17:34])
    g3 = set(ranking[34:])
    return {"G1": g1, "G2": g2, "G3": g3}


# ======================================================================
# Backtesting the Coverage Ranking
# ======================================================================
from collections import defaultdict
import numpy as np
import pandas as pd

def backtest_greedy_coverage(df_hist, start_draw=200, cols=('st1', 'st2', 'st3', 'st4', 'st5')):
    """
    Backtest the coverage-based greedy ranking.

    For each draw t >= start_draw:
      - Build ranking from draws [0..t-1]
      - Split into G1,G2,G3 (17,17,16)
      - Count how many numbers of draw t fall into each group.

    Returns
    -------
    hits_log : DataFrame with columns:
        draw_idx, hits_G1, hits_G2, hits_G3
    summary  : DataFrame with:
        group, size, avg_hits_per_draw, expected_hits_per_draw, lift
    """
    records = []
    n_total = len(df_hist)
    total_numbers = 50
    k = len(cols)  # number of main numbers, usually 5

    for t in range(start_draw, n_total):
        past = df_hist.iloc[:t]
        current = df_hist.iloc[t]

        ranking = greedy_coverage_ranking(past, cols=cols)
        groups = split_greedy_groups(ranking)

        draw_nums = set(int(current[c]) for c in cols)

        hits_G1 = len(draw_nums & groups["G1"])
        hits_G2 = len(draw_nums & groups["G2"])
        hits_G3 = len(draw_nums & groups["G3"])

        records.append({
            "draw_idx": t,
            "hits_G1": hits_G1,
            "hits_G2": hits_G2,
            "hits_G3": hits_G3,
        })

    hits_log = pd.DataFrame(records)

    # Summary
    num_eval = len(hits_log)
    group_sizes = {"G1": 17, "G2": 17, "G3": 16}

    rows_sum = []
    for g in ["G1", "G2", "G3"]:
        col_name = f"hits_{g}"
        total_hits = hits_log[col_name].sum()
        avg_hits = total_hits / num_eval

        expected_hits = group_sizes[g] * k / total_numbers  # random baseline
        lift = avg_hits / expected_hits if expected_hits > 0 else np.nan

        rows_sum.append({
            "group": g,
            "size": group_sizes[g],
            "avg_hits_per_draw": avg_hits,
            "expected_hits_per_draw": expected_hits,
            "lift": lift,
        })

    summary = pd.DataFrame(rows_sum)
    return hits_log, summary


# ======================================================================
# Code: core elimination function for EuroJackpot (5-out-of-50)
# ======================================================================
import numpy as np

import pandas as pd

def number_sequence_ranking(df_hist, cols=('st1','st2','st3','st4','st5'), nu_left=20):

    """

    Iteratively remove the EuroJackpot main number that belongs to the fewest currently-active

    historical 5-sets, until only nu_left numbers remain.

    Parameters

    ----------

    df_hist : pandas.DataFrame

        Historical EuroJackpot draws with columns holding the main numbers.

    cols : tuple of str, optional

        Column names for the main numbers (default: ('st1','st2','st3','st4','st5')).

    nu_left : int, optional

        How many numbers should remain at the end of the peeling.

        For EuroJackpot, values like 20 or 25 are natural choices for a survivor pool.

    Returns

    -------

    ranking : list of int

        A list of all 50 numbers in the order they were removed,

        followed by the final nu_left survivors (sorted).

    """

    # Extract the main number matrix

    draws = df_hist.loc[:, cols].astype(int).to_numpy()

    # All possible EuroJackpot main numbers (1 to 50)

    ALL_NUMS = np.arange(1, 51, dtype=int)

    # For each number, store the indices of draws where it appears

    indices_by_number = {n: [] for n in ALL_NUMS}

    for j, row in enumerate(draws):

        for n in row:

            if 1 <= n <= 50:  # simple safety guard

                indices_by_number[n].append(j)

    # Track which draws are still active

    active_draw = np.ones(len(draws), dtype=bool)

    # Initial counts: how many active draws each number belongs to

    cnt = {n: len(indices_by_number[n]) for n in ALL_NUMS}

    # Track which numbers are still in the game

    remaining = {n: True for n in ALL_NUMS}

    elimination_order = []

    # How many numbers we will remove

    to_remove = len(ALL_NUMS) - nu_left

    for _ in range(to_remove):

        # Choose the number with the smallest active-draw count (tie → smaller number)

        min_cnt, choice = min((cnt[n], n) for n in ALL_NUMS if remaining[n])

        # Record and remove it

        elimination_order.append(choice)

        remaining[choice] = False

        # Deactivate all active draws containing 'choice' and update neighbour counts

        for j in indices_by_number[choice]:

            if not active_draw[j]:

                continue

            active_draw[j] = False

            # For each other number in that draw, reduce its count

            for n in draws[j]:

                if n != choice and remaining.get(n, False):

                    cnt[n] -= 1

    # The survivors are the remaining numbers, sorted

    survivors = sorted([n for n in ALL_NUMS if remaining[n]])

    # Return full ranking: eliminated numbers first, survivors last

    return elimination_order + survivors


# ======================================================================
# Interpreting and using the EuroJackpot output
# ======================================================================
# Run the elimination with 25 survivors

ranking = number_sequence_ranking(

    df_hist,

    cols=('st1','st2','st3','st4','st5'),

    nu_left=25

)

# Split into elimination order and survivors

elimination_order = ranking[:-25]

survivors = ranking[-25:]

print("First 10 removed:", elimination_order[:10])

print("Survivor pool (25 numbers):", survivors)
