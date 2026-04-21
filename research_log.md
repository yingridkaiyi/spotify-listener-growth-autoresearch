# Research Log

## 2026-04-21 - Local Runtime Assessment

- Goal: verify that the repository can be run locally from a fresh copy and record the Week 2 runtime assessment.
- Environment: local test run with `Python 3.13.3`.
- Setup command:
  `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
- Run command:
  `python3 src/run.py`
- Result:
  the baseline run completed successfully and regenerated `evaluation_board.md`, `experiments/experiment_log.tsv`, and `experiments/best_model_artifact.pkl`.
- Runtime assessment:
  wall-clock time `11.75s`, user CPU `10.26s`, system CPU `0.44s`.
- Notes:
  the processed dataset is already included in the repository, so the TA does not need to download external source data to reproduce the baseline run.
