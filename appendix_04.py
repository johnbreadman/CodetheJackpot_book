"""
Code the Jackpot - Appendix 4 – Full Python Script for C(N, 5, 4) Coverings
Auto-extracted (book order). Full listings, nothing truncated.
"""


# ======================================================================
# Appendix 4 – Full Python Script for C(N, 5, 4) Coverings
# ======================================================================
import itertools
import math
import os
import sys
import time
from typing import List, Tuple

import numpy as np
import pandas as pd

# -----------------------------
# Parameters
# -----------------------------
N = 50
K = 5
C = 4

VERBOSE = True
LOG_EVERY_CHOICES = 1000      # log every X accepted combos
CHUNK_SIZE = 200_000          # how many candidates to process per vectorized chunk

# -----------------------------
# Validation
# -----------------------------
if not (1 <= C < K <= N):
    print("Invalid parameters: Ensure that 1 <= C < K <= N.")
    sys.exit(1)

# -----------------------------
# Helpers
# -----------------------------
def combo_to_mask(combo: Tuple[int, ...]) -> np.uint64:
    m = 0
    for x in combo:
        m |= (1 << (x - 1))
    return np.uint64(m)

def mask_to_tuple(m: int, N: int) -> Tuple[int, ...]:
    return tuple(i + 1 for i in range(N) if (m >> i) & 1)

# 16-bit popcount lookup table
def _make_popcnt16() -> np.ndarray:
    t = np.arange(1 << 16, dtype=np.uint16)
    return np.array([int(bin(x).count("1")) for x in t], dtype=np.uint8)

POPCNT16 = _make_popcnt16()

def popcount64(arr_u64: np.ndarray) -> np.ndarray:
    """Vectorized popcount for uint64 array using 16-bit lookup."""
    view16 = arr_u64.view(np.uint16).reshape(arr_u64.size, 4)  # 4 * 16 = 64
    return (POPCNT16[view16[:, 0]] +
            POPCNT16[view16[:, 1]] +
            POPCNT16[view16[:, 2]] +
            POPCNT16[view16[:, 3]]).astype(np.int16)

# -----------------------------
# Build combinations & masks
# -----------------------------
t0 = time.perf_counter()
initial_combos = list(itertools.combinations(range(1, N + 1), K))
masks = np.fromiter((combo_to_mask(c) for c in initial_combos), dtype=np.uint64, count=len(initial_combos))
total = masks.size
t1 = time.perf_counter()

if VERBOSE:
    print(f"[INIT] N={N}, K={K}, C={C}, total candidates={total:,}")
    print(f"[INIT] Built combinations & bitmasks in {t1 - t0:.3f}s")


# -----------------------------
# Vectorized single-process sieve-greedy
# -----------------------------
def sieve_greedy_vectorized() -> List[int]:
    valid = np.ones(total, dtype=np.uint8)  # 1 = candidate still available
    accepted_indices: List[int] = []

    last_report = time.perf_counter()
    # Scan left -> right; when we accept i, mark conflicts (|∩| >= C) as invalid in vectorized chunks
    for i in range(total):
        if not valid[i]:
            continue

        accepted_indices.append(i)
        valid[i] = 0  # do not reconsider this one

        # Vectorized marking over remaining indices in chunks
        base = i + 1
        if base < total:
            # Process [base:total) in chunks
            remaining = total - base
            n_chunks = math.ceil(remaining / CHUNK_SIZE)
            cm = masks[i]

            for ck in range(n_chunks):
                s = base + ck * CHUNK_SIZE
                e = min(base + (ck + 1) * CHUNK_SIZE, total)

                # Filter to still-valid only to save work
                idx = np.nonzero(valid[s:e])[0]
                if idx.size == 0:
                    continue
                sl = s + idx  # absolute indices of valid items in this chunk

                # Compute overlaps: popcount((cm & chunk_masks)) >= C
                and_vals = np.bitwise_and(cm, masks[sl])
                counts = popcount64(and_vals)
                kill = (counts >= C)

                if kill.any():
                    valid[sl[kill]] = 0

        # Progress logs
        if VERBOSE and (len(accepted_indices) % LOG_EVERY_CHOICES == 0 or i == total - 1):
            now = time.perf_counter()
            print(f"[PROGRESS] i={i:,}/{total:,} | chosen={len(accepted_indices):,} "
                  f"| window ~{(total - (i+1)):,} | dt={now - last_report:.2f}s")
            last_report = now

    return accepted_indices

