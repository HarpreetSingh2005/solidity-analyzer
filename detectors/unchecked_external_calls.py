# detectors/unchecked_external_calls.py
from slither import Slither
from slither.slithir.operations import LowLevelCall

def detect_unchecked_external_calls(slither: Slither):
    """
    Detects low-level calls (call, delegatecall, staticcall) where the return value is not checked.
    """
    findings = []
    
    for contract in slither.contracts:
        for function in contract.functions:
            for node in function.nodes:
                for ir in node.irs:
                    if isinstance(ir, LowLevelCall):
                        # Slither's ir.lvalue is the variable that captures the return value.
                        # If it's None, it means the return value of the low-level call is ignored.
                        if ir.lvalue is None:
                            line = node.source_mapping.lines[0] if node.source_mapping else "Unknown"
                            findings.append({
                                "vulnerability": "Unchecked External Call",
                                "contract": contract.name,
                                "function": function.name,
                                "line": line,
                                "severity": "Medium",
                                "explanation": f"The low-level call in function '{function.name}' at line {line} does not check the success return value. If the call fails, the execution will continue silently, potentially leading to inconsistent state.",
                                "suggested_fix": f"Assign the return value to a boolean and check it: '(bool success, ) = target.call(...)'; 'require(success, \"Call failed\");'."
                            })
    return findings
