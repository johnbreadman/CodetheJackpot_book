"""
Code the Jackpot - 5.2 Covering Sets for Efficient Play
Auto-extracted (book order). Full listings, nothing truncated.
"""


# ======================================================================
# 5.2.3 Empirical Covering Sizes and Generation Logs
# ======================================================================
[INIT] N=30, K=5, C=4, total candidates=142,506
[INIT] Built combinations & bitmasks in 0.123s
[PROGRESS] i=29,030/142,506 | chosen=1,000 | window ~113,475 | dt=1.40s
[PROGRESS] i=62,507/142,506 | chosen=2,000 | window ~79,998 | dt=0.87s
[PROGRESS] i=95,656/142,506 | chosen=3,000 | window ~46,849 | dt=0.46s
[PROGRESS] i=127,667/142,506 | chosen=4,000 | window ~14,838 | dt=0.17s

=== SUMMARY ===
Candidates (N choose K): 142,506
Chosen set size        : 4,459
Build combos time      : 0.123s
Greedy (vectorized)    : 2.929s
Saved                  : covering_30_5_4_4459.csv

[INIT] N=40, K=5, C=4, total candidates=658,008
[INIT] Built combinations & bitmasks in 0.610s
[PROGRESS] i=52,340/658,008 | chosen=1,000 | window ~605,667 | dt=9.91s
[PROGRESS] i=101,998/658,008 | chosen=2,000 | window ~556,009 | dt=8.91s
[PROGRESS] i=158,881/658,008 | chosen=3,000 | window ~499,126 | dt=7.58s
[PROGRESS] i=217,931/658,008 | chosen=4,000 | window ~440,076 | dt=6.31s
[PROGRESS] i=274,069/658,008 | chosen=5,000 | window ~383,938 | dt=5.57s
[PROGRESS] i=330,501/658,008 | chosen=6,000 | window ~327,506 | dt=3.57s
[PROGRESS] i=385,546/658,008 | chosen=7,000 | window ~272,461 | dt=2.46s
[PROGRESS] i=447,078/658,008 | chosen=8,000 | window ~210,929 | dt=1.84s
[PROGRESS] i=506,358/658,008 | chosen=9,000 | window ~151,649 | dt=1.21s
[PROGRESS] i=566,234/658,008 | chosen=10,000 | window ~91,773 | dt=0.65s
[PROGRESS] i=621,220/658,008 | chosen=11,000 | window ~36,787 | dt=0.25s

=== SUMMARY ===
Candidates (N choose K): 658,008
Chosen set size        : 11,271
Build combos time      : 0.610s
Greedy (vectorized)    : 48.271s
Saved                  : covering_40_5_4_11271.csv

[INIT] N=45, K=5, C=4, total candidates=1,221,759
[INIT] Built combinations & bitmasks in 1.132s
[PROGRESS] i=57,147/1,221,759 | chosen=1,000 | window ~1,164,611 | dt=19.05s
[PROGRESS] i=126,207/1,221,759 | chosen=2,000 | window ~1,095,551 | dt=17.45s
[PROGRESS] i=173,642/1,221,759 | chosen=3,000 | window ~1,048,116 | dt=16.04s
[PROGRESS] i=244,032/1,221,759 | chosen=4,000 | window ~977,726 | dt=14.85s
[PROGRESS] i=297,473/1,221,759 | chosen=5,000 | window ~924,285 | dt=13.36s
[PROGRESS] i=362,933/1,221,759 | chosen=6,000 | window ~858,825 | dt=11.88s
[PROGRESS] i=421,091/1,221,759 | chosen=7,000 | window ~800,667 | dt=11.24s
[PROGRESS] i=479,420/1,221,759 | chosen=8,000 | window ~742,338 | dt=9.65s
[PROGRESS] i=547,604/1,221,759 | chosen=9,000 | window ~674,154 | dt=7.84s
[PROGRESS] i=607,830/1,221,759 | chosen=10,000 | window ~613,928 | dt=6.73s
[PROGRESS] i=666,457/1,221,759 | chosen=11,000 | window ~555,301 | dt=4.95s
[PROGRESS] i=727,434/1,221,759 | chosen=12,000 | window ~494,324 | dt=4.17s
[PROGRESS] i=786,961/1,221,759 | chosen=13,000 | window ~434,797 | dt=3.51s
[PROGRESS] i=846,191/1,221,759 | chosen=14,000 | window ~375,567 | dt=2.80s
[PROGRESS] i=912,391/1,221,759 | chosen=15,000 | window ~309,367 | dt=2.15s
[PROGRESS] i=970,063/1,221,759 | chosen=16,000 | window ~251,695 | dt=1.63s
[PROGRESS] i=1,021,202/1,221,759 | chosen=17,000 | window ~200,556 | dt=1.13s
[PROGRESS] i=1,074,887/1,221,759 | chosen=18,000 | window ~146,871 | dt=0.63s
[PROGRESS] i=1,152,215/1,221,759 | chosen=19,000 | window ~69,543 | dt=0.29s