run_start = time.perf_counter()
chosen_idx = sieve_greedy_vectorized()
run_end = time.perf_counter()

# -----------------------------
# Save covering
# -----------------------------
covering_combos = [mask_to_tuple(int(masks[i]), N) for i in chosen_idx]
cols = [f"st{i}" for i in range(1, K + 1)]
df = pd.DataFrame(covering_combos, columns=cols)
os.makedirs("jkr_data", exist_ok=True)
out_path = f"jkr_data/covering_{N}_{K}_{C}_{len(covering_combos)}.csv"
df.to_csv(out_path, index=False)

print("\n=== SUMMARY ===")
print(f"Candidates (N choose K): {total:,}")
print(f"Chosen set size        : {len(covering_combos):,}")
print(f"Build combos time      : {t1 - t0:.3f}s")
print(f"Greedy (vectorized)    : {run_end - run_start:.3f}s")
print(f"Saved                  : {out_path}")

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Conscious-selection ranking and band-pattern strategy tournament
for EuroJackpot 5/50 main numbers.

This script:

  1. Fits a conscious-selection model using Q5, Q4, Q3 winners.
  2. Builds three popularity bands (NPR1, NPR2, NPR3).
  3. Runs a "strategy tournament" over history, checking which
     band-hit patterns (k1, k2, k3) are stable and attractive.
  4. Provides helpers to:
       - recompute latest bands using history rounded to the last
         full block of 100 draws,
       - filter candidate 5-number combinations by pattern.
"""

import math
from math import comb
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy.optimize import minimize


# ------------------------------------------------------------
# User configuration
# ------------------------------------------------------------

# Milestone step (in draws) for the tournament checkpoints.
# Choose 50 (checkpoints every 50 draws) or 100 (every 100 draws).
M = 50  # <-- change to 100 if you want checkpoints at 300, 400, 500, ...

# EuroJackpot main numbers are always 1..50:
M_MAIN = 50


# ------------------------------------------------------------
# Core helper: elementary symmetric sum e_m(q)
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# Negative log-likelihood for EuroJackpot (Q5, Q4, Q3)
# ------------------------------------------------------------

def neg_log_lik_Q5_Q4_Q3(
    params: np.ndarray,
    draws: List[Dict[str, int]],
    M_main: int = 50,
) -> float:
    """
    Negative log-likelihood for EuroJackpot main numbers (5-of-M_main),
    using Q5, Q4, and Q3 winners.

    params[:-1] = logits r_i  (for softmax q_i)
    params[-1]  = theta = log(Q)
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

    # total pair mass across all M_main numbers
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
            # If prod_W is effectively zero but there are winners,
            # the likelihood is essentially zero -> infinite nll.
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
        # (ignoring log(N!) constants).
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

    return nll


# ------------------------------------------------------------
# Data extraction from EuroJackpot DataFrame
# ------------------------------------------------------------

def extract_draws_Q5_Q4_Q3(df: pd.DataFrame, M_main: int = 50) -> List[Dict[str, int]]:
    """
    Convert a EuroJackpot DataFrame with columns:
      st1..st5 (main numbers), Q5, Q4, Q3
    into a list of draw dictionaries for the likelihood.
    """
    draws = []
    for _, row in df.iterrows():
        try:
            W = [int(row[f"st{i}"]) for i in range(1, 6)]
            N5 = int(row["Q5"])
            N4 = int(row["Q4"])
            N3 = int(row["Q3"])
            if not all(1 <= w <= M_main for w in W):
                continue
            draws.append({"W": sorted(W), "N5": N5, "N4": N4, "N3": N3})
        except Exception:
            continue

    return draws


# ------------------------------------------------------------
# Estimation of conscious-selection q and Q_hat
# ------------------------------------------------------------

