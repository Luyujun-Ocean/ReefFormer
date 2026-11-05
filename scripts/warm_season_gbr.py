"""Reproduce the GBR rows of the warm-season evaluation (Tables S32-S33 of the manuscript).

Five out-of-sample warm seasons on the central GBR (1 December-15 April, 2021/22-2025/26) are scored with
four metrics: RMSE over days 1-14 and 15-30, the mean absolute error of the forecast-extended degree heating
weeks (DHW) over leads 1-30, and the critical success index (CSI) of the 4 degC-week alert level.

ReefFormer, iTransformer (iT365) and anomaly persistence are regenerated here from the released checkpoints
and data, and their per-origin statistics are checked against the archive. DLinear, PatchTST and the LSTM are
not part of this release; their per-origin statistics are read from
reference_results/gbr_coraltemp/warm_season/WARM_SEASON_ORIGIN_STATS.csv.

Usage: python scripts/warm_season_gbr.py [--device auto|cpu|cuda]
"""

from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd

from reproduce_reference import (
    DOMAINS,
    HORIZON,
    ROOT,
    SEEDS,
    choose_device,
    infer,
    persistence,
    truth,
)
from reefformer import apply_reef_former, fit_reef_former

LEADS = np.arange(1, HORIZON + 1)
REFERENCE = ROOT / "reference_results/gbr_coraltemp/warm_season"
MODELS = ["ReefFormer", "LSTM", "iTransformer", "PatchTST", "DLinear", "Persistence"]
REGENERATED = ["ReefFormer", "iTransformer", "Persistence"]
REFS = MODELS[1:]
STAT_COLS = ["sse_d1_14", "n_d1_14", "sse_d15_30", "n_d15_30", "abs_dhw_err", "n_dhw",
             "hits_dhw4", "misses_dhw4", "false_alarms_dhw4"]
METRICS = ["rmse_d1_14", "rmse_d15_30", "dhw_mae", "csi_dhw4"]
# (name, split, window start, window end, bootstrap seed offset as used in the manuscript)
SEASONS = [("GBR 2021/22", "Dev", "2021-12-01", "2022-04-15", 5),
           ("GBR 2022/23", "Dev", "2022-12-01", "2023-04-15", 6),
           ("GBR 2023/24", "Dev", "2023-12-01", "2024-04-15", 7),
           ("GBR 2024/25", "Dev", "2024-12-01", "2025-04-15", 8),
           ("GBR 2025/26", "Test2026", "2025-12-01", "2026-04-15", 9)]
BLOCK, REPS, BASE_SEED = 15, 1000, 20261105
MONTH_OF_BIN = pd.date_range("2001-01-01", "2001-12-31").month.to_numpy()


def load(config: dict) -> dict:
    with np.load(config["data"], allow_pickle=False) as z:
        return {"ssta": z["ssta_c"].astype(np.float32), "sst": z["sst_c"].astype(np.float64),
                "clim365": z["climatology365_c"].astype(np.float64), "scale": float(z["ssta_scale"]),
                "rho": z["dap_rho_train"].astype(np.float64), "dates": pd.DatetimeIndex(z["dates"]),
                "ids": {s: z[s].astype(np.int64) for s in ("Val", "Dev", "Test2026")}}


def forecasts(data: dict, split: str, device: str, batch: int) -> dict:
    """Three-seed mean forecasts (anomalies) for the regenerated models."""
    cfg = DOMAINS["gbr_coraltemp"]
    reef, it365 = [], []
    for seed in SEEDS:
        p = {(lb, s): infer(data, cfg["checkpoints"] / f"iT_L{lb}_seed{seed}.pt", s, device, batch)
             for lb in (90, 365) for s in ("Val", split)}
        params = fit_reef_former(p[(90, "Val")], p[(365, "Val")], persistence(data, "Val"), truth(data, "Val"))
        reef.append(apply_reef_former(p[(90, split)], p[(365, split)], persistence(data, split), params))
        it365.append(p[(365, split)])
    ids = data["ids"][split]
    return {"ReefFormer": np.mean(np.stack(reef), 0).astype(np.float64),
            "iTransformer": np.mean(np.stack(it365), 0).astype(np.float64),
            "Persistence": np.repeat(data["ssta"][ids, None, :].astype(np.float64), HORIZON, axis=1)}