=== SUMMARY ===
Candidates (N choose K): 1,221,759
Chosen set size        : 19,631
Build combos time      : 1.132s
Greedy (vectorized)    : 149.396s
Saved                  :covering_45_5_4_19631.csv

[INIT] N=50, K=5, C=4, total candidates=2,118,760
[INIT] Built combinations & bitmasks in 1.976s
[PROGRESS] i=56,971/2,118,760 | chosen=1,000 | window ~2,061,788 | dt=33.42s
[PROGRESS] i=130,626/2,118,760 | chosen=2,000 | window ~1,988,133 | dt=32.35s
[PROGRESS] i=192,889/2,118,760 | chosen=3,000 | window ~1,925,870 | dt=30.81s
[PROGRESS] i=236,551/2,118,760 | chosen=4,000 | window ~1,882,208 | dt=29.33s
[PROGRESS] i=302,778/2,118,760 | chosen=5,000 | window ~1,815,981 | dt=27.99s
[PROGRESS] i=376,884/2,118,760 | chosen=6,000 | window ~1,741,875 | dt=26.42s
[PROGRESS] i=426,225/2,118,760 | chosen=7,000 | window ~1,692,534 | dt=25.08s
[PROGRESS] i=491,523/2,118,760 | chosen=8,000 | window ~1,627,236 | dt=23.83s
[PROGRESS] i=561,252/2,118,760 | chosen=9,000 | window ~1,557,507 | dt=23.25s
[PROGRESS] i=616,277/2,118,760 | chosen=10,000 | window ~1,502,482 | dt=22.97s
[PROGRESS] i=685,238/2,118,760 | chosen=11,000 | window ~1,433,521 | dt=19.29s
[PROGRESS] i=745,679/2,118,760 | chosen=12,000 | window ~1,373,080 | dt=18.35s
[PROGRESS] i=808,134/2,118,760 | chosen=13,000 | window ~1,310,625 | dt=16.72s
[PROGRESS] i=876,966/2,118,760 | chosen=14,000 | window ~1,241,793 | dt=14.97s
[PROGRESS] i=934,483/2,118,760 | chosen=15,000 | window ~1,184,276 | dt=13.68s
[PROGRESS] i=1,003,617/2,118,760 | chosen=16,000 | window ~1,115,142 | dt=10.91s
[PROGRESS] i=1,061,823/2,118,760 | chosen=17,000 | window ~1,056,936 | dt=9.86s
[PROGRESS] i=1,129,739/2,118,760 | chosen=18,000 | window ~989,020 | dt=8.66s
[PROGRESS] i=1,190,111/2,118,760 | chosen=19,000 | window ~928,648 | dt=7.72s
[PROGRESS] i=1,254,828/2,118,760 | chosen=20,000 | window ~863,931 | dt=6.89s
[PROGRESS] i=1,322,086/2,118,760 | chosen=21,000 | window ~796,673 | dt=6.30s
[PROGRESS] i=1,376,362/2,118,760 | chosen=22,000 | window ~742,397 | dt=5.30s
[PROGRESS] i=1,441,319/2,118,760 | chosen=23,000 | window ~677,440 | dt=4.68s
[PROGRESS] i=1,505,792/2,118,760 | chosen=24,000 | window ~612,967 | dt=4.18s
[PROGRESS] i=1,567,456/2,118,760 | chosen=25,000 | window ~551,303 | dt=3.47s
[PROGRESS] i=1,622,413/2,118,760 | chosen=26,000 | window ~496,346 | dt=3.01s
[PROGRESS] i=1,680,738/2,118,760 | chosen=27,000 | window ~438,021 | dt=2.55s
[PROGRESS] i=1,739,040/2,118,760 | chosen=28,000 | window ~379,719 | dt=1.99s
[PROGRESS] i=1,792,528/2,118,760 | chosen=29,000 | window ~326,231 | dt=1.43s
[PROGRESS] i=1,850,226/2,118,760 | chosen=30,000 | window ~268,533 | dt=1.03s
[PROGRESS] i=1,927,546/2,118,760 | chosen=31,000 | window ~191,213 | dt=0.69s
[PROGRESS] i=2,001,781/2,118,760 | chosen=32,000 | window ~116,978 | dt=0.46s
[PROGRESS] i=2,075,920/2,118,760 | chosen=33,000 | window ~42,839 | dt=0.22s

