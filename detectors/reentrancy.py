# detectors/reentrancy.py
from slither.slithir.operations import HighLevelCall, LowLevelCall, Send, Transfer

def detect_reentrancy(slither):
    """Flags Reentrancy (CEI Violation) using SlithIR analysis."""
    findings = []
    seen = set()
    for contract in slither.contracts:
        if contract.is_interface or contract.is_library: continue
        for func in contract.functions:
            if func.visibility not in ["public", "external"]: continue
            
            calls = [n for n in func.nodes if any(isinstance(ir, (HighLevelCall, LowLevelCall, Send, Transfer)) for ir in n.irs)]
            for call in calls:
                line = call.source_mapping.lines[0]
                # Check for state updates after the call
                if any(n.state_variables_written and n.source_mapping.lines[0] > line for n in func.nodes):
                    key = (contract.name, func.name, line)
                    if key in seen: continue
                    seen.add(key)
                    findings.append({
                        "vulnerability": "Reentrancy (CEI Violation)",
                        "contract": contract.name,
                        "function": func.name,
                        "line": line,
                        "severity": "High",
                        "explanation": "External call made before updating state variables.",
                        "suggested_fix": "Update all state variables before making external calls (Checks-Effects-Interactions)."
                    })
    return findings