def season_stats(data: dict, split: str, preds: dict, ws: str, we: str) -> tuple[dict, pd.DatetimeIndex]:
    sst, ssta = data["sst"], data["ssta"].astype(np.float64)
    ids = data["ids"][split]
    mmm = np.max([data["clim365"][MONTH_OF_BIN == m].mean(0) for m in range(1, 13)], axis=0)
    clim = sst - ssta
    hs = np.where(sst - mmm >= 1.0, sst - mmm, 0.0)
    cs = np.vstack([np.zeros((1, sst.shape[1])), np.cumsum(hs, 0)])
    dhw_obs = np.full_like(sst, np.nan)
    dhw_obs[83:] = (cs[84:] - cs[:-84]) / 7.0
    tidx = ids[:, None] + LEADS[None, :]
    tdates = data["dates"].values[tidx]
    win = (tdates >= np.datetime64(ws)) & (tdates <= np.datetime64(we))
    keep = win.any(1)
    target = ssta[tidx]
    dobs = dhw_obs[tidx]
    n_cells = target.shape[-1]
    out = {}
    for name, p in preds.items():
        hs_f = np.where(clim[tidx] + p - mmm >= 1.0, clim[tidx] + p - mmm, 0.0)
        hs_cum = np.cumsum(hs_f, axis=1)
        fd = np.empty_like(p)
        for k, h in enumerate(LEADS):
            fd[:, k] = (cs[ids + 1] - cs[np.maximum(ids + h - 83, 0)] + hs_cum[:, k]) / 7.0
        e2 = ((p - target) ** 2).sum(-1)
        r1 = win & (LEADS[None, :] <= 14)
        r2 = win & (LEADS[None, :] >= 15)
        o, f, w3 = dobs >= 4, fd >= 4, win[:, :, None]
        out[name] = np.stack([(e2 * r1).sum(1), r1.sum(1) * n_cells, (e2 * r2).sum(1), r2.sum(1) * n_cells,
                              (np.abs(fd - dobs).sum(-1) * win).sum(1), win.sum(1) * n_cells,
                              (f & o & w3).sum((1, 2)), (~f & o & w3).sum((1, 2)), (f & ~o & w3).sum((1, 2))],
                             1)[keep]
    return out, pd.DatetimeIndex(data["dates"].values[ids[keep]])


def scores(s: np.ndarray) -> np.ndarray:
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.stack([np.sqrt(s[..., 0] / s[..., 1]), np.sqrt(s[..., 2] / s[..., 3]), s[..., 4] / s[..., 5],
                         s[..., 6] / (s[..., 6] + s[..., 7] + s[..., 8])], -1)


def improvement(rf: np.ndarray, ref: np.ndarray) -> np.ndarray:
    out = 100 * (ref - rf) / ref
    out[..., 2] = ref[..., 2] - rf[..., 2]
    out[..., 3] = 100 * (rf[..., 3] - ref[..., 3])
    return out