=== SUMMARY ===
Candidates (N choose K): 2,118,760
Chosen set size        : 33,572
Build combos time      : 1.976s
Greedy (vectorized)    : 437.844s
Saved                  : covering_50_5_4_33572.csv


# ======================================================================
# Code: Four-ranking extended covering pipeline
# ======================================================================
import math
import time
from itertools import combinations
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np
import pandas as pd
from scipy import stats
from reliability.Fitters import Fit_Weibull_2P

# ----------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------

HIST_PATH = "data/total_nikstiles.csv"
COVERING_PATH = "data/covering_50_5_4_33572.csv"
MAIN_COLS = ("st1", "st2", "st3", "st4", "st5")
MAX_NUMBER = 50


# ======================================================================
# 1. Multi-column spacing ranking (Norm × Pct_score)
# ======================================================================

def calculate_percentiles_multi_columns(
    df: pd.DataFrame,
    columns: Sequence[str],
) -> pd.DataFrame:
    """
    For each unique value appearing in the given columns:
      - compute the index gaps between appearances (including head/tail)
      - get a delay percentile (Pct_score) for the current tail
      - compute Norm = 100 * co / sum(co)
      - Prod = Norm * Pct_score

    Returns
    -------
    DataFrame sorted by Prod descending, with columns:
      value, co, delay, median, P75, P90, P95, P99, max, Pct_score, Norm, Prod
    """
    if not all(col in df.columns for col in columns):
        missing = [c for c in columns if c not in df.columns]
        raise ValueError(f"Columns {missing} not found in DataFrame")

    unique_values = pd.unique(df[columns].values.ravel("K"))
    index_diff_dict: Dict[int, List[int]] = {}

    for value in unique_values:
        mask = df[columns].isin([value]).any(axis=1)
        indices = df.index[mask].tolist()
        if not indices:
            continue

        # gaps between appearances + head + tail
        index_diffs = (
            [indices[0]] +
            [indices[i] - indices[i - 1] for i in range(1, len(indices))] +
            [len(df) - indices[-1]]
        )
        index_diff_dict[int(value)] = index_diffs

    rows: List[Dict[str, float]] = []
    for key, index_diffs in index_diff_dict.items():
        if len(index_diffs) <= 1:
            continue

        delay = int(index_diffs[-1])
        pct_score = int(stats.percentileofscore(index_diffs, delay))

        rows.append(
            {
                "value": int(key),
                "co": len(index_diffs) - 1,
                "delay": delay,
                "median": int(np.percentile(index_diffs, 50)),
                "P75": int(np.percentile(index_diffs, 75)),
                "P90": int(np.percentile(index_diffs, 90)),
                "P95": int(np.percentile(index_diffs, 95)),
                "P99": int(np.max(index_diffs)),
                "max": int(np.max(index_diffs)),
                "Pct_score": pct_score,
            }
        )

    if not rows:
        return pd.DataFrame()

    results = pd.DataFrame(rows)
    results["Norm"] = (100 * results["co"] / results["co"].sum()).astype(float).round(2)
    results["Prod"] = results["Norm"] * results["Pct_score"]
    results = results.sort_values(by="Prod", ascending=False).reset_index(drop=True)
    return results


def spacing_ranking(df: pd.DataFrame, cols: Sequence[str] = MAIN_COLS) -> List[int]:
    """
    Multi-column spacing ranking: numbers with high Norm × Pct_score first.
    Fills any missing numbers (1..50) at the end, in ascending order.
    """
    res = calculate_percentiles_multi_columns(df, list(cols))
    if res.empty:
        return list(range(1, MAX_NUMBER + 1))

    ranked = res["value"].astype(int).tolist()
    all_nums = set(range(1, MAX_NUMBER + 1))
    missing = sorted(all_nums - set(ranked))
    return ranked + missing  # best first


# ======================================================================
# 2. Weibull-based ranking of inter-hit gaps
# ======================================================================

