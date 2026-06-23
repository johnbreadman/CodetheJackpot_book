"""
Code the Jackpot - 5.10 Hot, Cold, Fast, and Slow Numbers – state labels on top of K(n)
Auto-extracted (book order). Full listings, nothing truncated.
"""


# ======================================================================
# 5.10.3 The numb3rs table
# ======================================================================

import numpy as np
import pandas as pd

def update_Numb3rs(df):
    """
    Build the per-number status table (numb3rs) for a 5/50 game.

    df: historical draws with columns at least:
        ['st1', 'st2', 'st3', 'st4', 'st5']

    Returns a DataFrame with columns:
        No, Freq, Delay, Norm, FS, HC, HCFS
    """
    # Structure per number: [No, Freq, Delay, Norm]
    hcfs = np.zeros((50, 4), dtype=float)
    hcfs[:, 0] = np.arange(1, 51)  # numbers 1..50

    # Walk through all draws in time order
    for _, row in df.iterrows():
        # Increase "Delay" for all numbers
        hcfs[:, 2] += 1

        # Update counts and reset Delay for drawn numbers
        drawn_numbers = row[['st1', 'st2', 'st3', 'st4', 'st5']].astype(int).values - 1
        hcfs[drawn_numbers, 1] += 1
        hcfs[drawn_numbers, 2] = 0

    total_draws = df.shape[0]

    # Norm is the average spacing between hits for each number
    norms = np.where(hcfs[:, 1] > 0, total_draws / hcfs[:, 1], 0)
    hcfs[:, 3] = norms

    numb3rs = pd.DataFrame(hcfs, columns=['No', 'Freq', 'Delay', 'Norm'])
    numb3rs[['No', 'Freq', 'Delay']] = numb3rs[['No', 'Freq', 'Delay']].astype(int)

    # Mean frequency across all numbers
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
# 5.10.4 Turning HCFS labels into numbers: N1–N5 and NB
# ======================================================================

def create_initial_runHCFS(df_hist):
    """
    For each historical draw i, label its five numbers with HCFS states
    computed from all previous draws, and create:

        N1..N5 : per-position HCFS codes (1..4)
        NB1..NB4 : counts of HF, HS, CF, CS in the line
        NB        : 4-digit synthetic code NB1 NB2 NB3 NB4

    df_hist must have at least st1..st5 and be sorted in time.
    """
    lottery_data = df_hist.copy()

    # Initialise N-columns with 4 ('CS') for the very early draws
    for col in ['N1', 'N2', 'N3', 'N4', 'N5']:
        lottery_data[col] = 4

    # Start from some index where other dynamic columns are already valid;
    # if you want everything, just start from i = 1
    start_idx = 1

    for i in range(start_idx, len(lottery_data)):
        # numb3rs as seen BEFORE draw i
        numbers_table = update_Numb3rs(lottery_data.head(i))

        for j in range(1, 6):
            n = int(lottery_data.at[i, f'st{j}'])
            hc_label = numbers_table.at[n - 1, 'HCFS']
            lottery_data.at[i, f'N{j}'] = hcfs_code(hc_label)

    # Now add NB1..NB4 and NB
    for i in range(len(lottery_data)):
        row_codes = lottery_data.loc[i, ['N1', 'N2', 'N3', 'N4', 'N5']].tolist()

        lottery_data.at[i, 'NB1'] = row_codes.count(1)  # HF
        lottery_data.at[i, 'NB2'] = row_codes.count(2)  # HS
        lottery_data.at[i, 'NB3'] = row_codes.count(3)  # CF
        lottery_data.at[i, 'NB4'] = row_codes.count(4)  # CS

    lottery_data['NB'] = (
        lottery_data['NB1'] * 1000 +
        lottery_data['NB2'] * 100 +
        lottery_data['NB3'] * 10 +
        lottery_data['NB4']
    )

    return lottery_data


# ======================================================================
# 5.10.5 Keeping the HCFS logbook up to date
# ======================================================================

# update Numb3rs history in hist_df 
nmb = pd.read_csv('data/historicalHCFS.csv', index_col=0)
numb3rs = pd.read_csv('data/Numb3rs.csv', index_col=0)

# 'last' = list of the 5 numbers of the latest draw
numbs_list = [hcfs_code(numb3rs.at[n-1, 'HCFS']) for n in last]

# append the new row to the HCFS history
nmb.loc[len(nmb)] = numbs_list
nmb.to_csv('data/historicalHCFS.csv')

# copy the updated N1..N5 into your main dataframe
df_cols[['N1', 'N2', 'N3', 'N4', 'N5']] = nmb[['N1', 'N2', 'N3', 'N4', 'N5']]

# recompute NB1..NB4 and NB for df_cols
df_cols['NB1'] = [df_cols.loc[i, 'N1':'N5'].tolist().count(1) for i in range(len(df_cols))]
df_cols['NB2'] = [df_cols.loc[i, 'N1':'N5'].tolist().count(2) for i in range(len(df_cols))]
df_cols['NB3'] = [df_cols.loc[i, 'N1':'N5'].tolist().count(3) for i in range(len(df_cols))]
df_cols['NB4'] = [df_cols.loc[i, 'N1':'N5'].tolist().count(4) for i in range(len(df_cols))]

df_cols['NB'] = sum(df_cols[f'NB{i}'] * 10**(4 - i) for i in range(1, 5))


# ======================================================================
# 5.10.6 From per-number labels to per-combination filters
# ======================================================================

def summarize_NB_patterns(df_hist):
    """
    Quick view of how often each NB pattern appears in the history.
    """
    counts = df_hist['NB'].value_counts().sort_values(ascending=False)
    total  = len(df_hist)

    summary = (
        counts
        .to_frame('hits')
        .assign(
            freq = lambda x: x['hits'] / total
        )
    )
    return summary

nb_summary = summarize_NB_patterns(hist_df_with_NB)print(nb_summary.head(10))
