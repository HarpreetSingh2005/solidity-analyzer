# core/analyzer.py
from __future__ import annotations
import importlib
import inspect
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from slither import Slither

def _build_detector_registry() -> list:
    registry = []
    detectors_dir = Path(__file__).parent.parent / "detectors"
    for module_path in sorted(detectors_dir.glob("*.py")):
        if module_path.name.startswith("_"): 
            continue
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

def run_full_analysis(contract_path: str, run_ml: bool = False) -> dict[str, Any]:
    """Parse contract ONCE and run static + optional ML analysis."""
    path = Path(contract_path)
    if not path.exists():
        return {"error": f"File not found: {contract_path}"}

    try:
        print(f"[SCAN] Parsing contract: {contract_path}")
        slither = Slither(str(path), disable_color=True)
    except Exception as e:
        return {"error": f"Slither parse error: {e}"}

    all_results = []
    print(f"[ANALYSIS] Running {len(DETECTORS)} static detector(s)...")

    # Static detectors
    for detector in DETECTORS:
        try:
            all_results.extend(detector(slither))
        except Exception as e:
            print(f"[WARN] Detector '{detector.__name__}' failed: {e}")

    # ML Phase (Hybrid)
    if run_ml:
        print("[ML] Running ML semantic analysis...")
        try:
            from ml.ml_analyzer import analyze_with_ml
            ml_findings = analyze_with_ml(slither)
            all_results.extend(ml_findings)
        except Exception as e:
            print(f"[WARN] ML analysis failed: {e}")

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