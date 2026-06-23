"""
Code the Jackpot - 5.7 The Count of Hits with Every Draw – E4, ED4 and XD
Auto-extracted (book order). Full listings, nothing truncated.
"""


# ======================================================================
# 5.7.2 Updating E0…E5 in hist_df for Each New Draw
# ======================================================================
def co_common(st1, st2):
    return len(set(st1).intersection(set(st2)))

def count_common_values(df, new_row):
    counts = [0] * 6
    last_row = new_row.loc[0, :].tolist()
    for i in range(len(df)):
        row = df.iloc[i].tolist()
        common = co_common(last_row, row)
        counts[common] += 1
    return counts

def count_common_values_n(df, new_row):
    counts = [0] * 3
    last_row = new_row.loc[0, :].tolist()
    for i in range(len(df)):
        row = df.iloc[i].tolist()
        common = co_common(last_row, row)
        counts[common] += 1
    return counts

# Add the hit-count columns and initialise them
new_row_df[['E0', 'E1', 'E2', 'E3', 'E4', 'E5', 'En0', 'En1', 'En2']] = 0

# Main-number overlaps with all previous draws
new_row_df[['E0', 'E1', 'E2', 'E3', 'E4', 'E5']] = count_common_values(
    df[['st1', 'st2', 'st3', 'st4', 'st5']],
    new_row_df[['st1', 'st2', 'st3', 'st4', 'st5']]
)

# Euro-number overlaps with all previous draws
new_row_df[['En0', 'En1', 'En2']] = count_common_values_n(
    df[['n1', 'n2']],
    new_row_df[['n1', 'n2']]
)

# Append the new row to the historical dataset
hist_df = pd.concat([hist_df, new_row_df], ignore_index=True)


# ======================================================================
# 5.7.3 ED0…ED4 – How Often Do D-Patterns Overlap?
# ======================================================================
import os
import pandas as pd

HIST_PATH = "data/total_nikstiles.csv"
ED_PATH = "data/ED.csv"


def build_initial_ED(hist_df: pd.DataFrame, ed_path: str = ED_PATH) -> pd.DataFrame:
    """
    Create ED.csv from scratch.

    For each draw i, EDk counts how many previous draws (j < i) share
    exactly k common D-values (k in {0,1,2,3,4}) with draw i.
    """
    D_cols = ["D1", "D2", "D3", "D4"]
    records = []

    for i in range(len(hist_df)):
        current_Ds = hist_df.loc[hist_df.index[i], D_cols].astype(int).tolist()
        current_set = set(current_Ds)
        counts = [0] * 5  # ED0..ED4

        # compare only with earlier draws
        for j in range(i):
            prev_Ds = hist_df.loc[hist_df.index[j], D_cols].astype(int).tolist()
            prev_set = set(prev_Ds)
            common = len(current_set.intersection(prev_set))  # 0..4
            counts[common] += 1

        row = {
            "D1": current_Ds[0],
            "D2": current_Ds[1],
            "D3": current_Ds[2],
            "D4": current_Ds[3],
            "ED0": counts[0],
            "ED1": counts[1],
            "ED2": counts[2],
            "ED3": counts[3],
            "ED4": counts[4],
        }
        records.append(row)

        if (i + 1) % 200 == 0:
            print(f"Processed {i+1} / {len(hist_df)} draws for ED.csv")

    ed_df = pd.DataFrame(
        records,
        columns=["D1", "D2", "D3", "ED0", "ED1", "ED2", "ED3", "ED4"]
    )
    ed_df = ed_df.astype(int)

    os.makedirs(os.path.dirname(ed_path), exist_ok=True)
    ed_df.to_csv(ed_path)
    print(f"Saved ED.csv with {len(ed_df)} rows to {ed_path}")

    return ed_df


if __name__ == "__main__":
    hist_df = pd.read_csv(HIST_PATH, index_col=0)
    print(f"Loaded history from {HIST_PATH} with {len(hist_df)} rows")

    build_initial_ED(hist_df, ED_PATH)


# ======================================================================
# 5.7.4 E0…E5, ED0…ED4, and XD on total_df – The Full Hit Logbook
# ======================================================================
import pandas as pd
from multiprocessing import Pool, cpu_count
from datetime import datetime