def estimate_conscious_q_euro(
    df_ej: pd.DataFrame,
    M_main: int = 50,
    maxiter: int = 5000,
) -> Tuple[np.ndarray, float, List[Tuple[int, float]]]:
    """
    Estimate number preferences q_i and effective ticket volume Q
    for EuroJackpot main numbers, using Q5, Q4, Q3 winners.

    Returns q_hat, Q_hat, and number_prefs sorted ascending by q_i.
    """
    draws = extract_draws_Q5_Q4_Q3(df_ej, M_main=M_main)
    if not draws:
        raise ValueError("No valid draws in EuroJackpot dataframe.")

    # Initial values
    initial_r = np.zeros(M_main)
    avg_N5 = np.mean([d["N5"] for d in draws])

    comb_val = comb(M_main, 5)
    theta0 = math.log((avg_N5 + 1e-3) * comb_val)
    initial_params = np.concatenate([initial_r, [theta0]])

    res = minimize(
        neg_log_lik_Q5_Q4_Q3,
        initial_params,
        args=(draws, M_main),
        method="L-BFGS-B",
        options={"maxiter": maxiter, "ftol": 1e-10},
    )

    if not res.success:
        raise RuntimeError(f"Numerical search failed: {res.message}")

    r_hat = res.x[:-1]
    theta_hat = res.x[-1]

    exp_r = np.exp(r_hat - np.max(r_hat))
    q_hat = exp_r / np.sum(exp_r)
    Q_hat = math.exp(theta_hat)

    number_prefs = sorted(
        [(i + 1, float(q_hat[i])) for i in range(M_main)],
        key=lambda x: x[1],
    )

    return q_hat, Q_hat, number_prefs


# ------------------------------------------------------------
# Popularity bands: NPR1, NPR2, NPR3 (17, 17, 16)
# ------------------------------------------------------------

def build_bands_50(number_prefs: List[Tuple[int, float]]) -> Tuple[List[int], List[int], List[int]]:
    """
    Split 50 EuroJackpot numbers into 3 popularity bands:
      NPR1: 17 least popular
      NPR2: next 17
      NPR3: 16 most popular
    """
    if len(number_prefs) != 50:
        raise ValueError("number_prefs must contain 50 entries.")

    NPR1 = [num for num, q in number_prefs[0:17]]
    NPR2 = [num for num, q in number_prefs[17:34]]
    NPR3 = [num for num, q in number_prefs[34:50]]

    return NPR1, NPR2, NPR3


# ------------------------------------------------------------
# Band hit distribution for given bands
# ------------------------------------------------------------

def band_hit_distribution(
    df_ej: pd.DataFrame,
    NPR1: List[int],
    NPR2: List[int],
    NPR3: List[int],
) -> pd.DataFrame:
    """
    For each EuroJackpot draw in df_ej, count how many of the 5 main
    winning numbers fall into NPR1, NPR2, NPR3.
    """
    set1 = set(NPR1)
    set2 = set(NPR2)
    set3 = set(NPR3)

    records = []

    for idx, row in df_ej.iterrows():
        try:
            W = [int(row[f"st{i}"]) for i in range(1, 6)]
            Q5 = int(row["Q5"])
            Q4 = int(row["Q4"])
            Q3 = int(row["Q3"])
        except Exception:
            continue

        c1 = sum(1 for w in W if w in set1)
        c2 = sum(1 for w in W if w in set2)
        c3 = sum(1 for w in W if w in set3)

        records.append(
            {
                "draw_idx": idx,
                "NPR1_hits": c1,
                "NPR2_hits": c2,
                "NPR3_hits": c3,
                "Q5": Q5,
                "Q4": Q4,
                "Q3": Q3,
            }
        )

    bh = pd.DataFrame(records).set_index("draw_idx")
    return bh


# ------------------------------------------------------------
# Latest bands using history rounded to last full 100 draws
# ------------------------------------------------------------

