# Reproducibility runbook

## Level 1: unit and synthetic checks

```bash
python scripts/run_demo.py
pytest
```

This validates the fusion equations, monotonic weights, parameter recovery,
shape checks, and checkpoint-compatible model loading.

## Level 2: archived checkpoint reproduction (GBR)

```bash
python scripts/reproduce_reference.py --domain gbr_coraltemp --device auto
```

For seeds 42, 43, and 44 the workflow:

1. verifies the dataset, checkpoint, and reference paths;
2. infers the 90-day and 365-day forecasts;
3. builds damped anomaly persistence from the training-period coefficients;
4. fits Lead-dependent Context Fusion (LCF) on Validation only;
5. fits Lead-dependent Persistence Fusion (LPF) on Validation only;
6. freezes both weight curves;
7. scores Validation, Development (2022--2025), and Test2026;
8. compares the generated summaries with the archived tables.

The Hainan domains (`hainan_coraltemp`, `hainan_ostia`) run with the same
command once the files distributed on request are in place (see
`docs/DATA.md`).

## Level 2b: warm-season evaluation (GBR)

```bash
python scripts/warm_season_gbr.py --device auto
```

The workflow covers every out-of-sample GBR warm season, 1 December to 15 April
from 2021/22 to 2025/26, truncated by the record (the 2021/22 and 2025/26
seasons start on 1 January, at the start of `Dev` and `Test2026`). It:

1. regenerates the three-seed mean ReefFormer and iTransformer (365-day)
   forecasts from the archived checkpoints, as in Level 2, and builds anomaly
   persistence from the data;
2. computes degree heating weeks (DHW) from HotSpots of at least 1 deg C above
   the maximum monthly mean of the 2000--2017 climatology, summed over 84 days
   and divided by seven, and the forecast-extended DHW that combines observed
   HotSpots up to each origin with forecast HotSpots thereafter;
3. computes per-origin statistics for RMSE over days 1--14 and 15--30, the DHW
   mean absolute error over leads 1--30, and the contingency counts of the
   4 deg C-week alert level, and checks the regenerated statistics against
   `reference_results/gbr_coraltemp/warm_season/WARM_SEASON_ORIGIN_STATS.csv`;
4. reads the archived per-origin statistics of DLinear, PatchTST, and the LSTM,
   whose forecasts are not part of this release;
5. pools the statistics into `TABLE_S32_GBR.csv` and computes the improvement of
   ReefFormer over each reference with a circular moving-block bootstrap over
   origins (15-day blocks, 1,000 replicates, fixed seeds) into
   `TABLE_S33_GBR.csv`;
6. compares both tables with the archived references and writes
   `outputs/gbr_coraltemp/warm_season/verification.json`.

Tolerances: relative difference `1e-5` for regenerated statistics, `1e-4` for
pooled metrics, `1e-2` for improvements and interval bounds (percent,
deg C-weeks, or CSI points), and identical significance flags.

## Level 3: model retraining

The archived runs used deterministic CUDA training with Adam, seeds 42--44,
batch size 32, at most 40 epochs, and patience 8. Retrain one component with:

```bash
python scripts/train_backbone.py --domain gbr_coraltemp --lookback 90 --seed 42 --device cuda
```

Repeat for lookbacks 90 and 365 and seeds 42--44. The trainer reads only
`Train` for gradient updates and only `Val` for checkpoint selection; `Dev` and
`Test2026` are never loaded. New checkpoints can differ in the last digits
across PyTorch, CUDA, and GPU versions; the archived checkpoints remain the
reference artifacts for exact table reproduction.

## Expected numerical tolerance

CPU and CUDA inference may differ in the last floating-point digits. The
verification step treats an absolute metric difference below `1e-4 deg C` as a
successful reproduction.
