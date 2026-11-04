# Verification record

Release verification was completed on 2026-10-10 with Python 3.13, NumPy
2.3.5, pandas 2.3.3, and PyTorch 2.11.0 (CUDA 12.8).

| Check | Result |
|---|---|
| Synthetic demo | Pass |
| Unit and checkpoint-loading tests | 5 passed |
| Great Barrier Reef CoralTemp reference reproduction | Pass; 15 rows, maximum metric difference 7.9e-10 deg C |
| Restricted-domain handling without the Hainan files | Pass; clear on-request message, no traceback |
| Sensitive-information and local-path scan (`scripts/audit_release.py`) | Pass |
| Files at least 50 MB | None |

The reproduction tolerance is `1e-4 deg C`. Generated prediction arrays and
reports are written under the ignored `outputs/` directory. The Hainan domains
were verified on the full archive with the same scripts (maximum difference
2.7e-9 deg C for Hainan CoralTemp and 3.0e-9 deg C for Hainan OSTIA).
