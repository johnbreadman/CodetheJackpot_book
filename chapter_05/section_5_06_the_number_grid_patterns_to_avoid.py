"""
Code the Jackpot - 5.6 The Number Grid Patterns to Avoid
Auto-extracted (book order). Full listings, nothing truncated.
"""


# ======================================================================
# 5.6.1 From numbers to a 5×10 grid
# ======================================================================
def combo_to_coords_5x10(nums):

    """Map a 5-number combination to (row, col) on the 5×10 grid."""

    coords = []

    for n in nums:

        if not 1 <= n <= 50:

            raise ValueError(f"Number {n} out of range 1..50")

        n0 = n - 1

        r = n0 // 10   # row 0..4

        c = n0 % 10    # column 0..9

        coords.append((r, c))

    return coords


# ======================================================================
# 5.6.3 Python code to flag all patterns
# ======================================================================
from collections import Counter

from itertools import combinations, permutations

def compute_metrics(coords):

    """Bounding box area, perimeter and mean pairwise Manhattan distance."""

    rs = [r for r, c in coords]

    cs = [c for r, c in coords]

    min_r, max_r = min(rs), max(rs)

    min_c, max_c = min(cs), max(cs)

    bbox_area = (max_r - min_r + 1) * (max_c - min_c + 1)

    bbox_perim = 2 * ((max_r - min_r + 1) + (max_c - min_c + 1))

    dists = []

    for (r1, c1), (r2, c2) in combinations(coords, 2):

        dists.append(abs(r1 - r2) + abs(c1 - c2))

    mean_manh = sum(dists) / len(dists)

    return bbox_area, bbox_perim, mean_manh

def p_3_row(coords):

    cr = Counter(r for r, c in coords)

    return any(v >= 3 for v in cr.values())

def p_3_col(coords):

    cc = Counter(c for r, c in coords)

    return any(v >= 3 for v in cc.values())

def p_5_in_row(coords):

    cr = Counter(r for r, c in coords)

    return any(v >= 5 for v in cr.values())

def p_4_in_row(coords):

    cr = Counter(r for r, c in coords)

    return any(v >= 4 for v in cr.values())

def p_5_in_col(coords):

    cc = Counter(c for r, c in coords)

    return any(v >= 5 for v in cc.values())

def p_4_in_col(coords):

    cc = Counter(c for r, c in coords)

    return any(v >= 4 for v in cc.values())

def p_5_in_n_rows(coords, n):

    rows = {r for r, c in coords}

    return len(rows) == n

def p_5_in_n_cols(coords, n):

    cols = {c for r, c in coords}

    return len(cols) == n

def p_5_in_3_rows(coords): return p_5_in_n_rows(coords, 3)

def p_5_in_4_rows(coords): return p_5_in_n_rows(coords, 4)

def p_5_in_5_rows(coords): return p_5_in_n_rows(coords, 5)

def p_5_in_3_cols(coords): return p_5_in_n_cols(coords, 3)

def p_5_in_4_cols(coords): return p_5_in_n_cols(coords, 4)

def p_5_in_5_cols(coords): return p_5_in_n_cols(coords, 5)

def p_4_in_two_adj_rows(coords):

    cr = Counter(r for r, c in coords)

    rows = sorted(cr)

    for r in rows:

        if r + 1 in cr and cr[r] + cr[r + 1] >= 4:

            return True

    return False

def p_4_in_two_adj_cols(coords):

    cc = Counter(c for r, c in coords)

    cols = sorted(cc)

    for c in cols:

        if c + 1 in cc and cc[c] + cc[c + 1] >= 4:

            return True

    return False

def _border_count(coords, n_rows=5, n_cols=10):

    cnt = 0

    for r, c in coords:

        if r == 0 or r == n_rows - 1 or c == 0 or c == n_cols - 1:

            cnt += 1

    return cnt

def p_in_img_all5(coords):   return _border_count(coords) == 5

def p_in_img_exact4(coords): return _border_count(coords) == 4

def p_in_img_exact3(coords): return _border_count(coords) == 3

def p_border_heavy(coords):  return _border_count(coords) >= 4

