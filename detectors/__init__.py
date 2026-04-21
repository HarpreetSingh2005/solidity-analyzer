# detectors/__init__.py
"""
detectors/
==========
Static vulnerability detector plugins for SESA.

Each module exposes one or more functions named detect_*() that accept a
Slither instance and return a list of finding dicts conforming to the
project-wide schema:

    {
        "vulnerability" : str   — short human-readable name
        "contract"      : str   — Solidity contract name
        "function"      : str   — function name or "(state variable)"
        "line"          : int   — source line (or "Unknown")
        "severity"      : str   — Critical | High | Medium | Low
        "explanation"   : str   — full human-readable explanation
        "suggested_fix" : str   — actionable remediation advice
    }

Adding a new detector:
  1. Create detectors/my_detector.py
  2. Define def detect_<name>(slither: Slither) -> list: returning findings
  3. Done — core/analyzer.py auto-discovers it via the _build_detector_registry()
     function.  No changes to any other file are needed.
"""