def build_inter_hit_gaps(
    df: pd.DataFrame,
    columns: Sequence[str] = MAIN_COLS,
    max_number: int = MAX_NUMBER,
) -> Dict[int, List[int]]:
    """
    For each number 1..max_number, build a list of gaps (in draws)
    between consecutive hits, plus the gap from the last hit up to the
    end of the DataFrame (or full length if never hit).

    Returns
    -------
    dict: {number: [gap_1, gap_2, ..., current_gap]}
    """
    values = df[list(columns)].to_numpy()
    N = values.shape[0]

    hit_gaps: Dict[int, List[int]] = {}

    for number in range(1, max_number + 1):
        hit_indices = np.where((values == number).any(axis=1))[0].tolist()

        if hit_indices:
            hit_indices.sort()

            gaps: List[int] = [hit_indices[0]]
            for i in range(1, len(hit_indices)):
                gaps.append(hit_indices[i] - hit_indices[i - 1])

            gaps.append((N - 1) - hit_indices[-1])
        else:
            gaps = [N]

        hit_gaps[number] = gaps

    return hit_gaps


def compute_weibull_table(
    hit_gaps: Dict[int, List[int]],
    min_failures: int = 3,
) -> pd.DataFrame:
    """
    Fit a two-parameter Weibull distribution to finished gaps
    (all entries except the last) for each number with at least
    `min_failures` strictly positive finished gaps.

    Zeros in the gap list (e.g. first hit at index 0) are removed
    before fitting, so the reliability library does not complain.
    """
    rows: List[Dict[str, float]] = []

    for number, gaps in hit_gaps.items():
        if len(gaps) < 2:
            continue

        # Finished gaps before the current tail
        raw_data_f = gaps[:-1]

        # Remove zeros – Weibull_2P requires positive failures
        data_f = [g for g in raw_data_f if g > 0]
        current_gap = gaps[-1]

        # If after removing zeros we don't have enough data, skip this number
        if len(data_f) < min_failures:
            continue

        median = int(np.percentile(data_f, 50))
        P75 = int(np.percentile(data_f, 75))
        P90 = int(np.percentile(data_f, 90))
        P95 = int(np.percentile(data_f, 95))
        P99 = int(np.percentile(data_f, 99))

        pct_score = float(stats.percentileofscore(data_f, current_gap))

        if len(data_f) > 2:
            fit = Fit_Weibull_2P(
                failures=data_f,
                show_probability_plot=False,
                print_results=False,
            )
            ps = 1.0 - np.exp(-np.power((current_gap / fit.alpha), fit.beta))
            Pr = float(ps)
        else:
            Pr = 1.0

        rows.append(
            {
                "st": int(number),
                "emf": int(len(data_f)),
                "trials": int(current_gap),
                "Pr": Pr,
                "median": median,
                "P75": P75,
                "P90": P90,
                "P95": P95,
                "P99": P99,
                "Pct_score": pct_score,
            }
        )

    if not rows:
        return pd.DataFrame()

    results = pd.DataFrame(rows)
    results["PCT"] = results["emf"] / results["emf"].sum()
    results["nPr"] = results["Pr"] / results["Pr"].sum()
    return results


def weibull_ranking_for_history(
    df: pd.DataFrame,
    columns: Sequence[str] = MAIN_COLS,
    max_number: int = MAX_NUMBER,
    min_failures: int = 3,
) -> Tuple[pd.DataFrame, List[int], List[int]]:
    """
    Compute Weibull-based metrics for the whole history.

    Returns
    -------
    results : DataFrame
    weibull_rank : list[int]
        Numbers sorted by Pr (descending), then emf.
    percentile_rank : list[int]
        Numbers sorted by Pct_score (descending), then emf.
    """
    hit_gaps = build_inter_hit_gaps(df, columns=columns, max_number=max_number)
    results = compute_weibull_table(hit_gaps, min_failures=min_failures)

    if results.empty:
        return results, [], []

    weibull_rank = (
        results.sort_values(by=["Pr", "emf"], ascending=[False, False])["st"]
        .astype(int)
        .tolist()
    )

    percentile_rank = (
        results.sort_values(by=["Pct_score", "emf"], ascending=[False, False])["st"]
        .astype(int)
        .tolist()
    )

    return results, weibull_rank, percentile_rank


# ======================================================================
# 3. Coverage-based greedy elimination ranking
# ======================================================================

def co_common(remaining_numbers: Iterable[int], draw_numbers: Iterable[int]) -> int:
    """Count common numbers between two collections."""
    rem_set = set(remaining_numbers)
    return sum(1 for x in draw_numbers if x in rem_set)


