"""
Code the Jackpot - 5.12 The "Remaining" Triads (3-number combinations)
Auto-extracted (book order). Full listings, nothing truncated.
"""


# ======================================================================
# 5.12.2 Updating the Remaining Pool After Each New Draw
# ======================================================================
import itertools

import pandas as pd

from pathlib import Path

TRIADS_FILE = Path("data/triads_remaining.csv")  # remaining (unseen) triads

def initialize_triads_universe(n=50):

    # One-time setup:

    # create the full universe of 3-number combinations from 1..n

    # and save them as remaining triads.

    all_triads = list(itertools.combinations(range(1, n + 1), 3))

    triads_df = pd.DataFrame(all_triads, columns=["no1", "no2", "no3"])

    triads_df.to_csv(TRIADS_FILE, index=False)

def load_remaining_triads():

    # Load the still-unseen triads as a Python set of tuples.

    # Each element is a triad like (5, 17, 29).

    df = pd.read_csv(TRIADS_FILE)

    return set(map(tuple, df.to_numpy()))

def save_remaining_triads(remaining_triads):

    # Save the updated remaining triads back to CSV.

    df = pd.DataFrame(sorted(remaining_triads), columns=["no1", "no2", "no3"])

    df.to_csv(TRIADS_FILE, index=False)

def update_triads_for_draw(draw_numbers, remaining_triads):

    # Given a 5-number draw and the current set of remaining triads,

    # return the number of new triads discovered in this draw,

    # and update remaining_triads in-place.

    #

    # draw_numbers     : list or iterable of 5 ints [st1..st5]

    # remaining_triads : set of triad tuples that are still unseen

    # All 3-number subsets in the draw

    triads_in_draw = set(itertools.combinations(sorted(draw_numbers), 3))

    # New triads = intersection of this draw's triads with the remaining set

    new_triads = triads_in_draw & remaining_triads

    # Remove them from the unseen pool

    remaining_triads -= new_triads

    # Return how many were discovered now

    return len(new_triads)


# ======================================================================
# 5.12.3 Recording the Feature in hist_df
# ======================================================================
def rebuild_triads_new_column(hist_df, st_cols=("st1", "st2", "st3", "st4", "st5")):

    # Recompute triads_new for the whole historical dataset.

    # hist_df must contain the main number columns st1..st5.

    df_st = hist_df[list(st_cols)].astype(int)

    # Reset remaining triads to the full universe

    initialize_triads_universe(n=50)

    remaining_triads = load_remaining_triads()

    triads_counts = []

    for _, row in df_st.iterrows():

        draw_numbers = row.to_list()

        cnt_new = update_triads_for_draw(draw_numbers, remaining_triads)

        triads_counts.append(cnt_new)

    # Save updated remaining triads

    save_remaining_triads(remaining_triads)

    hist_df["triads_new"] = triads_counts

    return hist_df

def update_triads_for_last_draw(hist_df, st_cols=("st1", "st2", "st3", "st4", "st5")):

    # After appending a new draw to hist_df, update triads_new for the last row

    # and update the remaining triads file.

    idx = len(hist_df) - 1

    draw_numbers = hist_df.loc[idx, list(st_cols)].astype(int).to_list()

    remaining_triads = load_remaining_triads()

    cnt_new = update_triads_for_draw(draw_numbers, remaining_triads)

    save_remaining_triads(remaining_triads)

    hist_df.loc[idx, "triads_new"] = cnt_new

    return hist_df


# ======================================================================
# 5.12.4 Counting Remaining Triads per Combination in total_df
# ======================================================================
import numpy as np

def count_unseen_triads(combo, remaining_triads):

    # combo: list of 5 ints (main numbers).

    # remaining_triads: set of unseen triad tuples.

    #

    # Returns: how many of this combo's 10 triads are still unseen.

    combo_triads = set(itertools.combinations(sorted(combo), 3))

    return len(combo_triads & remaining_triads)

def update_triads_unseen_total(total_df,

                               remaining_triads,

                               st_cols=("st1", "st2", "st3", "st4", "st5")):

    # Add or refresh the triads_unseen column on total_df.

    total_df["triads_unseen"] = [

        count_unseen_triads(

            row[list(st_cols)].astype(int).to_list(),

            remaining_triads

        )

        for _, row in total_df.iterrows()

    ]

    return total_df