def p_2plus2_cols(coords):

    cc = Counter(c for r, c in coords)

    if len(cc) == 3:

        vals = sorted(cc.values())

        return vals == [1, 2, 2]

    return False

def p_rectangle(coords):

    pts = set(coords)

    rows = sorted({r for r, c in coords})

    cols = sorted({c for r, c in coords})

    for i in range(len(rows)):

        for j in range(i + 1, len(rows)):

            r1, r2 = rows[i], rows[j]

            for a in range(len(cols)):

                for b in range(a + 1, len(cols)):

                    c1, c2 = cols[a], cols[b]

                    corners = {(r1, c1), (r1, c2), (r2, c1), (r2, c2)}

                    if corners.issubset(pts):

                        return True

    return False

def p_near_rectangle(coords):

    pts = set(coords)

    rows = sorted({r for r, c in coords})

    cols = sorted({c for r, c in coords})

    for i in range(len(rows)):

        for j in range(i + 1, len(rows)):

            r1, r2 = rows[i], rows[j]

            for a in range(len(cols)):

                for b in range(a + 1, len(cols)):

                    c1, c2 = cols[a], cols[b]

                    corners = {(r1, c1), (r1, c2), (r2, c1), (r2, c2)}

                    count = sum(1 for p in corners if p in pts)

                    if count == 3:

                        return True

    return False

def p_L_shape(coords):

    pts = set(coords)

    for r, c in coords:

        if ((r + 1, c) in pts and (r, c + 1) in pts): return True

        if ((r + 1, c) in pts and (r, c - 1) in pts): return True

        if ((r - 1, c) in pts and (r, c + 1) in pts): return True

        if ((r - 1, c) in pts and (r, c - 1) in pts): return True

    return False

def p_cluster(coords):

    pts = set(coords)

    for r0 in range(5 - 3 + 1):

        for c0 in range(10 - 3 + 1):

            cnt = sum(

                1

                for (r, c) in pts

                if r0 <= r <= r0 + 2 and c0 <= c <= c0 + 2

            )

            if cnt >= 4:

                return True

    return False

def p_checkerboard_4plus(coords):

    colors = [(r + c) % 2 for r, c in coords]

    return colors.count(0) >= 4 or colors.count(1) >= 4

def p_3_diag(coords):

    pts = set(coords)

    for a, b, c in combinations(pts, 3):

        (r1, c1), (r2, c2), (r3, c3) = a, b, c

        if (r1 - c1) == (r2 - c2) == (r3 - c3): return True

        if (r1 + c1) == (r2 + c2) == (r3 + c3): return True

    return False

def p_staircase_horizontal(coords):

    pts = set(coords)

    coords_list = list(pts)

    for subset in combinations(coords_list, 4):

        for seq in permutations(subset):

            moves = []

            ok = True

            for (r1, c1), (r2, c2) in zip(seq, seq[1:]):

                dr, dc = r2 - r1, c2 - c1

                if not ((dr == 0 and abs(dc) == 1) or (dc == 0 and abs(dr) == 1)):

                    ok = False

                    break

                moves.append((dr, dc))

            if not ok:

                continue

            hor = sum(1 for dr, dc in moves if dr == 0)

            ver = sum(1 for dr, dc in moves if dc == 0)

            if hor >= 1 and ver >= 1 and hor >= ver:

                return True

    return False

def p_staircase_vertical(coords):

    pts = set(coords)

    coords_list = list(pts)

    for subset in combinations(coords_list, 4):

        for seq in permutations(subset):

            moves = []

            ok = True

            for (r1, c1), (r2, c2) in zip(seq, seq[1:]):

                dr, dc = r2 - r1, c2 - c1

                if not ((dr == 0 and abs(dc) == 1) or (dc == 0 and abs(dr) == 1)):

                    ok = False

                    break

                moves.append((dr, dc))

            if not ok:

                continue

            hor = sum(1 for dr, dc in moves if dr == 0)

            ver = sum(1 for dr, dc in moves if dc == 0)

            if hor >= 1 and ver >= 1 and ver >= hor:

                return True

    return False

