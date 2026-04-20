# detectors/tx_origin.py
from slither import Slither

def detect_tx_origin_phishing(slither: Slither):
    """
    Detects use of tx.origin for authentication, which is vulnerable to phishing attacks.
    """
    findings = []
    
    for contract in slither.contracts:
        for function in contract.functions:
            # Skip constructor as tx.origin is usually fine there
            if function.is_constructor or function.visibility not in ["public", "external"]:
                continue

            for node in function.nodes:
                # Check for tx.origin in IR operations
                for ir in node.irs:
                    if "tx.origin" in str(ir):
                        # check if it is part of a conditional check
                        is_auth_check = any(keyword in str(node).lower() for keyword in ["require", "if", "assert", "revert"])
                        
                        if is_auth_check:
                            line = node.source_mapping.lines[0] if node.source_mapping else "Unknown"
                            findings.append({
                                "vulnerability": "Vulnerable use of tx.origin",
                                "contract": contract.name,
                                "function": function.name,
                                "line": line,
                                "severity": "High",
                                "explanation": f"The function '{function.name}' uses 'tx.origin' for authorization at line {line}. This makes the contract vulnerable to phishing attacks where an attacker can trick a user into calling a malicious contract that then calls this function.",
                                "suggested_fix": f"Replace 'tx.origin' with 'msg.sender' in function '{function.name}' to ensure only the immediate caller is authenticated."
                            })
                            break
    return findings