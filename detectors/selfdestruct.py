# detectors/selfdestruct.py
from slither import Slither
from slither.slithir.operations import SolidityCall

def detect_unprotected_selfdestruct(slither: Slither):
    findings = []
    
    for contract in slither.contracts:
        for function in contract.functions:
            if function.is_constructor or function.visibility not in ["public", "external"]:
                continue

            # Check if the function has an access control modifier
            modifier_names = [mod.name.lower() for mod in function.modifiers]
            is_protected = any("onlyowner" in m or "onlyadmin" in m for m in modifier_names)

            if is_protected:
                continue

            for node in function.nodes:
                for ir in node.irs:
                    # THE FIX: Check if it's a SolidityCall and the function is 'selfdestruct'
                    if isinstance(ir, SolidityCall) and ir.function.name == "selfdestruct":
                        line = node.source_mapping.lines[0] if node.source_mapping else "Unknown"
                        findings.append({
                            "vulnerability": "Unprotected Self-Destruct",
                            "contract": contract.name,
                            "function": function.name,
                            "line": line,
                            "severity": "Critical",
                            "explanation": f"Anyone can call selfdestruct at line {line}, destroying the contract and forcibly sending its balance to the attacker.",
                            "suggested_fix": "Add an onlyOwner modifier to this function.",
                            "used_features": "node.irs + SolidityCall operation"
                        })
    return findings