def greedy_elimination_pool(
    draw_data: pd.DataFrame,
    target_count: int,
    cols: Sequence[str] = MAIN_COLS,
) -> Tuple[List[int], List[int]]:
    """
    Greedy elimination of numbers 1..50 based on history coverage.

    We iteratively remove numbers that are most redundant in terms of
    how often they still cover 4/5 or 5/5 of past draws.

    Parameters
    ----------
    draw_data : DataFrame with columns st1..st5
    target_count : int
        How many numbers we want to keep at the end.
    cols : sequence of str
        Columns that contain the 5 main numbers.

    Returns
    -------
    eliminated_numbers : list[int]
        Numbers removed in order (first removed = most redundant).
    survivors : list[int]
        Numbers that survived to the end, sorted.
    """
    draws = draw_data.loc[:, cols].astype(int).to_numpy()

    # number_stats[i, 0] = number (1..50 or 0 if eliminated)
    # number_stats[i, 1..6] = counts of draws with 0..5 numbers still covered
    number_stats = np.zeros((MAX_NUMBER, 7), dtype=int)
    number_stats[:, 0] = np.arange(1, MAX_NUMBER + 1)

    eliminated_numbers: List[int] = []
    numbers_to_eliminate = MAX_NUMBER - target_count

    for _ in range(numbers_to_eliminate):
        # For each active number, simulate removing it
        for idx in range(MAX_NUMBER):
            if number_stats[idx, 0] == 0:
                continue  # already eliminated

            temp_remaining = number_stats[:, 0].copy()
            temp_remaining[idx] = 0
            rem = temp_remaining[temp_remaining != 0]

            for row in draws:
                common_count = co_common(rem, row)  # 0..5
                number_stats[idx, common_count + 1] += 1

        # Choose the number to eliminate:
        # 1) max times we still see full coverage (5/5)
        # 2) break ties with 4/5 coverage
        full_cov = number_stats[:, 6]
        max_full = full_cov.max()
        candidates = np.where(full_cov == max_full)[0]

        if len(candidates) > 1:
            four_cov = number_stats[candidates, 5]
            best_idx_local = candidates[np.argmax(four_cov)]
        else:
            best_idx_local = candidates[0]

        eliminated_numbers.append(int(number_stats[best_idx_local, 0]))
        number_stats[best_idx_local, 0] = 0
        number_stats[:, 1:7] = 0  # reset stats for next round

    survivors = sorted(int(x) for x in number_stats[:, 0] if x != 0)
    return eliminated_numbers, survivors


def greedy_coverage_ranking(
    draw_data: pd.DataFrame,
    cols: Sequence[str] = MAIN_COLS,
) -> List[int]:
    """
    Build a full 1..50 ranking from the greedy elimination process.

    We keep 5 survivors (coverage core). These are considered the
    strongest coverage numbers. The ranking is:

        [5 survivors (sorted)] + [eliminated numbers in reverse elimination order]

    which gives a clean permutation of 1..50.
    """
    eliminated, survivors = greedy_elimination_pool(
        draw_data,
        target_count=5,   # keep last 5 numbers
        cols=cols,
    )

    survivors_sorted = sorted(survivors)
    ranking = survivors_sorted + list(reversed(eliminated))
    return ranking


# ======================================================================
# 4. Conscious selection ranking (players' choices)
# ======================================================================

def compute_esym(q: np.ndarray, m: int = 5) -> float:
    """
    Compute the m-th elementary symmetric sum e_m(q):
      e_m(q) = sum over all subsets S of size m of prod_{i in S} q_i.

    Uses dynamic programming with complexity O(len(q) * m).
    """
    n = len(q)
    dp = np.zeros((n + 1, m + 1))
    dp[0, 0] = 1.0
    for i in range(1, n + 1):
        qi = q[i - 1]
        for j in range(m, -1, -1):
            dp[i, j] = dp[i - 1, j]
            if j >= 1:
                dp[i, j] += qi * dp[i - 1, j - 1]
    return float(dp[n, m])