def compute_latest_bands_rounded(
    df_ej: pd.DataFrame,
    M_main: int = 50,
    base: int = 100,
) -> Tuple[int, np.ndarray, float, List[Tuple[int, float]], List[int], List[int], List[int]]:
    """
    Compute the most recent NPR1/NPR2/NPR3 bands using history
    rounded down to the last full 'base' draws (default: 100).

    Example:
      - If len(df_ej) = 937 and base=100, use first 900 draws.
      - If len(df_ej) = 890, use first 800 draws.
    """
    n = len(df_ej)
    n_hist = (n // base) * base
    if n_hist < 300:
        raise ValueError("Need at least 300 draws after rounding to build bands.")

    df_hist = df_ej.iloc[:n_hist].copy()
    q_hat, Q_hat, number_prefs = estimate_conscious_q_euro(df_hist, M_main)
    NPR1, NPR2, NPR3 = build_bands_50(number_prefs)

    return n_hist, q_hat, Q_hat, number_prefs, NPR1, NPR2, NPR3


# ------------------------------------------------------------
# Helper: baseline band-pattern probabilities (hypergeometric)
# ------------------------------------------------------------

def build_pattern_baseline_probs(
    size1: int = 17,
    size2: int = 17,
    size3: int = 16,
    M_main: int = 50,
) -> Dict[Tuple[int, int, int], float]:
    """
    Build baseline probabilities for all band-hit patterns (k1, k2, k3)
    such that k1 + k2 + k3 = 5, using a pure combinatorial
    hypergeometric model over bands of size (size1, size2, size3).

    P(k1,k2,k3) = [C(size1, k1) * C(size2, k2) * C(size3, k3)] / C(M_main, 5)
    """
    denom = comb(M_main, 5)
    pattern_probs: Dict[Tuple[int, int, int], float] = {}

    for k1 in range(0, 6):
        for k2 in range(0, 6):
            for k3 in range(0, 6):
                if k1 + k2 + k3 != 5:
                    continue
                if k1 > size1 or k2 > size2 or k3 > size3:
                    continue
                p = (
                    comb(size1, k1)
                    * comb(size2, k2)
                    * comb(size3, k3)
                    / denom
                )
                pattern_probs[(k1, k2, k3)] = p

    return pattern_probs


# ------------------------------------------------------------
# Strategy tournament over milestones
# ------------------------------------------------------------

def run_strategy_tournament(
    df_ej: pd.DataFrame,
    M_main: int = 50,
    milestones: List[int] = None,
    top_k: int = 21,
    min_count: int = 5,
) -> None:
    """
    Run the "strategy tournament" over a set of milestones.

    Timeline logic (history making):
      - At milestone 300: fit NPR bands on first 300 draws.
        These bands are used for draws 1..next_milestone (e.g. 1..400).
      - At milestone 400: refit NPR bands on first 400 draws.
        These bands are used only for the NEXT block of draws
        (e.g. 401..500), while 1..400 keep their original band assignment.
      - At milestone 500: refit on 1..500 and use for 501..600, etc.

    At each checkpoint D we compute:
      - count of each pattern (k1, k2, k3),
      - lift = freq(pattern) / hypergeom_baseline(pattern),
      - avg_Q5(pattern),
      - Q5_lift(pattern) = avg_Q5(pattern) / global_avg_Q5.
    """
    if milestones is None or len(milestones) < 2:
        raise ValueError("Provide at least two milestones (e.g. [300, 400, ...]).")

    # Restrict milestones so that they do not exceed history length.
    max_draws = len(df_ej)
    milestones = [m for m in milestones if m <= max_draws]
    if len(milestones) < 2:
        raise ValueError("After trimming to available draws, less than two milestones remain.")

    first_checkpoint = milestones[0]
    last_checkpoint = milestones[-1]

    # 1) Fit bands at each milestone.
    bands_by_milestone: Dict[int, Tuple[List[int], List[int], List[int]]] = {}
    q_by_milestone: Dict[int, np.ndarray] = {}
    Q_by_milestone: Dict[int, float] = {}

    for m in milestones:
        df_hist = df_ej.iloc[:m].copy()
        q_hat, Q_hat, number_prefs = estimate_conscious_q_euro(df_hist, M_main)
        NPR1, NPR2, NPR3 = build_bands_50(number_prefs)

        bands_by_milestone[m] = (NPR1, NPR2, NPR3)
        q_by_milestone[m] = q_hat
        Q_by_milestone[m] = Q_hat

        print(f"\n=== Bands fitted on first {m} draws ===")
        print("Sum of q_hat:", float(np.sum(q_hat)))
        print("Estimated Q_hat:", Q_hat)
        print("NPR1:", NPR1)
        print("NPR2:", NPR2)
        print("NPR3:", NPR3)

    # 2) Build band schedule over draws (which milestone's bands
    #    are "active" at each draw index).
    #
    # Example (milestones = [300, 400, 500, 600, 700, 800, 900]):
    #   - m=300 bands used for draws 1..400
    #   - m=400 bands used for draws 401..500
    #   - m=500 bands used for draws 501..600
    #   ...
    #   - m=800 bands used for draws 801..900
    #
    band_schedule: Dict[int, int] = {}

    for i in range(len(milestones) - 1):
        m_current = milestones[i]
        m_next = milestones[i + 1]

        if i == 0:
            start_draw = 1
        else:
            start_draw = milestones[i] + 1

        end_draw = m_next  # inclusive

        for d in range(start_draw, end_draw + 1):
            band_schedule[d] = m_current

    max_draw = last_checkpoint

    # Precompute set versions of bands for quick membership tests.
    band_sets_by_milestone: Dict[int, Tuple[set, set, set]] = {}
    for m, (NPR1, NPR2, NPR3) in bands_by_milestone.items():
        band_sets_by_milestone[m] = (set(NPR1), set(NPR2), set(NPR3))

    # 3) Precompute pattern (k1, k2, k3) and Q5 for each draw
    #    according to the band schedule.
    draw_info: List[Dict[str, int]] = []

    for d in range(1, max_draw + 1):
        row = df_ej.iloc[d - 1]
        try:
            W = [int(row[f"st{i}"]) for i in range(1, 6)]
            Q5 = int(row["Q5"])
        except Exception:
            continue

        m_active = band_schedule.get(d, None)
        if m_active is None:
            # No bands defined for this draw in the schedule
            continue

        set1, set2, set3 = band_sets_by_milestone[m_active]

        k1 = sum(1 for w in W if w in set1)
        k2 = sum(1 for w in W if w in set2)
        k3 = sum(1 for w in W if w in set3)

        draw_info.append(
            {
                "draw": d,
                "m_active": m_active,
                "k1": k1,
                "k2": k2,
                "k3": k3,
                "Q5": Q5,
            }
        )

    # 4) Build baseline pattern probabilities.
    pattern_probs = build_pattern_baseline_probs(size1=17, size2=17, size3=16, M_main=M_main)

    # 5) Strategy tournament: step through milestones and evaluate patterns.
    survivor_patterns = None

    for D in milestones:
        if D > max_draw:
            continue

        # History up to D
        history_draws = [info for info in draw_info if info["draw"] <= D]
        if not history_draws:
            continue

        global_avg_Q5 = float(np.mean([info["Q5"] for info in history_draws]))

        # Count patterns and accumulate Q5 by pattern.
        pattern_counts: Dict[Tuple[int, int, int], int] = {}
        pattern_Q5_sums: Dict[Tuple[int, int, int], float] = {}

        for info in history_draws:
            key = (info["k1"], info["k2"], info["k3"])
            pattern_counts[key] = pattern_counts.get(key, 0) + 1
            pattern_Q5_sums[key] = pattern_Q5_sums.get(key, 0.0) + float(info["Q5"])

        # Build summary table for patterns with count >= min_count.
        rows = []
        for key, count in pattern_counts.items():
            if count < min_count:
                continue

            k1, k2, k3 = key
            p0 = pattern_probs.get(key, 0.0)
            freq = count / len(history_draws)
            lift = freq / p0 if p0 > 0 else float("nan")
            avg_Q5 = pattern_Q5_sums[key] / count
            Q5_lift = avg_Q5 / global_avg_Q5 if global_avg_Q5 > 0 else float("nan")

            rows.append(
                {
                    "pattern": key,
                    "k1": k1,
                    "k2": k2,
                    "k3": k3,
                    "count": count,
                    "lift": lift,
                    "avg_Q5": avg_Q5,
                    "Q5_lift": Q5_lift,
                }
            )

        if not rows:
            continue

        summary = pd.DataFrame(rows)
        # Sort by Q5_lift ascending (small -> large).
        # Flip ascending=False if you want strongest Q5-lift first.
        summary = summary.sort_values(by="Q5_lift", ascending=True).reset_index(drop=True)

        print(f"\n=== CHECKPOINT D={D} (after {D} draws) ===")
        print(f"Global avg Q5 up to D={D}: {global_avg_Q5:.3f}")
        print(f"Number of patterns with count >= {min_count}: {len(summary)}\n")

        print(f"Top {top_k} patterns at D={D} (k1,k2,k3 | count | lift | avg_Q5 | Q5_lift):")
        for _, row in summary.head(top_k).iterrows():
            pat = row["pattern"]
            count = int(row["count"])
            lift = float(row["lift"])
            avg_Q5 = float(row["avg_Q5"])
            Q5_lift = float(row["Q5_lift"])
            print(
                f"  {pat} | count={count} | "
                f"lift={lift:.3f} | avg_Q5={avg_Q5:.3f} | Q5_lift={Q5_lift:.3f}"
            )

        # Survivor patterns from the first checkpoint D=first_checkpoint.
        if survivor_patterns is None and D == first_checkpoint:
            survivor_patterns = set(summary["pattern"])
        elif survivor_patterns is not None:
            current_top = set(summary["pattern"])
            survivors_now = sorted(survivor_patterns.intersection(current_top))
            print(
                f"\nSurvivors from D={first_checkpoint} still in top_{top_k} at D={D}:"
            )
            print(survivors_now)
            survivor_patterns = survivor_patterns.intersection(current_top)

# ------------------------------------------------------------
# Filtering helper for candidate combinations
# ------------------------------------------------------------

def filter_combinations_by_patterns(
    df_combis: pd.DataFrame,
    NPR1: List[int],
    NPR2: List[int],
    NPR3: List[int],
    num_cols: List[str],
    keep_patterns: List[Tuple[int, int, int]],
) -> pd.DataFrame:
    """
    Filter a combinations dataframe by band-hit patterns.

    Each row in df_combis is a candidate 5-number combination
    stored in columns given by `num_cols` (e.g. ["no1", "no2", "no3", "no4", "no5"]).

    We compute, for each row, the counts (k1, k2, k3) of numbers that fall
    into NPR1, NPR2, NPR3 respectively. Rows whose pattern (k1, k2, k3)
    is in keep_patterns are retained.
    """
    set1 = set(NPR1)
    set2 = set(NPR2)
    set3 = set(NPR3)
    keep_set = set(keep_patterns)

    filtered_rows = []
    for idx, row in df_combis.iterrows():
        try:
            nums = [int(row[col]) for col in num_cols]
        except Exception:
            continue

        k1 = sum(1 for n in nums if n in set1)
        k2 = sum(1 for n in nums if n in set2)
        k3 = sum(1 for n in nums if n in set3)
        pattern = (k1, k2, k3)

        if pattern in keep_set:
            record = row.to_dict()
            record["pattern"] = pattern
            filtered_rows.append(record)

    if not filtered_rows:
        return pd.DataFrame(columns=list(df_combis.columns) + ["pattern"])

    return pd.DataFrame(filtered_rows)


# ------------------------------------------------------------
# Main entry point
# ------------------------------------------------------------

def main() -> None:
    # Adjust the path to your EuroJackpot history file as needed.
    csv_path = "data/total_nikstiles.csv"

    print("Loading EuroJackpot data from:", csv_path)
    df_ej = pd.read_csv(csv_path, index_col=0)

    if len(df_ej) < 300:
        raise ValueError("Need at least 300 draws in df_ej for this analysis.")

    # Build milestones based on current history length and chosen step M.
    # We round the history down to the last full 100 draws, then step
    # from 300 upwards in increments of M.
    last_full_100 = (len(df_ej) // 100) * 100
    milestones = list(range(300, last_full_100 + 1, M))

    print("\nMilestones (checkpoints in draws):", milestones)

    # Run the strategy tournament on these milestones.
    run_strategy_tournament(
        df_ej,
        M_main=M_MAIN,
        milestones=milestones,
        top_k=21,
        min_count=5,
    )

    # Compute the latest NPR bands using history rounded to last full 100 draws.
    print("\n\n=== Latest bands using history rounded to last full 100 draws ===")
    n_hist, q_hat_latest, Q_hat_latest, prefs_latest, NPR1_latest, NPR2_latest, NPR3_latest = (
        compute_latest_bands_rounded(df_ej, M_main=M_MAIN, base=100)
    )
    print(f"Number of draws used: {n_hist}")
    print("Sum of q_hat:", float(np.sum(q_hat_latest)))
    print("Estimated Q_hat:", Q_hat_latest)
    print("NPR1_latest:", NPR1_latest)
    print("NPR2_latest:", NPR2_latest)
    print("NPR3_latest:", NPR3_latest)

    # Example usage of the filtering helper (commented):
    #
    # best_patterns = [
    #     (0, 2, 3),
    #     (0, 1, 4),
    #     (1, 2, 2),
    # ]
    # df_combis = pd.read_csv("data/all_5of50_combinations.csv")
    # filtered = filter_combinations_by_patterns(
    #     df_combis,
    #     NPR1_latest,
    #     NPR2_latest,
    #     NPR3_latest,
    #     num_cols=["no1", "no2", "no3", "no4", "no5"],
    #     keep_patterns=best_patterns,
    # )
    # print("Filtered combinations shape:", filtered.shape)

if __name__ == "__main__":
    main()
