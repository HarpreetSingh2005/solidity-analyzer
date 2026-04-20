# detectors/access_control.py
from slither import Slither

def detect_access_control(slither: Slither):
    """
    Detects functions that modify sensitive state variables but lack access control.
    """
    findings = []
    # Common privileged variable names to look for
    SENSITIVE_VARS = ["owner", "admin", "governor", "authority"]

    for contract in slither.contracts:
        # Get all state variables in this contract that match sensitive names
        privileged_vars = [v for v in contract.state_variables if v.name.lower() in SENSITIVE_VARS]
        
        if not privileged_vars:
            continue

        for function in contract.functions:
            # Skip constructor, private, internal, or view/pure functions
            if function.is_constructor or function.visibility in ["private", "internal", "view", "pure"]:
                continue

            # Check if function writes to a privileged variable
            writes_to_privileged = False
            target_var = ""
            for node in function.nodes:
                written_vars = [var.name for var in node.state_variables_written if var in privileged_vars]
                if written_vars:
                    writes_to_privileged = True
                    target_var = written_vars[0]
                    break

            if not writes_to_privileged:
                continue

            # Check for protection modifiers
            modifier_names = [mod.name.lower() for mod in function.modifiers]
            is_protected = any("onlyowner" in m or "onlyadmin" in m or "onlyrole" in m or "authorized" in m for m in modifier_names)

            # Also check for explicit msg.sender checks in the function body
            has_require_check = False
            for node in function.nodes:
                for ir in node.irs:
                    # Look for require/assert/if logic involving msg.sender
                    ir_str = str(ir).lower()
                    if "msg.sender" in ir_str and ("require" in ir_str or "revert" in ir_str):
                        has_require_check = True
                        break

            if not is_protected and not has_require_check:
                line = function.nodes[0].source_mapping.lines[0] if function.nodes else "Unknown"
                findings.append({
                    "vulnerability": "Missing Access Control",
                    "contract": contract.name,
                    "function": function.name,
                    "line": line,
                    "severity": "Critical",
                    "explanation": f"The function '{function.name}' updates the sensitive variable '{target_var}' but does not seem to have any access control (like onlyOwner). This allows any external actor to take control of the contract.",
                    "suggested_fix": f"Add an access control modifier (e.g., 'onlyOwner') to the function '{function.name}' at line {line}."
                })
                
    return findings