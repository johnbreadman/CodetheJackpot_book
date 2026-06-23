"""
Code the Jackpot - 5.17 Creating a Playbook: Combining Features and Strategies
Auto-extracted (book order). Full listings, nothing truncated.
"""


# ======================================================================
# Code: Searching Bands for a Single Feature
# ======================================================================
import numpy as np

import pandas as pd

def compute_lift(hk: int, hn: int, baseline_p: float) -> float:

    # Compute the lift of a band, given:

    #   hk : number of 5-hits inside the band

    #   hn : number of combinations inside the band

    #   baseline_p : overall 5-hit probability in that split

    if hn == 0:

        return 0.0

    p_band = hk / hn

    if baseline_p == 0:

        return 0.0

    return p_band / baseline_p

def evaluate_band_for_feature(df_split: pd.DataFrame,

                              feature: str,

                              l: float,

                              u: float,

                              target_col: str = "is_5hit") -> tuple[int, int]:

    # For one dataset split (train, val or test), count how many rows

    # satisfy the band l <= feature <= u, and how many of them are 5-hits.

    mask = (df_split[feature] >= l) & (df_split[feature] <= u)

    sub = df_split.loc[mask]

    hn = len(sub)

    hk = int(sub[target_col].sum())

    return hk, hn

def find_best_band_for_feature(df_train: pd.DataFrame,

                               df_val: pd.DataFrame,

                               df_test: pd.DataFrame,

                               feature: str,

                               candidate_lows,

                               candidate_highs,

                               target_col: str = "is_5hit") -> dict:

    # Scan a grid of candidate (l, u) values and keep the band that

    # maximises validation lift, subject to minimum selectivity s_p.

    #

    # The function returns a dictionary with:

    #   feature, l, u, s_p,

    #   hk_train, hn_train, L_train,

    #   hk_val,   hn_val,   L_val,

    #   hk_test,  hn_test,  L_test

    # Baseline probabilities for each split

    total_train = len(df_train)

    total_val   = len(df_val)

    total_test  = len(df_test)

    p0_train = df_train[target_col].mean()

    p0_val   = df_val[target_col].mean()

    p0_test  = df_test[target_col].mean()

    best_band = None

    best_L_val = -np.inf

    for l in candidate_lows:

        for u in candidate_highs:

            if u < l:

                continue  # invalid band

            # Evaluate band on each split

            hk_tr, hn_tr = evaluate_band_for_feature(df_train, feature, l, u, target_col)

            hk_va, hn_va = evaluate_band_for_feature(df_val,   feature, l, u, target_col)

            hk_te, hn_te = evaluate_band_for_feature(df_test,  feature, l, u, target_col)

            # Selectivity on train

            s_p = hn_tr / total_train if total_train > 0 else 0.0

            # Ignore bands that are too restrictive (e.g. keep < 5% of data)

            if s_p < 0.05:

                continue

            # Compute lifts

            L_tr = compute_lift(hk_tr, hn_tr, p0_train)

            L_va = compute_lift(hk_va, hn_va, p0_val)

            L_te = compute_lift(hk_te, hn_te, p0_test)

            # Keep the band with the highest validation lift

            if L_va > best_L_val:

                best_L_val = L_va

                best_band = {

                    "feature":   feature,

                    "l":         float(l),

                    "u":         float(u),

                    "s_p":       float(s_p),

                    "hk_train":  int(hk_tr),

                    "hn_train":  int(hn_tr),

                    "L_train":   float(L_tr),

                    "hk_val":    int(hk_va),

                    "hn_val":    int(hn_va),

                    "L_val":     float(L_va),

                    "hk_test":   int(hk_te),

                    "hn_test":   int(hn_te),

                    "L_test":    float(L_te),

                }

    return best_band


# ======================================================================
# Step 2 – Building the Feature Leaderboard
# ======================================================================
def build_feature_leaderboard(df_train, df_val, df_test, feature_names, target_col="is_5hit"):

    rows = []

    for feat in feature_names:

        # Here you decide the candidate grid for each feature.

        # For count features (0..something) you might use integers.

        # For continuous features you might use quantiles or a coarse grid.

        candidate_lows  = np.linspace(df_train[feat].min(), df_train[feat].max(), 20)

        candidate_highs = np.linspace(df_train[feat].min(), df_train[feat].max(), 20)

        best = find_best_band_for_feature(

            df_train, df_val, df_test,

            feature=feat,

            candidate_lows=candidate_lows,

            candidate_highs=candidate_highs,

            target_col=target_col,

        )

        if best is not None:

            rows.append(best)

    leaderboard = pd.DataFrame(rows)

    leaderboard = leaderboard.sort_values("L_train", ascending=False).reset_index(drop=True)

    return leaderboard


