# detectors/access_control.py
def detect_access_control(slither):
    """Flags functions modifying privileged state without access guards."""
    findings = []
    privileged = ["owner", "admin", "authority", "governor", "operator"]
    for contract in slither.contracts:
        if contract.is_interface or contract.is_library: continue
        p_vars = [v for v in contract.state_variables if v.name.lower() in privileged]
        for func in contract.functions:
            if func.visibility in ["private", "internal"] or func.is_constructor: continue
            if any(v in func.all_state_variables_written() for v in p_vars):
                if not any(m.name.lower() in ["onlyowner", "onlyadmin", "onlyrole"] for m in func.modifiers):
                    findings.append({
                        "vulnerability": "Missing Access Control",
                        "contract": contract.name,
                        "function": func.name,
                        "line": func.source_mapping.lines[0],
                        "severity": "Critical",
                        "explanation": "Privileged variable modified without owner/admin check.",
                        "suggested_fix": "Add an 'onlyOwner' modifier or require(msg.sender == ...) check."
                    })
    return findings