# SESA — Solidity Explainable Static Analyzer

SESA is a hybrid analyzer designed for research-grade smart contract auditing. It combines the speed of Slither-based static rules with a Phase 2 ML layer for semantic DeFi vulnerabilities.

## Architecture
- **Phase 1 (Static)**: High-precision Slither detectors in `detectors/` using centralized parsing.
- **Phase 2 (ML)**: Semantic layer targeting Price Oracle, Flash Loan, and Business Logic flaws.

## Installation
1. `pip install -r requirements.txt`
2. `solc-select install 0.8.0 && solc-select use 0.8.0`

## Usage
`python main.py path/to/contract.sol`

## Project Structure
- `core/`: Orchestrator and reporting logic.
- `detectors/`: Standardized static vulnerability plugins.
- `ml/`: Machine Learning layer for semantic analysis.
- `scripts/`: Utilities for dataset generation.
