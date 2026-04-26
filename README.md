# SEHA — Solidity Explainable Hybrid Analyzer

**A hybrid smart contract vulnerability analyzer combining rule-based static detection with machine learning for semantic and business logic flaws.**

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Slither](https://img.shields.io/badge/Slither-Static_Analysis-orange)
![RandomForest](https://img.shields.io/badge/ML-RandomForest-green)
![Accuracy](https://img.shields.io/badge/Accuracy-91.8%25-brightgreen)

---

## 📋 Overview

SEHA is a **hybrid analyzer** for Solidity smart contracts that combines:

- **Phase 1**: High-precision **static detectors** powered by Slither
- **Phase 2**: **Machine Learning (RandomForest)** for complex semantic/business logic vulnerabilities (reward logic flaws, price oracle manipulation, flash loan attacks, etc.)

It provides:
- Clear explanations
- Exact line numbers
- Suggested fixes
- Professional **PDF reports**

---

## ✨ Key Features

- 10+ static detectors:
  - Reentrancy
  - Access Control
  - `tx.origin`
  - Selfdestruct
  - Unchecked Calls
  - Timestamp Dependence
  - Delegatecall
  - Front-running
- ML-based detection for semantic/business logic issues
- Hybrid analysis mode (`--mode hybrid`)
- Explainable results with human-readable explanations
- Consolidated PDF report generation
- Clean, modular, and extensible architecture
- Easy testing suite

---

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/HarpreetSingh2005/solidity-analyzer.git
cd solidity-analyzer

pip install slither-analyzer fpdf2 pandas scikit-learn joblib matplotlib seaborn
```

---

### Usage

#### Analyze a single contract (recommended):
```bash
python main.py tests/Reentrancy.sol --mode hybrid
```

#### Analyze in static-only mode:
```bash
python main.py dataset/business_logic/broken_rewards.sol
```

#### Run full test suite + generate PDF report:
```bash
python run_all_tests.py
```

#### Test any individual contract:
```bash
python test_single_contract.py dataset/business_logic/broken_rewards.sol --mode hybrid
```

---

## 📊 Project Results

- **Dataset**: 241 smart contracts  
  - 143 vulnerable  
  - 98 safe  

- **Best Model**: RandomForest  
- **Accuracy**: 91.80%  
- **F1-Score**: 0.9333  

The hybrid system successfully detected **8 issues across 10 diverse test contracts** with very low false positives.  

(Screenshots: model comparison, dataset distribution, and feature importance are available in the repository.)

---

## 🏗️ Project Structure

```
solidity-analyzer/
├── core/                  # Core analyzer + PDF generator
├── detectors/             # Static detectors (Slither-based)
├── ml/                    # Machine Learning module
│   ├── feature_extractor.py
│   ├── model.py
│   └── ml_analyzer.py
├── dataset/               # Training data (business_logic, price_oracle, flash_loan, safe)
├── tests/                 # Test contracts
├── reports/               # Generated JSON + PDF reports
├── scripts/               # Utility scripts
├── main.py                # Main CLI
├── run_all_tests.py       # Batch testing + PDF
└── test_single_contract.py
```

---

## 🔬 How It Works

- **Static Phase** → Runs multiple high-precision Slither detectors  
- **ML Phase** → Extracts 19 semantic features and runs RandomForest model  
- **Hybrid Reporting** → Combines both with clear explanations and fixes  

---

## 📸 Screenshots

- Model Performance Comparison  
- Dataset Distribution (241 contracts)  
- Feature Importance (RandomForest)  
- Sample PDF Report  

---

## 📝 Limitations

- ML component is probabilistic and may produce occasional false positives on complex contracts  
- Very advanced business logic vulnerabilities still require manual review  
- Trained on a curated dataset of 241 contracts  

---

## 🔮 Future Work

- Add deeper data-flow and taint analysis features  
- Integrate symbolic execution / formal verification  
- Develop a web interface or VS Code extension  
- Support for newer Solidity versions and upgradeable contracts  

---

## 📄 License

MIT License  

---

## 🙌 Acknowledgments

- Built as a Minor Project (2026)  
- Uses Slither by Trail of Bits  
- Dataset inspired by SmartBugs Curated  

---

**Made with ❤️ for smart contract security** 🚀
