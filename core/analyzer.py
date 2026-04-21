# core/analyzer.py
from slither import Slither
from pathlib import Path
import json
import importlib
import inspect
from datetime import datetime

from ml.ml_analyzer import analyze_with_ml

# ── Detector Registry (Auto-Discovery) ────────────────────────────────────────
# Scans the detectors/ package for any callable whose name starts with 'detect_'.
# To add a new detector: just drop a new .py file in detectors/ — nothing else
# needs to change.

def _build_detector_registry() -> list:
    """Dynamically loads all detect_* functions from the detectors/ package."""
    registry = []
    detectors_dir = Path(__file__).parent.parent / "detectors"

    for module_path in sorted(detectors_dir.glob("*.py")):
        if module_path.name.startswith("_"):
            continue  # skip __init__.py etc.
        module_name = f"detectors.{module_path.stem}"
        try:
            module = importlib.import_module(module_name)
            for name, obj in inspect.getmembers(module, inspect.isfunction):
                if name.startswith("detect_") and obj.__module__ == module_name:
                    registry.append(obj)
        except Exception as e:
            print(f"[WARN] Could not load detector module '{module_name}': {e}")

    return registry

DETECTORS = _build_detector_registry()

def run_full_analysis(contract_path: str, run_ml: bool = True):
    """
    Parses the contract ONCE using Slither and runs all security detectors.
    This architecture ensures maintainability and efficiency.
    """
    try:
        if not Path(contract_path).exists():
            return {"error": f"File not found: {contract_path}"}

        print(f"[SCAN] Parsing contract: {contract_path}")
        # Initialize Slither only once
        slither = Slither(contract_path, disable_color=True)

        all_results = []

        # Run Phase 1: Auto-discovered detector registry
        print(f"[ANALYSIS] Running {len(DETECTORS)} Vulnerability Detectors...")
        for detector in DETECTORS:
            try:
                all_results.extend(detector(slither))
            except Exception as e:
                print(f"[WARN] Detector '{detector.__name__}' failed: {e}")

        # Run Phase 2: ML Analysis (Optional — isolated so failures never kill static results)
        if run_ml:
            try:
                ml_results = analyze_with_ml(slither)
                all_results.extend(ml_results)
            except Exception as e:
                print(f"[WARNING] ML analysis skipped due to error: {e}")
                print("[WARNING] Static results are unaffected and have been saved.")

        # Prepare the report
        report = {
            "contract": Path(contract_path).name,
            "analyzed_at": datetime.now().isoformat(),
            "total_issues": len(all_results),
            "issues": all_results
        }

        # Ensure reports directory exists
        report_dir = Path("reports")
        report_dir.mkdir(exist_ok=True)
        
        output_file = report_dir / f"{Path(contract_path).stem}_report.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4, ensure_ascii=False)

        print(f"[SUCCESS] Analysis complete! {len(all_results)} findings saved to {output_file}")
        return report

    except Exception as e:
        print(f"[ERROR] Error analyzing {contract_path}: {e}")
        return {"error": str(e)}