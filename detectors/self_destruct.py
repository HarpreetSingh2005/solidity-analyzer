# detectors/self_destruct.py
from slither import Slither
from slither.slithir.operations import SolidityCall

def detect_self_destruct(slither: Slither):
    """
    Detects functions that allow anyone to trigger a selfdestruct operation.
    """
    findings = []
    
    for contract in slither.contracts:
        for function in contract.functions:
            # Check for selfdestruct in unprotected public/external functions
            if function.is_constructor or function.visibility not in ["public", "external"]:
                continue

            # Check for protection modifiers
            modifier_names = [mod.name.lower() for mod in function.modifiers]
            is_protected = any("onlyowner" in m or "onlyadmin" in m for m in modifier_names)

            if is_protected:
                continue

            for node in function.nodes:
                for ir in node.irs:
                    # Check for selfdestruct or suicide in various ways
                    is_sd = False
                    if isinstance(ir, SolidityCall) and ir.function.name in ["selfdestruct", "suicide"]:
                        is_sd = True
                    elif "selfdestruct" in str(ir).lower() or "suicide" in str(ir).lower():
                        # Fallback for different Slither versions or IR representations
                        is_sd = True
                    
                    if is_sd:
                        line = node.source_mapping.lines[0] if node.source_mapping else "Unknown"
                        findings.append({
                            "vulnerability": "Unprotected Self-Destruct",
                            "contract": contract.name,
                            "function": function.name,
                            "line": line,
                            "severity": "Critical",
                            "explanation": f"The function '{function.name}' contains a self-destruct operation at line {line} and lacks proper access control. Any external user can call this to destroy the contract.",
                            "suggested_fix": f"Restrict access to the function '{function.name}' using an 'onlyOwner' modifier or remove the self-destruct call."
                        })
                        break # Only one report per function node
    return findings
