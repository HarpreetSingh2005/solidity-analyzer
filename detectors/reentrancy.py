# detectors/reentrancy.py

from __future__ import annotations

from slither import Slither
from slither.slithir.operations import HighLevelCall, LowLevelCall, Send, Transfer


def detect_reentrancy(slither: Slither) -> list[dict]:
    """
    Detector: Reentrancy (CEI Violation)
    Flags external calls made before state variables are written.
    """
    findings = []
    seen = set()

    for contract in slither.contracts:
        if contract.is_interface or contract.is_library:
            continue

        for func in contract.functions:
            if func.is_constructor or func.view or func.pure:
                continue

            calls = [n for n in func.nodes if any(isinstance(ir, (HighLevelCall, LowLevelCall, Send, Transfer)) for ir in n.irs)]
            for call in calls:
                line = call.source_mapping.lines[0] if call.source_mapping and call.source_mapping.lines else "Unknown"
                
                # Check for state updates after the call
                call_line_int = line if isinstance(line, int) else 0
                if any(n.state_variables_written and n.source_mapping and n.source_mapping.lines and n.source_mapping.lines[0] > call_line_int for n in func.nodes):
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
                        "explanation": f"Function '{func.name}' makes an external call before updating all state variables. A malicious contract can reenter this function and exploit the stale state.",
                        "suggested_fix": "Follow the Checks-Effects-Interactions (CEI) pattern: move all state variable updates BEFORE the external call, or use a ReentrancyGuard modifier."
                    })
    return findings
