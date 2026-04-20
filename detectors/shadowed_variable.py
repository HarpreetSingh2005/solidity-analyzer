# detectors/shadowed_variable.py
from slither import Slither

def detect_shadowed_variables(slither: Slither):
    """
    Detects state variables that shadow (have the same name as) variables in parent contracts.
    """
    findings = []
    
    for contract in slither.contracts:
        # State variables declared in the current contract
        current_vars = {var.name: var for var in contract.state_variables if var.contract == contract}

        # Check all parent contracts (inherited contracts)
        for parent in contract.inheritance:
            parent_vars = {var.name: var for var in parent.state_variables}
            
            # Find intersection of variable names
            shadowed_names = set(current_vars.keys()).intersection(set(parent_vars.keys()))
            
            for name in shadowed_names:
                var = current_vars[name]
                line = var.source_mapping.lines[0] if var.source_mapping else "Unknown"
                
                findings.append({
                    "vulnerability": "State Variable Shadowing",
                    "contract": contract.name,
                    "function": "N/A (State Variable)",
                    "line": line,
                    "severity": "Medium",
                    "explanation": f"The state variable '{name}' in contract '{contract.name}' shadows a variable with the same name in the parent contract '{parent.name}'. This can lead to confusion and unintended behavior when accessing the variable.",
                    "suggested_fix": f"Rename the state variable '{name}' in contract '{contract.name}' at line {line} to avoid shadowing the parent variable."
                })
                
    return findings
