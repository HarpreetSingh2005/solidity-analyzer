# detectors/access_control.py
"""
Detector: Missing Access Control on Privileged Variables
SWC-105  |  Severity: Critical

Functions that modify privileged state variables (e.g. owner, admin, authority)
must be restricted with an access-control modifier. Without it, any external
account can takeover the protocol by assigning themselves administrative roles.

Detection strategy:
  Flags public/external functions that modify state variables containing
  privileged keywords ("owner", "admin", etc.) without having an associated
  modifier like "onlyOwner".
"""
from __future__ import annotations

from slither import Slither


def detect_access_control(slither: Slither) -> list[dict]:
    """
    Flags functions modifying privileged state without access guards.
    """
    findings: list[dict] = []
    seen:     set[tuple] = set()
    privileged = ("owner", "admin", "authority", "governor", "operator")

    for contract in slither.contracts:
        if contract.is_interface or contract.is_library:
            continue

        p_vars = [v for v in contract.state_variables if v.name.lower() in privileged]
        if not p_vars:
            continue

        for func in contract.functions:
            if func.is_constructor or func.visibility in ("private", "internal"):
                continue

            # Check if function writes to any privileged variable
            if any(v in func.all_state_variables_written() for v in p_vars):
                # Check if function has an access control modifier
                if not any(m.name.lower() in ("onlyowner", "onlyadmin", "onlyrole") for m in func.modifiers):
                    line = func.source_mapping.lines[0] if func.source_mapping else "Unknown"
                    key = (contract.name, func.name, line)
                    
                    if key in seen:
                        continue
                    seen.add(key)
                    
                    findings.append({
                        "vulnerability": "Missing Access Control",
                        "contract": contract.name,
                        "function": func.name,
                        "line": line,
                        "severity": "Critical",
                        "explanation": (
                            f"Function '{func.name}' modifies a privileged variable at line {line} "
                            f"but lacks an access control modifier (e.g., onlyOwner). "
                            f"Any external caller can exploit this to seize control of the contract."
                        ),
                        "suggested_fix": "Add an 'onlyOwner', 'onlyAdmin', or equivalent modifier to restrict access to authorized users."
                    })

    return findings