def neg_log_lik_Q5_Q4_Q3(
    params: np.ndarray,
    draws: List[Dict[str, int]],
    M: int = MAX_NUMBER,
) -> float:
    """
    Negative log-likelihood for EuroJackpot main numbers (5-of-M),
    using Q5, Q4, and Q3 winners.

    params: array of length M+1
      params[:-1] = r_i (softmax logits for q_i)
      params[-1]  = theta (log Q)

    draws: list of dicts with keys:
      "W": list[5] winning main numbers in [1..M]
      "N5": Q5 winners
      "N4": Q4 winners
      "N3": Q3 winners
    """
    r = params[:-1]
    theta = params[-1]

    # softmax for q
    r_shift = r - np.max(r)
    exp_r = np.exp(r_shift)
    q = exp_r / np.sum(exp_r)

    Q = math.exp(theta)

    # normalizing constant for 5-number tickets
    e5 = compute_esym(q, m=5)
    if e5 <= 0 or not np.isfinite(e5):
        return np.inf

    # total pair mass across all M numbers
    sum_q2 = np.sum(q ** 2)
    e2_total = 0.5 * (1.0 - sum_q2)

    nll = 0.0
    eps = 1e-12

    for d in draws:
        W = d["W"]
        N5 = d["N5"]
        N4 = d["N4"]
        N3 = d["N3"]

        idx = [w - 1 for w in W]
        q_W = q[idx]
        prod_W = np.prod(q_W)

        if prod_W <= 0:
            if N5 > 0 or N4 > 0 or N3 > 0:
                return np.inf
            else:
                continue

        # 5-hit intensity
        lam5 = Q * prod_W / e5

        # shared quantities
        s_W = np.sum(q_W)
        s_L = max(1.0 - s_W, 0.0)
        inv_sum_1 = np.sum(1.0 / np.maximum(q_W, eps))

        # pairwise winner mass and inverse pair mass
        e2_W = 0.0
        inv_sum_2 = 0.0
        for i in range(len(q_W)):
            for j in range(i + 1, len(q_W)):
                qi, qj = q_W[i], q_W[j]
                e2_W += qi * qj
                inv_sum_2 += 1.0 / (qi * qj + eps)

        # pair mass on losers
        e2_L = e2_total - e2_W - s_W * s_L

        # 4-hit and 3-hit intensities
        lam4 = lam5 * s_L * inv_sum_1
        lam3 = lam5 * e2_L * inv_sum_2

        for lam, N in ((lam5, N5), (lam4, N4), (lam3, N3)):
            if lam < eps and N > 0:
                return np.inf

        # Poisson log-likelihood contributions
        if lam5 > eps:
            nll -= N5 * math.log(lam5) - lam5
        else:
            nll -= -lam5

        if lam4 > eps:
            nll -= N4 * math.log(lam4) - lam4
        else:
            nll -= -lam4

        if lam3 > eps:
            nll -= N3 * math.log(lam3) - lam3
        else:
            nll -= -lam3

    return float(nll)


def extract_draws_Q5_Q4_Q3(df: pd.DataFrame, M: int = MAX_NUMBER) -> List[Dict]:
    """
    Convert a DataFrame with columns st1..st5, Q5, Q4, Q3
    into a list of draw dictionaries suitable for the likelihood.
    """
    draws: List[Dict] = []
    for _, row in df.iterrows():
        try:
            W = [int(row[f"st{i}"]) for i in range(1, 6)]
            N5 = int(row["Q5"])
            N4 = int(row["Q4"])
            N3 = int(row["Q3"])
            if not all(1 <= w <= M for w in W):
                continue
            draws.append({"W": sorted(W), "N5": N5, "N4": N4, "N3": N3})
        except Exception:
            continue
    return draws


def estimate_conscious_q_euro(
    df_ej: pd.DataFrame,
    M: int = MAX_NUMBER,
    maxiter: int = 5000,
) -> List[int]:
    """
    Estimate number preferences q_i and effective ticket volume Q
    for EuroJackpot main numbers, using Q5, Q4, Q3 winners.

    Returns
    -------
      numbers_rank : list[int]
        Numbers 1..M sorted from most preferred to least preferred.
    """
    from scipy.optimize import minimize  # local import

    draws = extract_draws_Q5_Q4_Q3(df_ej, M)
    if not draws:
        raise ValueError("No valid draws with Q5/Q4/Q3 in EuroJackpot dataframe.")

    initial_r = np.zeros(M)
    avg_N5 = np.mean([d["N5"] for d in draws])

    comb_val = math.comb(M, 5)
    theta0 = math.log((avg_N5 + 1e-3) * comb_val)
    initial_params = np.concatenate([initial_r, [theta0]])

    res = minimize(
        neg_log_lik_Q5_Q4_Q3,
        initial_params,
        args=(draws, M),
        method="L-BFGS-B",
        options={"maxiter": maxiter, "ftol": 1e-10},
    )

    if not res.success:
        raise RuntimeError(f"Conscious selection fit failed: {res.message}")

    r_hat = res.x[:-1]
    theta_hat = res.x[-1]

    exp_r = np.exp(r_hat - np.max(r_hat))
    q_hat = exp_r / np.sum(exp_r)
    _Q_hat = math.exp(theta_hat)  # kept for completeness

    # sort numbers by q descending (most preferred first)
    number_prefs = sorted(
        [(i + 1, float(q_hat[i])) for i in range(M)],
        key=lambda x: x[1],
        reverse=True,
    )
    numbers_rank = [x[0] for x in number_prefs]
    return numbers_rank