def block_weights(n: int, rng: np.random.Generator) -> np.ndarray:
    nb = int(np.ceil(n / BLOCK))
    w = np.zeros((REPS, n))
    starts = rng.integers(0, n, size=(REPS, nb))
    for b in range(BLOCK):
        np.add.at(w, (np.repeat(np.arange(REPS), nb), ((starts + b) % n).ravel()), 1)
    return w * (n / w.sum(1, keepdims=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()
    device = choose_device(args.device)
    data = load(DOMAINS["gbr_coraltemp"])
    archive = pd.read_csv(REFERENCE / "WARM_SEASON_ORIGIN_STATS.csv")
    out_dir = ROOT / "outputs/gbr_coraltemp/warm_season"
    out_dir.mkdir(parents=True, exist_ok=True)

    cached, totals, rows, regen_check = {}, {m: 0.0 for m in MODELS}, [], []
    for name, split, ws, we, k in SEASONS:
        if split not in cached:
            cached[split] = forecasts(data, split, device, args.batch_size)
        regen, dates = season_stats(data, split, cached[split], ws, we)
        st = {}
        for m in MODELS:
            arc = archive[(archive.season == name) & (archive.model == m)]
            if list(arc.origin_date) != list(dates.strftime("%Y-%m-%d")):
                raise SystemExit(f"Origin mismatch for {name} {m}")
            arc_vals = arc[STAT_COLS].to_numpy(np.float64)
            if m in REGENERATED:
                rel = np.max(np.abs(regen[m] - arc_vals) / np.maximum(np.abs(arc_vals), 1.0))
                regen_check.append({"season": name, "model": m, "max_relative_difference": float(rel)})
                st[m] = regen[m]
            else:
                st[m] = arc_vals
            totals[m] = totals[m] + st[m].sum(0)
        weights = block_weights(len(st["ReefFormer"]), np.random.default_rng(BASE_SEED + k))
        rf_point, rf_boot = scores(st["ReefFormer"].sum(0)), scores(weights @ st["ReefFormer"])
        for ref in REFS:
            point = improvement(rf_point, scores(st[ref].sum(0)))
            boot = improvement(rf_boot, scores(weights @ st[ref]))
            for j, metric in enumerate(METRICS):
                lo, hi = (np.nanquantile(boot[:, j], [0.025, 0.975]) if np.isfinite(point[j]) else (np.nan, np.nan))
                rows.append({"season": name, "metric": metric, "reference": ref, "improvement_pct": point[j],
                             "ci_low": lo, "ci_high": hi, "significant": bool(lo > 0 or hi < 0),
                             "n_origins": len(st["ReefFormer"])})

    table_s33 = pd.DataFrame(rows)
    table_s32 = pd.DataFrame([{"model": m, **dict(zip(METRICS, scores(totals[m])))} for m in MODELS])
    table_s32.to_csv(out_dir / "TABLE_S32_GBR.csv", index=False)
    table_s33.to_csv(out_dir / "TABLE_S33_GBR.csv", index=False)

    ref32 = pd.read_csv(REFERENCE / "TABLE_S32_GBR.csv").set_index("model").loc[MODELS, METRICS]
    ref33 = pd.read_csv(REFERENCE / "TABLE_S33_GBR.csv")
    d32 = float(np.nanmax(np.abs(table_s32.set_index("model")[METRICS].to_numpy() - ref32.to_numpy())))
    merged = table_s33.merge(ref33, on=["season", "metric", "reference"], suffixes=("", "_ref"))
    d33 = float(np.nanmax(np.abs(merged[["improvement_pct", "ci_low", "ci_high"]].to_numpy()
                                 - merged[["improvement_pct_ref", "ci_low_ref", "ci_high_ref"]].to_numpy())))
    same_sig = bool((merged.significant == merged.significant_ref).all())
    max_regen = max(r["max_relative_difference"] for r in regen_check)
    audit = {"regenerated_models_max_relative_difference": max_regen,
             "table_s32_max_abs_difference": d32, "table_s33_max_abs_difference": d33,
             "table_s33_rows_compared": int(len(merged)), "significance_flags_identical": same_sig,
             "tolerances": {"regenerated_relative": 1e-5, "table_s32": 1e-4, "table_s33": 1e-2}}
    audit["status"] = "PASS" if (max_regen <= 1e-5 and d32 <= 1e-4 and d33 <= 1e-2 and same_sig
                                 and len(merged) == len(ref33)) else "FAIL"
    pd.DataFrame(regen_check).to_csv(out_dir / "regeneration_check.csv", index=False)
    (out_dir / "verification.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(table_s32.round(4).to_string(index=False))
    print(json.dumps(audit, indent=2))
    if audit["status"] != "PASS":
        raise SystemExit("Warm-season verification failed")


if __name__ == "__main__":
    main()
