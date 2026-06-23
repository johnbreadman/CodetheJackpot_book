"""
Code the Jackpot - 5.9 Spacing-Based Dynamic Ranking of D-Values
Auto-extracted (book order). Full listings, nothing truncated.
"""


# ======================================================================
# 5.9.2. Structural D-distribution in the full 5-of-50 space
# ======================================================================
from itertools import combinations
from collections import Counter

D_counts = Counter()
total_positions = 0

for a, b, c, d, e in combinations(range(1, 51), 5):
    d1 = b - a
    d2 = c - b
    d3 = d - c
    d4 = e - d
    D_counts[d1] += 1
    D_counts[d2] += 1
    D_counts[d3] += 1
    D_counts[d4] += 1
    total_positions += 4

struct_probs = {d: D_counts[d] / total_positions for d in sorted(D_counts)}
struct_series = pd.Series(struct_probs).sort_values(ascending=False)


# ======================================================================
# 5.9.4. Historical EuroJackpot dataset and D-construction
# ======================================================================
df = pd.read_csv('total_nikstiles.csv')
for i in range(1, 5):
    df[f'D{i}'] = df[f'st{i+1}'] - df[f'st{i}']


# ======================================================================
# 5.9.5. Spacing-based ranking of D-values
# ======================================================================
from scipy import stats

def spacing_scores_df(df, cols):
    uniq = pd.unique(df[cols].values.ravel('K'))
    rows = []
    for v in uniq:
        idx = df.index[df[cols].isin([v]).any(axis=1)].to_list()
        if not idx:
            continue
        diffs = [idx[0]] + [idx[i] - idx[i-1] for i in range(1, len(idx))] \
                + [len(df) - idx[-1]]
        if len(diffs) <= 1:
            continue
        delay = diffs[-1]
        pct = int(stats.percentileofscore(diffs, delay))
        rows.append(dict(value=int(v), co=len(diffs)-1,
                        delay=delay, Pct_score=pct))
    if not rows:
        return pd.DataFrame(columns=['value','co','delay','Pct_score','Norm','Prod'])
    res = pd.DataFrame(rows)
    res['Norm'] = (100 * res['co'] / res['co'].sum()).round(2)
    res['Prod'] = (res['Norm'] * res['Pct_score']).round(2)
    return res

def calc_percentiles_multi_cols(df, cols):
    res = spacing_scores_df(df, cols)
    if res.empty:
        return []
    return res.sort_values('Prod', ascending=False)['value'].astype(int)


# ======================================================================
# 5.9.6. Backtest design for top_n ∈ {13, 15, 17}
# ======================================================================
def run_D_backtest_multi_topn(
    df,
    cols=('D1','D2','D3','D4'),
    start_draw_index=100,
    top_n_list=(13,15,17)
):
    df = df.copy()
    for c in cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    results_by_topn = {n: [] for n in top_n_list}
    for t in range(start_draw_index, len(df)):
        hist = df.iloc[:t]
        ranking = calc_percentiles_multi_cols(hist, list(cols))
        ranking_values = list(ranking) if isinstance(ranking, pd.Series) else list(ranking)
        row = df.iloc[t]
        d_vals = [int(row[c]) for c in cols]
        unique_vals = sorted(set(d_vals))
        for top_n in top_n_list:
            top_values = ranking_values[:top_n]
            top_set = set(top_values)
            hits_unique = len(set(d_vals) & top_set)
            hits_with_dups = sum(1 for v in d_vals if v in top_set)
            all_in_top = all(v in top_set for v in d_vals)
            results_by_topn[top_n].append({
                'draw_index': t,
                'draw_no_1_based': t + 1,
                'Date': row.get('Date', None),
                cols[0]: d_vals[0], cols[1]: d_vals[1],
                cols[2]: d_vals[2], cols[3]: d_vals[3],
                'unique_D_values': tuple(unique_vals),
                'num_unique': len(unique_vals),
                'has_duplicates': len(unique_vals) < len(d_vals),
                'top_values': tuple(top_values),
                'top_n': top_n,
                'hits_unique': hits_unique,
                'hits_with_dups': hits_with_dups,
                'all_in_top': all_in_top,
            })
    return {n: pd.DataFrame(rows) for n, rows in results_by_topn.items()}
