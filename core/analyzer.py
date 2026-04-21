# core/analyzer.py
"""
SESA — Solidity Explainable Static Analyzer
============================================
Core orchestrator. Slither is initialised **exactly once** here and the
resulting object is passed to every detector.

Finding schema:
  {
      "vulnerability" : str   — short human-readable name
      "contract"      : str   — Solidity contract name
      "function"      : str   — function name or "(state variable)"
      "line"          : int   — source line number
      "severity"      : str   — Critical | High | Medium | Low
      "explanation"   : str   — full human-readable explanation
      "suggested_fix" : str   — actionable remediation advice
  }
"""

from __future__ import annotations
import importlib
import inspect
import json
from datetime import datetime
from pathlib import Path
from typing import Any
from slither import Slither

def _build_detector_registry() -> list:
    """Dynamically loads all detect_* functions from the detectors/ package."""
    registry = []
    detectors_dir = Path(__file__).parent.parent / "detectors"
    for module_path in sorted(detectors_dir.glob("*.py")):
        if module_path.name.startswith("_"): continue
        module_name = f"detectors.{module_path.stem}"
        try:
            module = importlib.import_module(module_name)
            for name, obj in inspect.getmembers(module, inspect.isfunction):
                if name.startswith("detect_") and obj.__module__ == module_name:
                    registry.append(obj)
        except Exception as e:
            print(f"[WARN] Could not load detector '{module_name}': {e}")
    return registry

DETECTORS = _build_detector_registry()

def run_full_analysis(contract_path: str, run_ml: bool = True) -> dict[str, Any]:
    """Parse contract EXACTLY ONCE and run all static/hybrid detectors."""
    path = Path(contract_path)
    if not path.exists(): return {"error": f"File not found: {contract_path}"}

    try:
        print(f"[SCAN] Parsing contract: {contract_path}")
        slither = Slither(str(path), disable_color=True)
    except Exception as e:
        return {"error": f"Slither parse error: {e}"}

    all_results = []
    print(f"[ANALYSIS] Running {len(DETECTORS)} static detector(s)...")
    
    # Static Phase
    for detector in DETECTORS:
        try:
            all_results.extend(detector(slither))
        except Exception as e:
            print(f"[WARN] Detector '{detector.__name__}' failed: {e}")

    # ML Phase (Hybrid)
    if run_ml:
        try:
            from ml.ml_analyzer import analyze_with_ml
            all_results.extend(analyze_with_ml(slither))
        except Exception as e: 
            print(f"[WARN] ML Analysis failed or not configured: {e}")

    report = {
        "contract": path.name,
        "path": str(path.resolve()),
        "analyzed_at": datetime.now().isoformat(),
        "total_issues": len(all_results),
        "issues": all_results,
    }

    report_dir = Path("reports")
    report_dir.mkdir(exist_ok=True)
    with open(report_dir / f"{path.stem}_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)

    return report
