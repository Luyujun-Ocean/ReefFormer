# Freeze timeline of the Hainan 2026 holdout

This note gives the order of the steps summarized in Table A3(b) of the
article. Times are local (UTC+8).

| Time | Step | SHA-256 prefix |
|---|---|---|
| 8 Sep 2026, 23:54 | Source-lineage review of the reef-survey anchor coordinates completed. Two survey sites whose recorded locations conflict between source tables are isolated. | -- |
| 9 Sep 2026, 00:02 | Hainan pixel inventory fixed at 154 cells: the nine candidate cells supported only by one of the isolated sites are removed. Isolating the second site removes no cell, because nearby anchors still support them. | `2c899779` (inventory file) |
| 9 Sep 2026, 04:23 | Architecture, fusion formulas, fitting rules, and the 2026 evaluation protocol written and hashed. The protocol text refers to the earlier 163-cell candidate list. | `2305f985` (`protocols/2026_TEST_PROTOCOL_PRE_DATA.json`) |
| 9 Sep 2026, 04:24 | CoralTemp 2026 extension downloaded. | `688c0437` (raw 2026 subset) |
| 10 Sep 2026 | All networks trained on the 154-cell inventory from 2000--2021 data alone under the frozen rules; every context, checkpoint, and fusion coefficient fitted on 2018--2021 validation forecasts; 2026 forecasts produced by forward passes only. | -- |

The pixel change rests on survey-coordinate quality alone and uses no SST
value. An evaluation of the earlier 163-cell networks on the 2026 holdout gives
the same ranking (RMSE 0.9279 °C for ReefFormer and 0.9319 °C for DLinear).

The LSTM baseline and the GBR, OSTIA, and ERA5 experiments were added after the
2026 extension was obtained, under the same frozen rules; none of them changes
any ReefFormer quantity.

The protocol file is stored byte-for-byte (`.gitattributes` disables line-ending
conversion under `protocols/`), so `sha256sum` reproduces the prefix above. The
inventory and raw-2026 hashes are recorded in `hainan_coraltemp_protocol.json`,
which is distributed with the Hainan artifacts on request (see `DATA.md`).
