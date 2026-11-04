# ReefFormer

A toolkit for lead-dependent fusion of sea surface temperature forecasts in
reef-adjacent coastal waters.

## Scope

ReefFormer combines forecasts from short- and long-context regional
iTransformer branches with damped anomaly persistence. The fusion weights
depend on forecast lead and are fitted on validation forecasts.

This repository provides:

- implementations of Lead-dependent Context Fusion (LCF), Lead-dependent
  Persistence Fusion (LPF), and damped anomaly persistence;
- a regional iTransformer implementation and branch-training entry point;
- a synthetic example and tests;
- processed Great Barrier Reef data, archived branch checkpoints, and
  reference results for the principal reproduction workflow.

## Available materials

| Material | Location | Access |
|---|---|---|
| Forecast-fusion and model code | [`src/reefformer/`](src/reefformer/) | Included |
| Synthetic example | [`scripts/run_demo.py`](scripts/run_demo.py) | Included |
| Great Barrier Reef data and pixel inventory | [`data/`](data/) | Included |
| Six Great Barrier Reef branch checkpoints | [`checkpoints/gbr_coraltemp/`](checkpoints/gbr_coraltemp/) | Included |
| Great Barrier Reef reference results | [`reference_results/gbr_coraltemp/`](reference_results/gbr_coraltemp/) | Included |
| Hainan CoralTemp and OSTIA data and checkpoints | See [`docs/DATA.md`](docs/DATA.md) | On request |

The included checkpoints cover the 90- and 365-day branches for seeds 42, 43,
and 44. The full set of external-baseline and exploratory experiments in the
accompanying manuscript is not bundled in this repository.

## Installation

Clone or download this repository, then open a terminal in its root directory.
Python 3.10 or later is required.

```bash
python -m venv .venv
```

Activate the environment:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# Linux / macOS
source .venv/bin/activate
```

Install the package and test dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[test]"
```

See [`docs/INSTALL.md`](docs/INSTALL.md) for environment and CUDA notes.

## Usage

### Run the synthetic example

```bash
python scripts/run_demo.py
pytest
```

This checks the installation without downloading additional data or
checkpoints.

### Reproduce the Great Barrier Reef reference results

```bash
python scripts/reproduce_reference.py --domain gbr_coraltemp --device auto
```

The command loads the archived branches, refits LCF and LPF on 2018-2021
validation forecasts, and compares the generated summary metrics with the
included reference tables. The numerical tolerance is `1e-4` degrees Celsius.
See [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md) for the exact scope.

### Use the fusion API

```python
from reefformer import fit_reef_former, apply_reef_former

params = fit_reef_former(short_val, long_val, persistence_val, truth_val)
forecast = apply_reef_former(short_test, long_test, persistence_test, params)
```

Arrays use the shape `[forecast_origin, lead, spatial_unit]` in anomaly units.
See [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) for input definitions and examples.

## Data access

The processed Great Barrier Reef domain is included. It contains 292
CoralTemp cells and uses chronological training, validation, development, and
2026 holdout periods.

The processed Hainan CoralTemp and OSTIA domains and their checkpoints are
available on request under the access arrangements described in
[`docs/DATA.md`](docs/DATA.md). That document also records source attribution,
file paths, and hashes. Source datasets remain subject to their providers'
terms.

## Repository layout

```text
.
|-- src/reefformer/            # Fusion, regional iTransformer, metrics
|-- scripts/                  # Demo, reference reproduction, branch training
|-- tests/                    # Fusion and model-loading tests
|-- data/                     # Public GBR processed data and inventory
|-- checkpoints/              # Archived GBR branch checkpoints
|-- reference_results/        # Reference metrics and fitted coefficients
|-- docs/                     # Installation, usage, data, reproduction
|-- CITATION.cff              # Software citation metadata
|-- MANIFEST.sha256           # Released-file integrity checks
`-- LICENSE
```

## Reproducibility boundary

- The public workflow reproduces the principal Great Barrier Reef branch and
  fusion results from the included artifacts.
- Reproducing the Hainan results requires the files distributed on request.
- External-baseline implementations, all baseline checkpoints, and every
  exploratory experiment are not included in this package.
- Retraining can produce small numerical differences across software and
  hardware environments. The archived checkpoints are the reference for
  checkpoint-based reproduction.

## Associated manuscript and citation

*ReefFormer: Lead-Dependent Fusion of Transformer and Persistence Forecasts
for 1-30-Day Sea Surface Temperature Prediction in Coral Reef Coastal Waters*
is a research manuscript. A publication link and final bibliographic details
will be added when available.

Software citation metadata is provided in [`CITATION.cff`](CITATION.cff).
For the associated manuscript:

```bibtex
@unpublished{lu2026reefformer,
  author = {Lu, Yujun and Yang, Changen and Liang, Xi and Huang, Wenguo and Zhou, Zhi},
  title = {ReefFormer: Lead-Dependent Fusion of Transformer and Persistence Forecasts for 1--30-Day Sea Surface Temperature Prediction in Coral Reef Coastal Waters},
  year = {2026},
  note = {Research manuscript}
}
```

## License

The source code is distributed under the GNU Affero General Public License
v3.0; see [`LICENSE`](LICENSE). Data attribution and redistribution conditions
are documented separately in [`docs/DATA.md`](docs/DATA.md).

## Contact

For usage questions or to arrange contact about Hainan data access, open an
issue through this repository's **Issues** tab. Share personal contact details
and any restricted materials only through an agreed private channel.