def p_zigzag_horizontal(coords):

    pts = set(coords)

    coords_list = list(pts)

    for subset in combinations(coords_list, 4):

        for seq in permutations(subset):

            cols = [c for r, c in seq]

            diffs = [cols[i + 1] - cols[i] for i in range(3)]

            if all(abs(d) == 1 for d in diffs):

                if diffs[0] * diffs[1] < 0 and diffs[1] * diffs[2] < 0:

                    return True

    return False

def p_zigzag_vertical(coords):

    pts = set(coords)

    coords_list = list(pts)

    for subset in combinations(coords_list, 4):

        for seq in permutations(subset):

            rows = [r for r, c in seq]

            diffs = [rows[i + 1] - rows[i] for i in range(3)]

            if all(abs(d) == 1 for d in diffs):

                if diffs[0] * diffs[1] < 0 and diffs[1] * diffs[2] < 0:

                    return True

    return False

def compute_pattern_flags_5x10(nums, bbox_area_thresh=None, bbox_perim_thresh=None):

    """Compute all pattern flags and compactness metrics for one combination."""

    coords = combo_to_coords_5x10(nums)

    bbox_area, bbox_perim, mean_manh = compute_metrics(coords)

    flags = {

        "p_2plus2_cols": p_2plus2_cols(coords),

        "p_3_diag": p_3_diag(coords),

        "p_3_row": p_3_row(coords),

        "p_3_col": p_3_col(coords),

        "p_cluster": p_cluster(coords),

        "p_L_shape": p_L_shape(coords),

        "p_staircase_horizontal": p_staircase_horizontal(coords),

        "p_staircase_vertical": p_staircase_vertical(coords),

        "p_zigzag_horizontal": p_zigzag_horizontal(coords),

        "p_zigzag_vertical": p_zigzag_vertical(coords),

        "p_rectangle": p_rectangle(coords),

        "p_near_rectangle": p_near_rectangle(coords),

        "p_in_img_all5": p_in_img_all5(coords),

        "p_in_img_exact4": p_in_img_exact4(coords),

        "p_in_img_exact3": p_in_img_exact3(coords),

        "p_5_in_3_cols": p_5_in_3_cols(coords),

        "p_5_in_4_cols": p_5_in_4_cols(coords),

        "p_5_in_5_cols": p_5_in_5_cols(coords),

        "p_5_in_3_rows": p_5_in_3_rows(coords),

        "p_5_in_4_rows": p_5_in_4_rows(coords),

        "p_5_in_5_rows": p_5_in_5_rows(coords),

        "p_5_in_row": p_5_in_row(coords),

        "p_4_in_row": p_4_in_row(coords),

        "p_5_in_col": p_5_in_col(coords),

        "p_4_in_col": p_4_in_col(coords),

        "p_4_in_two_adj_rows": p_4_in_two_adj_rows(coords),

        "p_4_in_two_adj_cols": p_4_in_two_adj_cols(coords),

        "p_border_heavy": p_border_heavy(coords),

        "p_checkerboard_4plus": p_checkerboard_4plus(coords),

        "cluster_mean_manhattan_distance": mean_manh,

        "bbox_area": bbox_area,

        "bbox_perimeter": bbox_perim,

    }

    flags["p_small_bbox_area"] = (

        bbox_area_thresh is not None and bbox_area <= bbox_area_thresh

    )

    flags["p_small_bbox_perim"] = (

        bbox_perim_thresh is not None and bbox_perim <= bbox_perim_thresh

    )

    return flags

# Example:

# combo = [13, 14, 15, 16, 17]

# print(compute_pattern_flags_5x10(combo))


# ======================================================================
# 5.6.4 Measuring how often each pattern appears
# ======================================================================
PATTERN_COLS = [

    "p_2plus2_cols", "p_3_diag", "p_3_row", "p_3_col", "p_cluster", "p_L_shape",

    "p_staircase_horizontal", "p_staircase_vertical", "p_zigzag_horizontal",

    "p_zigzag_vertical", "p_rectangle", "p_near_rectangle", "p_in_img_all5",

    "p_in_img_exact4", "p_in_img_exact3", "p_5_in_3_cols", "p_5_in_4_cols",

    "p_5_in_5_cols", "p_5_in_3_rows", "p_5_in_4_rows", "p_5_in_5_rows",

    "p_5_in_row", "p_4_in_row", "p_5_in_col", "p_4_in_col",

    "p_4_in_two_adj_rows", "p_4_in_two_adj_cols", "p_border_heavy",

    "p_checkerboard_4plus", "p_small_bbox_area", "p_small_bbox_perim",

]

