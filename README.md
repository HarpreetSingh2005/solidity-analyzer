# SESA — Solidity Explainable Static Analyzer

> A **hybrid smart contract vulnerability analyzer** combining deterministic
> static rule-based detection (Slither) with a lightweight explainable ML
> layer (RandomForest + SHAP). Built as a research project for academic study
> of automated vulnerability detection in Solidity smart contracts.

---

## Table of Contents

1. [Features](#features)
2. [Project Structure](#project-structure)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Static Detectors](#static-detectors)
6. [Phase 1 — Static Analysis](#phase-1--static-analysis)
7. [Phase 2 — ML Semantic Layer](#phase-2--ml-semantic-layer)
8. [Adding a New Detector](#adding-a-new-detector)
9. [Dataset](#dataset)
10. [Research Context](#research-context)
11. [Requirements](#requirements)

---

## Features

| Feature | Details |
|---|---|
| **10 Static Detectors** | Rule-based, high-precision detection of known Solidity vulnerability patterns |
| **ML Semantic Layer** | RandomForest model catches business-logic anomalies that rule-based tools miss |
| **SHAP Explainability** | Human-readable reasoning (top feature contributions) for every AI flag |
| **Hybrid Merge** | Static + AI findings unified in a single structured report |
| **JSON Reports** | Machine-readable output saved to `reports/` for every run |
| **PDF Export** | Professional consolidated PDF with Static and AI sections (`--pdf` flag) |
| **Extensible Registry** | Drop a new `.py` file in `detectors/` and it auto-loads — zero boilerplate |
| **Consistent Finding Schema** | Every detector returns the same 7-key dict format |

---

## Project Structure

```
solidity-analyzer/
├── core/
│   ├── analyzer.py          # Orchestrator — Slither init once, detector registry, ML call
│   ├── extractor.py         # Feature extractor for ML (16-dim vector per function)
│   └── pdf_generator.py     # Consolidated PDF report generator (fpdf2)
│
├── detectors/               # Static detectors — auto-discovered by analyzer.py
│   ├── __init__.py          # Package docstring + schema documentation
│   ├── reentrancy.py        # CEI violation detector (SWC-107)
│   ├── access_control.py    # Missing owner/role guard (SWC-105)
│   ├── tx_origin.py         # tx.origin phishing (SWC-115)
│   ├── self_destruct.py     # Unprotected selfdestruct (SWC-106)
│   ├── unchecked_external_calls.py  # Ignored low-level call return (SWC-104)
│   ├── shadowed_variable.py # State variable shadowing (SWC-119)
│   ├── integer_overflow.py  # Unsafe arithmetic in <0.8.0 (SWC-101)
│   ├── timestamp_dependence.py      # block.timestamp misuse (SWC-116)
│   ├── dangerous_delegatecall.py    # Dynamic delegatecall target (SWC-112)
│   └── front_running.py     # ERC-20 approve race + timestamp payable (SWC-114)
│
├── ml/
│   ├── feature_extractor.py # Extracts 16-dim feature vector per function
│   ├── model.py             # RandomForest load / predict / SHAP explain
│   ├── ml_analyzer.py       # ML entry point → standard finding dicts
│   ├── train_on_colab.ipynb # Google Colab training notebook
│   └── training_instructions.md
│
├── dataset/
│   ├── business_logic/      # 10 vulnerable contracts — economic invariant flaws
│   ├── price_oracle/        # 10 vulnerable contracts — spot price / stale feed
│   ├── flash_loan/          # 10 vulnerable contracts — reentrancy + governance
│   ├── smartbugs/           # Clone SmartBugs Curated here (see Dataset section)
│   └── labels.csv           # Ground-truth labels for all 30 custom contracts
│
├── scripts/
│   └── create_dataset.py    # Generates all 30 dataset contracts + labels.csv
│
├── tests/
│   ├── *.sol                # Vulnerable test contracts (one per detector)
│   └── unit/
│       └── test_detectors.py
│
├── reports/                 # JSON analysis reports (gitignored)
├── main.py                  # CLI entry point
├── run_all_tests.py         # Batch test runner (all contracts in tests/)
└── requirements.txt
```

---

## Installation

### Prerequisites

- **Python 3.8 – 3.11** (Slither is not yet compatible with 3.12+)
- **[solc-select](https://github.com/crytic/solc-select)** — Solidity compiler version manager
- **[Slither](https://github.com/crytic/slither)** — static analysis framework

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/HarpreetSingh2005/solidity-analyzer.git
cd solidity-analyzer

# 2. Create and activate a virtual environment (recommended)
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install and select the Solidity compiler
pip install solc-select
solc-select install 0.8.0
solc-select use 0.8.0

# 5. Verify Slither is working
slither --version
```

> **Windows note:** If `python` does not resolve to the correct interpreter,
> use `py -3.11` or the full path. A `run.bat` launcher is provided for
> convenience.

---

## Usage

### Hybrid analysis (Static + AI)
```bash
python main.py tests/Reentrancy.sol
```

### Static analysis only (faster, no ML model required)
```bash
python main.py tests/Reentrancy.sol --no-ml
```

### Generate a PDF report after analysis
```bash
python main.py tests/Reentrancy.sol --pdf
```

### Analyze any contract
```bash
python main.py path/to/YourContract.sol --no-ml
```

### Run the full test suite (all contracts in `tests/`)
```bash
python run_all_tests.py
```

### Generate the Phase 2 dataset
```bash
python scripts/create_dataset.py
# → dataset/business_logic/*.sol
# → dataset/price_oracle/*.sol
# → dataset/flash_loan/*.sol
# → dataset/labels.csv
```

### Run unit tests
```bash
pytest tests/unit/ -v
```

---

## Static Detectors

| # | File | Vulnerability | Severity | SWC | Description |
|---|------|--------------|----------|-----|-------------|
| 1 | `reentrancy.py` | Reentrancy (CEI Violation) | High | SWC-107 | External call before state update violates Checks-Effects-Interactions |
| 2 | `access_control.py` | Missing Access Control | Critical | SWC-105 | Privileged state variables modified without owner/role guard |
| 3 | `tx_origin.py` | Vulnerable Use of tx.origin | High | SWC-115 | `tx.origin` used for authentication — vulnerable to phishing |
| 4 | `self_destruct.py` | Unprotected Self-Destruct | Critical | SWC-106 | `selfdestruct` callable by any address without access control |
| 5 | `unchecked_external_calls.py` | Unchecked Low-Level Call | Medium | SWC-104 | Return value of `call()` / `delegatecall()` silently ignored |
| 6 | `shadowed_variable.py` | State Variable Shadowing | Medium | SWC-119 | Child contract redeclares a variable from the parent contract |
| 7 | `integer_overflow.py` | Integer Overflow / Underflow | High | SWC-101 | Unsafe arithmetic in Solidity < 0.8.0 without SafeMath |
| 8 | `timestamp_dependence.py` | Timestamp Dependence | Medium | SWC-116 | `block.timestamp` used in critical conditional logic |
| 9 | `dangerous_delegatecall.py` | Dangerous Delegatecall | Critical | SWC-112 | `delegatecall` to a non-constant / user-controlled address |
| 10 | `front_running.py` | Front-Running | Medium | SWC-114 | ERC-20 approve race condition or timestamp-dependent payable |

---

## Phase 1 — Static Analysis

Phase 1 uses **Slither's intermediate representation (SlithIR)** to apply
deterministic rules to the parsed contract.  Key architectural decisions:

- **Single parse**: `core/analyzer.py` initialises Slither once and passes
  the `Slither` object to every detector — no repeated compilation.
- **Auto-discovery**: `_build_detector_registry()` imports every `detect_*`
  function from `detectors/` at startup using `importlib`.  Adding a new
  detector requires no changes to `analyzer.py`.
- **Consistent schema**: Every finding dict has exactly 7 keys
  (`vulnerability`, `contract`, `function`, `line`, `severity`,
  `explanation`, `suggested_fix`).
- **Deduplication**: Each detector maintains a `seen` set to avoid emitting
  duplicate findings for the same location.

**Strengths:** Zero false negatives on known patterns; fast (<1 s); no
external API required.

**Limitations:** Cannot reason about complex multi-contract business logic,
novel economic invariants, or cross-transaction state changes.

---

## Phase 2 — ML Semantic Layer

Phase 2 addresses Phase 1's limitations with a **RandomForestClassifier**
trained on a curated dataset of 30 vulnerable contracts across three
semantic categories:

| Category | Contracts | What it detects |
|----------|-----------|-----------------|
| Business Logic | 10 | Reward rounding, vesting bypass, governance double-vote, fee manipulation |
| Price Oracle | 10 | Spot price manipulation, stale feeds, self-referential oracles |
| Flash Loan | 10 | Single-transaction reentrancy, collateral inflation, governance attacks |

### Architecture

```
Contract → core/extractor.py → 16-dim feature vector
                                      ↓
                          ml/model.py (RandomForest)
                                      ↓
                    SHAP TreeExplainer → top-3 features
                                      ↓
                      ml/ml_analyzer.py → finding dicts
```

### Training (Google Colab)

1. Open `ml/train_on_colab.ipynb` in [Google Colab](https://colab.research.google.com/)
2. Run all cells — auto-clones SmartBugs Curated, extracts features, trains,
   exports `model.pkl` and `label_encoder.pkl`
3. Download `model.pkl` → place in `ml/model.pkl`
4. Re-run the analyzer — ML confidence scores appear in output automatically

### Inference

- **Speed**: < 1 second per contract on a laptop CPU
- **Explainability**: SHAP highlights the top 3 features driving each flag
- **Fallback**: If `ml/model.pkl` is missing or SHAP errors, static results
  are always saved — Phase 2 never breaks Phase 1

---

## Adding a New Detector

The registry auto-discovers all `detect_*` functions in `detectors/`.

```python
# detectors/my_detector.py
"""
Detector: My New Vulnerability
SWC-XXX  |  Severity: High

Explanation of the vulnerability.
"""
from slither import Slither

def detect_my_vulnerability(slither: Slither) -> list[dict]:
    findings = []
    seen = set()

    for contract in slither.contracts:
        if contract.is_interface or contract.is_library:
            continue
        # ... detection logic ...
        findings.append({
            "vulnerability" : "My Vulnerability Name",
            "contract"      : contract.name,
            "function"      : function.name,   # or "(state variable)"
            "line"          : line_number,     # int or "Unknown"
            "severity"      : "High",          # Critical | High | Medium | Low
            "explanation"   : "What is wrong and why it is dangerous.",
            "suggested_fix" : "How to fix it.",
        })

    return findings
```

**That's all.** `core/analyzer.py` will pick it up automatically on the next
run.

---

## Dataset

The `dataset/` directory is populated by running:
```bash
python scripts/create_dataset.py
```

This generates 30 high-quality vulnerable Solidity contracts with realistic
vulnerability patterns and detailed inline comments explaining each flaw.  A
`labels.csv` is also written with ground-truth labels for ML training.

To add real-world training data, clone SmartBugs Curated into
`dataset/smartbugs/`:
```bash
git clone https://github.com/smartbugs/smartbugs-curated dataset/smartbugs
```

---

## Research Context

SESA is a Phase 1 + Phase 2 hybrid vulnerability analyzer built for academic
research into automated smart contract auditing.  The goal is to combine the
**precision** of static analysis with the **recall** of ML-based semantic
detection, providing explainable results suitable for inclusion in research
papers.

**Key research contributions:**
- Centralized, single-parse architecture ensuring efficient multi-detector analysis
- Consistent 7-key finding schema enabling structured comparison and evaluation
- Lightweight ML layer trainable on a laptop GPU-free environment (Colab)
- SHAP-based explainability bridging the gap between black-box ML and auditor trust

**Tech stack:** Python · Slither · scikit-learn · SHAP · fpdf2 · pytest

---

## Requirements

See [requirements.txt](requirements.txt) for the complete list.

```
slither-analyzer>=0.10.0
scikit-learn>=1.3.0
pandas>=2.0.0
numpy>=1.24.0
joblib>=1.3.0
shap>=0.44.0
fpdf2>=2.7.0
pytest>=7.4.0
```
