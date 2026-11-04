# Data provenance and access

This repository releases one complete domain, the central Great Barrier Reef
(GBR), so that every step of the method can be run and checked end to end. The
two Hainan Island domains are distributed on request.

| Domain | Pixels | Source | In this repository |
|---|---|---|---|
| `gbr_coraltemp` | 292 | NOAA CoralTemp v3.1, 2000-01-01 to 2026-09-07 | Processed data, pixel inventory, 6 checkpoints, reference tables |
| `hainan_coraltemp` | 154 | NOAA CoralTemp v3.1 | On request |
| `hainan_ostia` | 154 | Copernicus Marine OSTIA | On request |

## Released GBR files

- `data/processed/gbr_coraltemp_daily.npz`: daily SST, anomalies, the
  training-only climatology and anomaly scale, damped-persistence coefficients,
  frozen split indices (`Train`, `Val`, `Dev`, `Test2026`), dates, and the
  ordered pixel coordinates.
- `data/processed/gbr_coraltemp_protocol.json`: pixel-selection rule, splits,
  origin counts, and dataset hashes.
- `data/inventories/gbr_coraltemp_pixels.csv`: the 292 CoralTemp cells within
  10 km of 33 preregistered reef anchors (18 AIMS Long-Term Monitoring
  Program, 12 AIMS Marine Monitoring Program, and 3 Great Barrier Reef Marine
  Park Authority sites).
- `checkpoints/gbr_coraltemp/`: 90-day and 365-day iTransformer branches for
  seeds 42, 43, and 44.
- `reference_results/gbr_coraltemp/`: archived summary metrics and fusion
  parameters used by `scripts/reproduce_reference.py`.

No validation, development, or 2026 observation contributes to the stored
climatology, scale, or persistence coefficients. SHA-256 hashes of all released
files are listed in `MANIFEST.sha256`.

## Requesting the Hainan artifacts

The Hainan processed datasets, pixel inventories, checkpoints, and reference
tables are available for academic, non-commercial research. To request them,
open a GitHub issue to arrange contact with the authors (see the README).
Share your name, affiliation, and intended use through the agreed contact channel. Recipients are asked not to redistribute the files and to
cite the associated article.

The order in which the Hainan inventory, the 2026 evaluation protocol, and the
2026 data were fixed is documented in [`FREEZE_TIMELINE.md`](FREEZE_TIMELINE.md).

Place the received files at the paths below; `.gitignore` keeps them out of
version control. Check them against these SHA-256 hashes before use.

```text
1851293fbd1e8a66eaacffd71c9392faaba5422851010513d0f7ade6f5954247  data/processed/hainan_coraltemp_daily.npz
d373682381ceb83143a5932f2bd2dff99dde033548973f2261409d6d58e51a6d  data/processed/hainan_coraltemp_protocol.json
7bffd407fb70981fc77f66fb802e564b320664067f6854d2874729697ebe94e6  data/inventories/hainan_coraltemp_pixels.csv
3522f7abd113eba5f77dd93d630c63a390908a6402a3e7e439837df4b6215a64  checkpoints/hainan_coraltemp/iT_L365_seed42.pt
8a233fecc72a74674effdd7675b9f87b88bbed10513e436e1d43ab72bcd821b5  checkpoints/hainan_coraltemp/iT_L365_seed43.pt
69d93b6a0d0a67ad2d5aedf3d443906eaa31a1846181f7350fee4a2f326491be  checkpoints/hainan_coraltemp/iT_L365_seed44.pt
34326a11cfb0dc02706e4688daf081489664e58209a90fa6bf0fad0221981882  checkpoints/hainan_coraltemp/iT_L90_seed42.pt
c8acea95d34d72bf50ab5720e731e97ff9718393ec1fd13003b2ec00e3bacc48  checkpoints/hainan_coraltemp/iT_L90_seed43.pt
4eb01d2a6b08c2e6173e5a647e6c26e3368f656d7946c7968b5e46e458b8fb36  checkpoints/hainan_coraltemp/iT_L90_seed44.pt
d41f077adbc2799f730b4ddf9af091067a0782285d197d1daf37ff36fc181ba3  reference_results/hainan_coraltemp/CORE_METRICS_SUMMARY.csv
1d3fae8ebb966c56580057d9dbd28812b26356ae1e5e1a5ce714cd8876cb08cd  data/processed/hainan_ostia_daily.npz
f692616a0d83d7c04e1d14076adf90ef4d0514e81d2024d7db6fc6e130760a0e  data/processed/hainan_ostia_protocol.json
f96eedffbdda0fdee3400ce91129c947052963418085785787ab273e7d70a2d8  data/inventories/hainan_ostia_pixel_mapping.csv
3cd9df4e6bed353b7da4e77d9c25d249127668b309f0244f08f168cd90eb1071  checkpoints/hainan_ostia/iT_L365_seed42.pt
2849fd268147eeae39b689eb966e1312d59984e5ad0a08e84da0a676a781a205  checkpoints/hainan_ostia/iT_L365_seed43.pt
bb5b4b2495a49a227baeec257927f86dbfceda2547d676505a964c147a4474eb  checkpoints/hainan_ostia/iT_L365_seed44.pt
3c12d4b645fbb4f43b0583ef8956a6e361a85e4787ec3d3e854571fac175d820  checkpoints/hainan_ostia/iT_L90_seed42.pt
c611710963bb7c7cc6ba054c22e8a5253c7b50519c1be81ef39e2ee2432de115  checkpoints/hainan_ostia/iT_L90_seed43.pt
34cbcf7214aa3ff23e52090d703ba5ca31e0b6f0bd184d8b9ccf3d8be227cb3b  checkpoints/hainan_ostia/iT_L90_seed44.pt
eabcc9ce7d69b9b13402e4a17888571e7d564c9d674a632fab486a48c0336982  reference_results/hainan_ostia/SUMMARY_MEAN_SD.csv
```

With these files in place, `scripts/reproduce_reference.py --domain
hainan_coraltemp` and `--domain hainan_ostia` run exactly as for the GBR.

## Source data and attribution

**NOAA CoralTemp v3.1.** NOAA states that Coral Reef Watch web content is
public domain and may be distributed freely with appropriate credit. Cite NOAA
Coral Reef Watch and Skirving et al. (2020),
`https://doi.org/10.3390/rs12233856`. Source portal:
`https://coralreefwatch.noaa.gov/product/5km_v3.1_op/index_5km_sst.php`.

**GBR reef anchors.** Thirty anchor locations were drawn from public Australian
Institute of Marine Science monitoring resources (CC BY) and three from public
Great Barrier Reef Marine Park Authority site information. Credit the Australian
Institute of Marine Science, its Long-Term Monitoring Program and Marine
Monitoring Program, and the Great Barrier Reef Marine Park Authority.

**Copernicus Marine OSTIA** (Hainan, on request). Product
`SST_GLO_SST_L4_REP_OBSERVATIONS_010_011`, dataset
`METOFFICE-GLO-SST-L4-REP-OBS-SST`, version `202003`,
`https://doi.org/10.48670/moi-00168`. Acknowledge as: "Generated using E.U.
Copernicus Marine Service Information; https://doi.org/10.48670/moi-00168."
