# core/analyzer.py
"""
SESA — Solidity Explainable Static Analyzer
============================================
Core orchestrator.  Slither is initialised **exactly once** here and the
resulting object is passed to every detector.  This file owns:

  • Detector auto-discovery (all detect_* functions in detectors/)
  • Phase 1 — static detector execution
  • Phase 2 — optional ML semantic layer
  • JSON report serialisation to reports/

Finding schema (every detector must return a list of dicts with these keys):
  {
      "vulnerability" : str   — short, human-readable name
      "contract"      : str   — Solidity contract name
      "function"      : str   — function name or "(state variable)"
      "line"          : int   — source line number (or "Unknown")
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


# ── Detector Auto-Discovery ───────────────────────────────────────────────────

def _build_detector_registry() -> list:
    """
    Scans detectors/ for any callable whose name starts with 'detect_'.
    Adding a new detector requires only dropping a .py file there — no changes
    to this file are needed.
    """
    registry: list = []
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
        except Exception as exc:
            print(f"[WARN] Could not load detector module '{module_name}': {exc}")

    return registry


DETECTORS: list = _build_detector_registry()


# ── Main Entry Point ──────────────────────────────────────────────────────────

def run_full_analysis(contract_path: str, run_ml: bool = True) -> dict[str, Any]:
    """
    Parse the Solidity contract **once** with Slither and run all registered
    detectors, followed by an optional ML layer.

    Returns a report dict:
    {
        "contract"     : filename,
        "path"         : absolute path (string),
        "analyzed_at"  : ISO-8601 timestamp,
        "total_issues" : int,
        "issues"       : [... finding dicts ...]
    }
    On hard failure returns {"error": "message"}.
    """
    path = Path(contract_path)

    if not path.exists():
        return {"error": f"File not found: {contract_path}"}

    try:
        print(f"[SCAN]     Parsing contract  : {contract_path}")
        slither = Slither(str(path), disable_color=True)
    except Exception as exc:
        print(f"[ERROR]    Slither failed to parse '{contract_path}': {exc}")
        return {"error": f"Slither parse error: {exc}"}

    all_results: list[dict] = []

    # ── Phase 1: Static Detectors ─────────────────────────────────────────────
    print(f"[ANALYSIS] Running {len(DETECTORS)} static detector(s)...")
    for detector in DETECTORS:
        try:
            findings = detector(slither)
            all_results.extend(findings)
        except Exception as exc:
            print(f"[WARN]     Detector '{detector.__name__}' failed: {exc}")

    # ── Phase 2: ML Semantic Layer (optional) ─────────────────────────────────
    if run_ml:
        try:
            from ml.ml_analyzer import analyze_with_ml  # lazy import — optional dep
            ml_results = analyze_with_ml(slither)
            all_results.extend(ml_results)
        except ImportError:
            print("[INFO]     ML module not found — skipping Phase 2.")
        except Exception as exc:
            print(f"[WARN]     ML analysis skipped due to error: {exc}")
            print("[WARN]     Static results are unaffected.")

    # ── Build Report ──────────────────────────────────────────────────────────
    report: dict[str, Any] = {
        "contract"     : path.name,
        "path"         : str(path.resolve()),
        "analyzed_at"  : datetime.now().isoformat(),
        "total_issues" : len(all_results),
        "issues"       : all_results,
    }

    # ── Persist JSON ──────────────────────────────────────────────────────────
    report_dir = Path("reports")
    report_dir.mkdir(exist_ok=True)
    output_file = report_dir / f"{path.stem}_report.json"

    with open(output_file, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=4, ensure_ascii=False)

    phase_tag = "Static + AI" if run_ml else "Static Only"
    print(
        f"[SUCCESS]  {len(all_results)} finding(s) found [{phase_tag}]"
        f" — report saved to '{output_file}'"
    )
    return report