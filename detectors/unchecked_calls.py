# detectors/unchecked_calls.py
from slither import Slither
from slither.slithir.operations import LowLevelCall

def detect_unchecked_calls(slither: Slither):
    findings = []
    
    for contract in slither.contracts:
        for function in contract.functions:
            if function.is_constructor or function.visibility not in ["public", "external"]:
                continue

            for node in function.nodes:
                # 1. Find all Low Level Calls (e.g., .call(), .delegatecall())
                for ir in node.irs:
                    if isinstance(ir, LowLevelCall):
                        # LowLevelCall returns a tuple. The first item is the 'success' bool.
                        # Slither tracks if this return value is used.
                        if ir.lvalue is None:
                            # If lvalue (left-hand value) is None, the return value was completely discarded!
                            line = node.source_mapping.lines[0] if node.source_mapping else "Unknown"
                            
                            findings.append({
                                "vulnerability": "Unchecked External Call (SC06)",
                                "contract": contract.name,
                                "function": function.name,
                                "line": line,
                                "severity": "Medium",
                                "explanation": f"Low-level call at line {line} does not check the return value (success/failure). If the call fails silently, the contract will continue executing with an incorrect state.",
                                "suggested_fix": f"Assign the call to a variable (e.g., (bool success, ) = target.call(...)) and add a require(success) statement.",
                                "used_features": "node.irs + LowLevelCall.lvalue check"
                            })
    return findings