METRIC_COLS = ["cluster_mean_manhattan_distance", "bbox_area", "bbox_perimeter"]

def add_pattern_flags_to_df(df, st_cols=("st1", "st2", "st3", "st4", "st5")):

    def _row_flags(row):

        nums = [int(row[c]) for c in st_cols]

        return compute_pattern_flags_5x10(nums)

    flags_df = df.apply(_row_flags, axis=1, result_type="expand")

    return pd.concat([df.reset_index(drop=True), flags_df], axis=1)

def add_small_bbox_flags(

    total_flags_df,

    hist_flags_df,

    area_quantile=0.10,

    perim_quantile=0.10,

):

    area_thr  = total_flags_df["bbox_area"].quantile(area_quantile)

    perim_thr = total_flags_df["bbox_perimeter"].quantile(perim_quantile)

    total_flags_df = total_flags_df.copy()

    hist_flags_df  = hist_flags_df.copy()

    total_flags_df["p_small_bbox_area"]  = total_flags_df["bbox_area"] <= area_thr

    total_flags_df["p_small_bbox_perim"] = total_flags_df["bbox_perimeter"] <= perim_thr

    hist_flags_df["p_small_bbox_area"]  = hist_flags_df["bbox_area"] <= area_thr

    hist_flags_df["p_small_bbox_perim"] = hist_flags_df["bbox_perimeter"] <= perim_thr

    thresholds = {

        "bbox_area_thr": float(area_thr),

        "bbox_perim_thr": float(perim_thr),

    }

    return total_flags_df, hist_flags_df, thresholds

def build_pattern_lift_table(hist_flags_df, total_flags_df, pattern_cols=PATTERN_COLS):

    n_hist  = len(hist_flags_df)

    n_total = len(total_flags_df)

    rows = []

    for col in pattern_cols:

        if col not in hist_flags_df.columns or col not in total_flags_df.columns:

            continue

        total_count = int(total_flags_df[col].sum())

        hist_count  = int(hist_flags_df[col].sum())

        total_share = total_count / n_total if n_total > 0 else float("nan")

        hist_share  = hist_count  / n_hist  if n_hist  > 0 else float("nan")

        lift = hist_share / total_share if total_share > 0 else float("nan")

        rows.append({

            "pattern": col,

            "total_count": total_count,

            "total_share": total_share,

            "hist_count": hist_count,

            "hist_share": hist_share,

            "lift": lift,

        })

    pat_df = pd.DataFrame(rows)

    return pat_df.sort_values("lift", ascending=False).reset_index(drop=True)

# Usage outline:

# total_flags_df = add_pattern_flags_to_df(total_df)

# hist_flags_df  = add_pattern_flags_to_df(hist_df)

# total_flags_df, hist_flags_df, thresholds = add_small_bbox_flags(total_flags_df, hist_flags_df)

# pattern_stats = build_pattern_lift_table(hist_flags_df, total_flags_df)


# ======================================================================
# 5.6.5 Choosing geometric shapes to avoid
# ======================================================================
FORBIDDEN_PATTERNS = [

    "p_5_in_row",

    "p_5_in_col",

    "p_4_in_col",

    "p_staircase_vertical",

    "p_zigzag_horizontal",

    "p_4_in_row",

    "p_4_in_two_adj_cols",

]

def add_geom_forbidden_flag(df):

    df = df.copy()

    df["geom_forbidden"] = df[FORBIDDEN_PATTERNS].any(axis=1)

    return df

total_flags_df = add_geom_forbidden_flag(total_flags_df)

share_forbidden = total_flags_df["geom_forbidden"].mean()

print("Share of combinations removed due to geometric filters:", share_forbidden)
