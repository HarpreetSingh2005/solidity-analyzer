# SESA — Solidity Explainable Static Analyzer

SESA is a professional, hybrid vulnerability analyzer designed for research-grade smart contract auditing. It combines the speed and determinism of Slither-based static rules with a powerful Phase 2 Machine Learning layer tailored for semantic DeFi vulnerabilities.

## Architecture

The project is structured into two complementary phases to ensure both high-precision static detection and robust semantic analysis.

*   **Phase 1 (Static Analysis)**: High-precision Slither detectors in `detectors/` using centralized parsing. It guarantees exact line numbers, clear explanations, and actionable suggested fixes for common vulnerabilities.
*   **Phase 2 (Machine Learning)**: A semantic layer targeting complex DeFi vulnerabilities like Price Oracle manipulation, Flash Loan attacks, and Business Logic flaws.

## Supported Static Detectors

| Vulnerability | Category | Severity | Description |
| :--- | :--- | :--- | :--- |
| **Reentrancy** | Access Control / State | High | Flags external calls made before updating state variables (CEI Violation). |
| **Missing Access Control** | Authorization | Critical | Flags modification of privileged variables (e.g., owner) without an access guard. |
| **tx.origin Phishing** | Authentication | High | Detects vulnerable use of `tx.origin` for authorization. |
| **Unprotected selfdestruct** | Access Control | Critical | Flags unprotected calls to `selfdestruct` / `suicide`. |
| **Unchecked External Call** | Error Handling | Medium | Detects low-level calls whose boolean return value is not captured. |
| **Shadowed Variable** | Logic Error | Medium | Flags state variables in a child contract that shadow variables in a parent. |

## Installation

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install and use Solc 0.8.0
solc-select install 0.8.0
solc-select use 0.8.0
```

## Usage

You can run SESA in either `static` mode (Slither only) or `hybrid` mode (Static + ML).

```bash
# Run in Static Mode (Default)
python main.py path/to/contract.sol --mode static

# Run in Hybrid Mode
python main.py path/to/contract.sol --mode hybrid
```

## Dataset Generation (Phase 2)

To generate the evaluation dataset containing 30 vulnerable contracts (Business Logic, Price Oracle, Flash Loan):

```bash
python scripts/create_dataset.py
```
This will populate the `dataset/` directory and generate a `labels.csv` file for ML training.

## Project Structure

*   `core/`: Orchestrator and reporting logic (`analyzer.py`).
*   `detectors/`: Standardized static vulnerability plugins.
*   `dataset/`: Generated dataset contracts and labels for ML.
*   `ml/`: Machine Learning layer for semantic analysis.
*   `scripts/`: Utilities for dataset generation (`create_dataset.py`).

## Contribution

Contributions are welcome! If you're adding a new static detector, ensure it follows the standardized output schema (vulnerability, contract, function, line, severity, explanation, suggested_fix) and uses type annotations.
