# detectors/reentrancy.py
"""
Detector: Reentrancy (CEI Violation)
SWC-107  |  Severity: High

Reentrancy occurs when an external call is made to an untrusted contract
before resolving any effects (updating state variables). The untrusted
contract can callback into the vulnerable contract and re-execute logic
with an outdated state.

Detection strategy:
  Flags HighLevelCall, LowLevelCall, Send, and Transfer operations
  that are followed by state variable writes in the same function.
"""
from __future__ import annotations

from slither import Slither
from slither.slithir.operations import HighLevelCall, LowLevelCall, Send, Transfer


def detect_reentrancy(slither: Slither) -> list[dict]:
    """
    Flags Reentrancy (CEI Violation) using SlithIR analysis.
    """
    findings: list[dict] = []
    seen:     set[tuple] = set()

    for contract in slither.contracts:
        if contract.is_interface or contract.is_library:
            continue

        for func in contract.functions:
            if func.visibility not in ("public", "external"):
                continue
            
            calls = [n for n in func.nodes if any(isinstance(ir, (HighLevelCall, LowLevelCall, Send, Transfer)) for ir in n.irs)]
            for call in calls:
                line = call.source_mapping.lines[0] if call.source_mapping else "Unknown"
                
                # Check for state updates after the call
                if any(n.state_variables_written and n.source_mapping and n.source_mapping.lines[0] > line for n in func.nodes):
                    key = (contract.name, func.name, line)
                    if key in seen:
                        continue
                    seen.add(key)
                    findings.append({
                        "vulnerability": "Reentrancy (CEI Violation)",
                        "contract": contract.name,
                        "function": func.name,
                        "line": line,
                        "severity": "High",
                        "explanation": (
                            f"Function '{func.name}' makes an external call at line {line} "
                            f"before updating state variables. This violates the Checks-Effects-Interactions "
                            f"pattern and may allow an attacker to re-enter the contract."
                        ),
                        "suggested_fix": "Update all state variables before making external calls (Checks-Effects-Interactions) or add a ReentrancyGuard (e.g., nonReentrant modifier)."
                    })
    return findings