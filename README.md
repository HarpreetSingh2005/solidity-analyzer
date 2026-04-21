# SESA — Solidity Explainable Static Analyzer

> A hybrid smart contract vulnerability analyzer combining **static rule-based detection** (Slither) with a **lightweight explainable ML layer** (RandomForest + SHAP). Built as a research project for academic study of automated vulnerability detection in Solidity smart contracts.

---

## Features

- **10 Static Detectors** — rule-based, zero false-negatives on known patterns
- **ML Semantic Layer** — RandomForest model flags business-logic anomalies Slither misses
- **SHAP Explainability** — human-readable reasoning for every AI flag
- **Hybrid Merge** — static + AI findings in a single unified report
- **PDF Export** — professional consolidated report with Static and AI sections
- **Extensible Registry** — drop a new `.py` file in `detectors/` and it auto-loads

---

## Project Structure

```
solidity-analyzer/
├── core/
│   ├── analyzer.py          # Orchestrator — Slither init, detector registry, ML call
│   └── pdf_generator.py     # Consolidated PDF report generator
├── detectors/               # Static detectors (auto-discovered)
│   ├── reentrancy.py
│   ├── access_control.py
│   ├── tx_origin.py
│   ├── self_destruct.py
│   ├── unchecked_external_calls.py
│   ├── shadowed_variable.py
│   ├── integer_overflow.py
│   ├── timestamp_dependence.py
│   ├── dangerous_delegatecall.py
│   └── front_running.py
├── ml/
│   ├── feature_extractor.py # Extracts 16-dim feature vector per function
│   ├── model.py             # RandomForest load/predict/SHAP explain
│   ├── ml_analyzer.py       # ML entry point → standard finding format
│   ├── train_on_colab.ipynb # Google Colab training notebook
│   └── training_instructions.md
├── tests/
│   ├── *.sol                # Vulnerable test contracts (one per detector)
│   └── unit/
│       └── test_detectors.py
├── reports/                 # JSON reports (gitignored)
├── main.py                  # CLI entry point
├── run_all_tests.py         # Batch test runner
├── run.bat                  # Windows launcher (uses correct Python 3.11)
└── requirements.txt
```

---

## Installation

### Prerequisites
- Python 3.8 – 3.11
- [solc-select](https://github.com/crytic/solc-select) (Solidity compiler version manager)
- [Slither](https://github.com/crytic/slither)

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/HarpreetSingh2005/solidity-analyzer.git
cd solidity-analyzer

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install and select the Solidity compiler
pip install solc-select
solc-select install 0.8.0
solc-select use 0.8.0

# 4. Verify Slither is installed
slither --version
```

### Windows Note
If `python` does not resolve correctly on Windows, use the provided launcher:
```bat
.\run.bat tests/Reentrancy.sol --ml
```

---

## Usage

### Basic analysis (Hybrid Static + AI)
```bash
python main.py tests/Reentrancy.sol
```

### Static analysis only (faster, no ML)
```bash
python main.py tests/Reentrancy.sol --no-ml
```

### Analyze any contract
```bash
python main.py path/to/YourContract.sol --ml
```

### Run full test suite (all contracts in `tests/`)
```bash
python run_all_tests.py
```

### Generate consolidated PDF report
```bash
python core/pdf_generator.py
# → Security_Vulnerability_Summary.pdf
```

### Run unit tests
```bash
pytest tests/unit/ -v
```

---

## Static Detectors

| # | Detector | Severity | SWC | Description |
|---|---|---|---|---|
| 1 | `reentrancy.py` | High | SWC-107 | External call before state update (CEI violation) |
| 2 | `access_control.py` | High | SWC-105 | Sensitive functions missing owner/role checks |
| 3 | `tx_origin.py` | High | SWC-115 | `tx.origin` used for authentication |
| 4 | `self_destruct.py` | Critical | SWC-106 | Unprotected `selfdestruct` call |
| 5 | `unchecked_external_calls.py` | Medium | SWC-104 | Return value of low-level call not checked |
| 6 | `shadowed_variable.py` | Low | SWC-119 | State variable shadowed by local declaration |
| 7 | `integer_overflow.py` | High | SWC-101 | Unsafe arithmetic in Solidity < 0.8.0 |
| 8 | `timestamp_dependence.py` | Medium | SWC-116 | `block.timestamp` in critical conditional logic |
| 9 | `dangerous_delegatecall.py` | Critical | SWC-112 | `delegatecall` to non-constant address |
| 10 | `front_running.py` | Medium | SWC-114 | ERC-20 approve race / timestamp-dependent payable |

---

## Phase 1 vs Phase 2

### Phase 1 — Static Analysis
Pure rule-based detection using Slither's IR. High precision on known vulnerability patterns. Zero external dependencies beyond Slither and Python.

### Phase 2 — ML Semantic Layer
A `RandomForestClassifier` trained on the [SmartBugs Curated](https://github.com/smartbugs/smartbugs-curated) dataset, applied on top of Phase 1. It catches **business logic anomalies** that rule-based detectors miss — unusual state transition patterns, complex multi-call flows, and semantic inconsistencies.

- **Training**: Google Colab (see `ml/train_on_colab.ipynb`)
- **Inference**: Local, < 1 second per contract
- **Explainability**: SHAP TreeExplainer highlights the top 3 features driving each flag
- **Fallback**: If ML fails (missing model, SHAP error), static results are always saved

#### Training the ML Model
1. Open `ml/train_on_colab.ipynb` in [Google Colab](https://colab.research.google.com/)
2. Run all cells — auto-clones SmartBugs, extracts features, trains, exports `model.pkl`
3. Download `model.pkl` → place in `ml/model.pkl`
4. Re-run the analyzer — ML confidence scores will now appear in output

---

## Adding a New Detector

The detector registry auto-discovers all `detect_*` functions in `detectors/`. To add a new detector:

1. Create `detectors/my_detector.py`
2. Define `def detect_my_vulnerability(slither) -> list:` returning finding dicts
3. **That's it.** No changes to `analyzer.py` needed.

Each finding dict must have:
```python
{
    "vulnerability": "Short name",
    "contract": "ContractName",
    "function": "functionName",
    "line": 42,
    "severity": "High",          # Critical / High / Medium / Low
    "explanation": "...",
    "suggested_fix": "..."
}
```

---

## Research Context

This project is a Phase 1 + Phase 2 hybrid vulnerability analyzer built for academic research into automated smart contract auditing. The goal is to combine the precision of static analysis with the recall of ML-based semantic detection, providing explainable results suitable for inclusion in research papers.

**Tech stack:** Python · Slither · scikit-learn · SHAP · fpdf2 · pytest

---

## Requirements

See [requirements.txt](requirements.txt) for the full list. Key dependencies:

```
slither-analyzer
scikit-learn
pandas
numpy
joblib
shap
fpdf2
pytest
```