def process_chunk_numbers_and_diff(chunk, b_set, diaf):
    """
    For one chunk of total_df, update:
      - E0..E5 based on intersection with the last draw's main numbers.
      - XD based on Diffcombi equality with the last draw's Diffcombi.
    """
    # Number of common main numbers with the last draw
    chunk['intersection_count"] = chunk.apply(
        lambda row: len(b_set.intersection(
            set(row[['st1', 'st2', 'st3', 'st4', 'st5']])
        )),
        axis=1
    )

    # Update 'E' columns based on 'intersection_count' values
    for i in range(6):
        mask = chunk['intersection_count'] == i
        chunk.loc[mask, f'E{i}'] += 1

    # Update 'XD' based on 'Diffcombi' matching 'diaf'
    chunk['XD'] += chunk['Diffcombi'].eq(diaf).astype(int)

    # Drop helper column if you prefer to keep total_df clean
    chunk.drop(columns=['intersection_count'], inplace=True)

    return chunk


def process_chunk_Ds(chunk, d_set):
    """
    For one chunk of total_df, update ED0..ED4 based on how many
    D1..D4 values it shares with the last draw.
    """
    # set of D-values for each row
    chunk['D_intersection'] = chunk.apply(
        lambda row: len(d_set.intersection(
            set(row[['D1', 'D2', 'D3', 'D4']])
        )),
        axis=1
    )

    for i in range(5):
        mask = chunk['D_intersection'] == i
        chunk.loc[mask, f'ED{i}'] += 1

    chunk.drop(columns=['D_intersection'], inplace=True)
    return chunk


def apply_multiprocessing(df, func, n_processes=None, **kwargs):
    """
    Generic helper that:
      - splits df into `n_processes` chunks,
      - runs `func(chunk, **kwargs)` in parallel,
      - concatenates the processed chunks.
    """
    if n_processes is None:
        n_processes = int(0.7 * cpu_count())  # leave some cores free

    chunk_size = len(df) // n_processes or len(df)
    chunks = [df.iloc[i:i + chunk_size]
              for i in range(0, len(df), chunk_size)]

    with Pool(n_processes) as pool:
        processed = pool.starmap(
            func,
            [(chunk, *kwargs.values()) for chunk in chunks]
        )

    return pd.concat(processed, ignore_index=True)

if __name__ == "__main__":
    df = pd.read_csv('data/totalcombinations.csv', index_col=0)
    df_n = pd.read_csv('data/total_nikstiles.csv', index_col=0)
    ed_df = pd.read_csv('data/ED.csv', index_col=0)

    # Last draw's main numbers and difference pattern
    st = sorted(list(df_n.iloc[-1, 1:6]))
    b_set = set(st)

    # Synthetic Diffcombi for the last draw (same formula as in Chapter 4.4)
    diaf = (
        1000000 * (st[1] - st[0]) +
        10000   * (st[2] - st[1]) +
        100     * (st[3] - st[2]) +
                  (st[4] - st[3])
    )

    # Last draw's D-values for ED updates
    last_Ds = ed_df.iloc[-1, :4].astype(int).tolist()
    d_set = set(last_Ds)

    print("Last draw:", st, "Diffcombi:", diaf, "D-set:", d_set)

    t0 = datetime.now()

    # Work only on needed columns to keep memory usage reasonable
    df_subset = df[[
        'st1', 'st2', 'st3', 'st4', 'st5',
        'D1', 'D2', 'D3', 'D4',
        'E0', 'E1', 'E2', 'E3', 'E4', 'E5',
        'ED0', 'ED1', 'ED2', 'ED3', 'ED4',
        'Diffcombi', 'XD'
    ]].copy()

    # First pass: main-number hits and XD
    df_subset = apply_multiprocessing(
        df_subset,
        process_chunk_numbers_and_diff,
        b_set=b_set,
        diaf=diaf
    )

    # Second pass: D-based overlaps for ED0..ED4
    df_subset = apply_multiprocessing(
        df_subset,
        process_chunk_Ds,
        d_set=d_set
    )

    # Write updated E, ED, XD back to the full total_df
    cols_to_update = [
        'E0', 'E1', 'E2', 'E3', 'E4', 'E5',
        'ED0', 'ED1', 'ED2', 'ED3', 'ED4',
        'XD'
    ]

    for col in cols_to_update:
        df[col] = df_subset[col]

    elapsed = datetime.now() - t0

    print("E/ED/XD update time:", elapsed)
    print("Combinations with E4 > 0:", len(df[df['E4'] > 0]))

    df.to_csv('data/totalcombinations.csv')


# ======================================================================
# 5.7.5 Reading the Hit Logbook – What E4 and ED4 Tell You
# ======================================================================
# Basic summary of the E4 distribution in total_df
total_lines = len(df)
e4_counts = df['E4'].value_counts().sort_index()

print("Total lines:", total_lines)
for k, cnt in e4_counts.items():
    share = cnt / total_lines
    print(f"E4 == {k}: {cnt} lines ({share:.5f} of space)")