# ======================================================================
# 5. Covering helpers and mapping
# ======================================================================

def normalize_combination_frame(df: pd.DataFrame) -> pd.DataFrame:
    """
    Take a raw covering DataFrame (possibly with extra columns/strings)
    and return a clean (st1..st5) frame of sorted integer combinations.
    """
    df_num = df.map(lambda x: pd.to_numeric(x, errors="coerce"))
    df_num = df_num.dropna(how="all")

    def sort_row(row: pd.Series) -> pd.Series:
        vals = [int(v) for v in row.dropna().tolist() if 1 <= int(v) <= MAX_NUMBER]
        vals = sorted(vals)[:5]
        if len(vals) < 5:
            vals += [np.nan] * (5 - len(vals))
        return pd.Series(vals)

    df_sorted = df_num.apply(sort_row, axis=1)
    df_sorted.columns = ["st1", "st2", "st3", "st4", "st5"]
    return df_sorted


def mapping_covering(
    covering: pd.DataFrame,
    ranked_nums: Sequence[int],
) -> pd.DataFrame:
    """
    Remap a generic 5-number covering (with labels 1..50) to actual
    EuroJackpot numbers using a ranked list.

    Parameters
    ----------
    covering : DataFrame
        DataFrame with columns 'st1'..'st5'. Values are 1..50 labels,
        interpreted as positions in the ranking (1 = best, 50 = worst).
    ranked_nums : sequence of int
        Length-50 sequence of distinct integers (usually 1..50),
        ordered from most to least preferred. ranked_nums[0] replaces 1,
        ranked_nums[1] replaces 2, etc.

    Returns
    -------
    mapped : DataFrame
        Copy of `covering` where st1..st5 are remapped through
        the ranking and then sorted in ascending order per row.
    """
    if len(ranked_nums) != MAX_NUMBER:
        raise ValueError(f"ranked_nums must have length {MAX_NUMBER}.")

    mapping = {i + 1: int(ranked_nums[i]) for i in range(MAX_NUMBER)}

    cols = ["st1", "st2", "st3", "st4", "st5"]
    for c in cols:
        if c not in covering.columns:
            raise ValueError(f"Column '{c}' not found in covering DataFrame.")

    mapped = covering.copy()

    def _map_and_sort(row: pd.Series) -> pd.Series:
        nums = [mapping[int(row[c])] for c in cols]
        nums.sort()
        return pd.Series(nums, index=cols)

    mapped[cols] = mapped[cols].apply(_map_and_sort, axis=1)
    return mapped


# ======================================================================
# 6. Hit checking functions
# ======================================================================

def build_hit_index(
    combos_df: pd.DataFrame,
) -> Tuple[set, Dict[Tuple[int, int, int, int], int]]:
    """
    Build helpers for hit checking:
      - combo_set_5 : set of 5-tuples (full combinations)
      - four_dict   : counts of 4-subsets across all combinations
    """
    combo_tuples = [
        tuple(row) for row in combos_df[["st1", "st2", "st3", "st4", "st5"]].to_numpy()
    ]
    combo_set_5 = set(combo_tuples)

    four_dict: Dict[Tuple[int, int, int, int], int] = {}
    for comb in combo_tuples:
        for T in combinations(comb, 4):
            four_dict[T] = four_dict.get(T, 0) + 1

    return combo_set_5, four_dict


