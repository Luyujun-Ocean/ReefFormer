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
