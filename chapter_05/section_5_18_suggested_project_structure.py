"""
Code the Jackpot - 5.18 From Book to Software Lab (Building the Lab Framework)

Section 5.18 is a descriptive chapter (no runnable Python listings). The one
structured listing is the suggested Git project layout, reproduced below as
reference. NOTE: this illustrative package layout ('eurojackpotpylab/') differs
from the actual live repository (the FastAPI app in this repo).
"""

SUGGESTED_PROJECT_STRUCTURE = r'''
A concrete folder layout helps keep the different pieces in order. The following tree is one possible structure for a Git repository that houses the project:

eurojackpotpylab/
  README.md
  LICENSE
  pyproject.toml        # packaging and dependencies
  .gitignore
  data/                 # small example datasets for the repository
    sample_historical_draws.csv
    sample_total_nikstiles.csv
  src/
    eurojackpotpylab/
      __init__.py
      dataio/
        scrape.py
        paths.py
        io_helpers.py
      features/
        inherent.py
        time_based_numbers.py
        time_based_combinations.py
        euronumbers.py
        markov.py
      filters/
        bands.py
        playbook.py
      backtest/
        hit_counts.py
        reports.py
      cli_core.py
  scripts/
    init_all.py
    update_after_new_draw.py
    rebuild_total_space_features.py
    run_playbook.py
    export_pools.py
  notebooks/
    4_4_inherent_features.ipynb
    5_2_covering_sets_backtest.ipynb
    5_3_gap_analysis.ipynb
    5_7_E4_ED4_XD.ipynb
    5_10_HCFS.ipynb
    5_11_delay_engine.ipynb
    5_12_remaining_triads.ipynb
    5_13_markov_prediction.ipynb
    5_17_playbook_framework.ipynb
    5_18_software_lab_demo.ipynb
  docs/
    api_reference.md
    book_snippets/

In the public repository only small example datasets need to be included under `data/`. These are just enough for readers to run the notebooks and confirm that the code behaves as described. Full histories and heavy combination tables can be downloaded separately from the project website or built locally by the framework itself.

This structure keeps the code related to the book in one place, presents clear entry points for frequent tasks, and leaves room for documentation and reproducible examples.
'''
