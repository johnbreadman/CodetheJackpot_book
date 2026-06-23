"""
Code the Jackpot - 5.8 Arithmetic Complexity of a Combination
Auto-extracted (book order). Full listings, nothing truncated.
"""


# ======================================================================
# Computing AC in code (and adding it to hist_df and total_df)
# ======================================================================
    def arithmetic_complexity_five(st1, st2, st3, st4, st5):
        """
        Compute Arithmetic Complexity (AC) for one 5-number combination.

        AC = number of distinct pairwise differences between the 5 sorted numbers.
        """
        nums = sorted([int(st1), int(st2), int(st3), int(st4), int(st5)])
        diffs = set()

        for i in range(5):
            for j in range(i + 1, 5):
                diffs.add(nums[j] - nums[i])

        return len(diffs)

    import pandas as pd

    def add_AC_column(df, cols=('st1', 'st2', 'st3', 'st4', 'st5'), new_col='AC'):
        """
        Return a copy of df with an extra column `new_col` holding
        the arithmetic complexity for each 5-number row.
        """
        df = df.copy()
        df[new_col] = df.loc[:, cols].apply(
            lambda row: arithmetic_complexity_five(*row.values),
            axis=1
        )
        return df

    hist_df = add_AC_column(hist_df)
    total_df = add_AC_column(total_df)