# ======================================================================
# Code: Greedy Joint Profile Search
# ======================================================================
def apply_band_mask(df: pd.DataFrame, feature: str, l: float, u: float) -> pd.Series:

    # Return a boolean mask for l <= feature <= u.

    return (df[feature] >= l) & (df[feature] <= u)

def greedy_joint_profile(df_train, df_val, df_test, best_bands_df, target_col="is_5hit"):

    # Starting from the sorted leaderboard (best_bands_df), add feature bands one by one

    # and track how the joint selectivity S_joint and joint lift L_joint evolve.

    #

    # Returns

    # -------

    # chosen : list[dict]

    #     A list of band dictionaries, enriched with S_joint and joint lifts.

    baseline_train = df_train[target_col].mean()

    baseline_val   = df_val[target_col].mean()

    baseline_test  = df_test[target_col].mean()

    # Start with masks that keep everything

    mask_tr = pd.Series(True, index=df_train.index)

    mask_va = pd.Series(True, index=df_val.index)

    mask_te = pd.Series(True, index=df_test.index)

    total_train = len(df_train)

    total_val   = len(df_val)

    total_test  = len(df_test)

    chosen = []

    for _, row in best_bands_df.iterrows():

        feat = row["feature"]

        l    = row["l"]

        u    = row["u"]

        # Update masks with the new band

        mask_tr &= apply_band_mask(df_train, feat, l, u)

        mask_va &= apply_band_mask(df_val,   feat, l, u)

        mask_te &= apply_band_mask(df_test,  feat, l, u)

        # Count survivors and hits in each split

        hn_tr = int(mask_tr.sum())

        hn_va = int(mask_va.sum())

        hn_te = int(mask_te.sum())

        hk_tr = int(df_train.loc[mask_tr, target_col].sum())

        hk_va = int(df_val.loc[mask_va,   target_col].sum())

        hk_te = int(df_test.loc[mask_te,  target_col].sum())

        # Joint selectivity (fraction of survivors)

        S_joint = hn_tr / total_train if total_train > 0 else 0.0

        # Joint lifts

        L_tr_joint = compute_lift(hk_tr, hn_tr, baseline_train)

        L_va_joint = compute_lift(hk_va, hn_va, baseline_val)

        L_te_joint = compute_lift(hk_te, hn_te, baseline_test)

        band_info = row.to_dict()

        band_info.update({

            "S_joint":       float(S_joint),

            "L_train_joint": float(L_tr_joint),

            "L_val_joint":   float(L_va_joint),

            "L_test_joint":  float(L_te_joint),

        })

        chosen.append(band_info)

        print(

            f"Trying {feat} → Joint S={S_joint:.4f} | "

            f"Lift(train)={L_tr_joint:.3f} | "

            f"Lift(val)={L_va_joint:.3f} | "

            f"Lift(test)={L_te_joint:.3f}"

        )

    return chosen


# ======================================================================
# Final Chosen Bands and the Playbook Dictionary
# ======================================================================
best_band_dict = {

    "k5":                [1, 36],

    "k4":                [1, 36],

    "k3":                [1, 36],

    "k2":                [1, 39],

    "E4":                [0, 0],

    "k1":                [1, 39],

    "combist4":          [0, 1222],

    "combist3":          [0, 1111],

    "cluster_mean_manh": [3.4, 6.8],

    "x8":                [0, 1],

    "bbox_perimeter":    [14, 26],

    "x_sum10":           [0, 5],

    "C2":                [0, 2],

    "p_3_row":           [0, 0],

    "st3":               [8, 41],

    "0s":                [8, 16],

    "x_sum":             [4, 15],

    "npr1":              [0, 3],

    "st1":               [1, 21],

    "Syn":               [0, 1],

    "npr2":              [0, 3],

    "NB1":               [0, 3],

    "D2":                [1, 21],

    "bbox_area":         [9, 36],

    "xD5":               [0, 2],

    "p_4_in_two_adj_rows": [0, 0],

    "2s":                [0, 3],

    "AC":                [4, 6],

    "Diffcombi":         [1031208, 27010108],

    # ... (and so on for all remaining features)

}