def backtest_hits(
    df_hist: pd.DataFrame,
    combos_df: pd.DataFrame,
    cols: Sequence[str] = MAIN_COLS,
) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """
    For each historical draw, count:
      - exact 5-hit lines in combos_df
      - 4-hit-only lines (lines with exactly 4 common numbers)
      - whether there was at least one ≥4-hit line that draw

    Returns
    -------
    hits_df : DataFrame with per-draw details
    summary : dict with totals and coverage rate
    """
    combo_set_5, four_dict = build_hit_index(combos_df)

    records: List[Dict[str, float]] = []
    for idx, row in df_hist.iterrows():
        draw_nums = sorted(int(row[c]) for c in cols)
        draw5 = tuple(draw_nums)

        five_hits = 1 if draw5 in combo_set_5 else 0

        sum_four = 0
        for T in combinations(draw5, 4):
            sum_four += four_dict.get(T, 0)

        # 5-hits contribute 5 fours each; remove those from pure 4-hit count
        four_hits = sum_four - 5 * five_hits

        records.append(
            {
                "idx": idx,
                "Date": row.get("Date", None),
                "five_hits": five_hits,
                "four_hits": four_hits,
                "any_4plus": 1 if (four_hits + five_hits) > 0 else 0,
            }
        )

    hits_df = pd.DataFrame(records)
    total_five = int(hits_df["five_hits"].sum())
    total_four_only = int(hits_df["four_hits"].sum())
    total_draws = len(df_hist)
    draws_with_4plus = int(hits_df["any_4plus"].sum())

    summary = {
        "total_five_hits": total_five,
        "total_four_only_hits": total_four_only,
        "total_draws": total_draws,
        "draws_with_4plus": draws_with_4plus,
        "draw_coverage_rate_4plus": draws_with_4plus / total_draws,
    }
    return hits_df, summary


# ======================================================================
# 7. Putting it all together
# ======================================================================

def main() -> None:
    # --- Load historical data ---
    df_hist = pd.read_csv(HIST_PATH, index_col=0)

    print("Building rankings from full history...")
    spacing_rank = spacing_ranking(df_hist, MAIN_COLS)

    _, weibull_rank, _ = weibull_ranking_for_history(df_hist, MAIN_COLS)
    greedy_rank = greedy_coverage_ranking(df_hist, MAIN_COLS)
    conscious_rank = estimate_conscious_q_euro(df_hist, M=MAX_NUMBER, maxiter=5000)

    # --- Load and normalize covering for 50 numbers ---
    covering_50_raw = pd.read_csv(COVERING_PATH)
    covering_50 = normalize_combination_frame(covering_50_raw)

    print("Mapping covering with the four rankings...")
    mapped_spacing = mapping_covering(covering_50, spacing_rank)
    mapped_weibull = mapping_covering(covering_50, weibull_rank)
    mapped_greedy = mapping_covering(covering_50, greedy_rank)
    mapped_cons = mapping_covering(covering_50, conscious_rank)

    combined_df = pd.concat(
        [mapped_spacing, mapped_weibull, mapped_greedy, mapped_cons],
        ignore_index=True,
    )

    combined_unique = combined_df.drop_duplicates(
        subset=["st1", "st2", "st3", "st4", "st5"]
    ).reset_index(drop=True)

    print(f"\nUnion size after dedup: {len(combined_unique)} lines")

    # --- Backtesting against full history ---
    print("\nBacktesting hits against full history...")
    t0 = time.time()
    hits_df, summary_stats = backtest_hits(df_hist, combined_unique, MAIN_COLS)
    t1 = time.time()

    print("\nBacktest summary:")
    for k, v in summary_stats.items():
        print(f"  {k}: {v}")
    print(f"Backtest time: {t1 - t0:.2f}s")

    # --- Random baseline comparison ---
    from math import comb as nCk

    total_combos_universe = nCk(MAX_NUMBER, 5)
    p_5 = 1 / total_combos_universe
    p_4only = (nCk(5, 4) * nCk(MAX_NUMBER - 5, 1)) / total_combos_universe
    p_4plus = p_5 + p_4only

    expected_5_per_draw = len(combined_unique) * p_5
    expected_4plus_per_draw = len(combined_unique) * p_4plus

    actual_5_per_draw = summary_stats["total_five_hits"] / summary_stats["total_draws"]
    actual_4plus_per_draw = (
        summary_stats["total_four_only_hits"] + summary_stats["total_five_hits"]
    ) / summary_stats["total_draws"]

    print("\nRandom baseline comparison:")
    print(f"  Expected 5-hits per draw     : {expected_5_per_draw:.6f}")
    print(f"  Actual 5-hits per draw       : {actual_5_per_draw:.6f}")
    print(f"  Expected ≥4 hits per draw    : {expected_4plus_per_draw:.6f}")
    print(f"  Actual ≥4 hits per draw      : {actual_4plus_per_draw:.6f}")
    print(f"  Lift on 5-hits               : {actual_5_per_draw / expected_5_per_draw:.3f}")
    print(
        f"  Lift on ≥4 hits              : {actual_4plus_per_draw / expected_4plus_per_draw:.3f}"
    )


if __name__ == "__main__":
    main()
