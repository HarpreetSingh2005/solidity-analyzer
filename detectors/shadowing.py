# detectors/shadowing.py
from slither import Slither

def detect_state_variable_shadowing(slither: Slither):
    findings = []
    
    for contract in slither.contracts:
        # If the contract doesn't inherit from anything, it can't shadow
        if not contract.inheritance:
            continue

        # Get all state variables declared in THIS specific contract
        current_vars = {var.name for var in contract.state_variables}

        # Check all parent contracts
        for parent in contract.inheritance:
            parent_vars = {var.name for var in parent.state_variables}
            
            # Find the intersection (variables that exist in both)
            shadowed = current_vars.intersection(parent_vars)
            
            if shadowed:
                findings.append({
                    "vulnerability": "State Variable Shadowing",
                    "contract": contract.name,
                    "function": "N/A (Contract Level)",
                    "line": contract.source_mapping.lines[0] if contract.source_mapping else "Unknown",
                    "severity": "Medium",
                    "explanation": f"This contract shadows state variables from its parent ({parent.name}): {', '.join(shadowed)}. Updates to these variables will modify the child's copy, not the parent's storage slot.",
                    "suggested_fix": f"Rename the variables in {contract.name} to avoid conflicting with {parent.name}.",
                    "used_features": "contract.inheritance + state_variables"
                })
    return findings