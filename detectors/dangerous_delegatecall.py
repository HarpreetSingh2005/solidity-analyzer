# detectors/dangerous_delegatecall.py
"""
Detector: Delegatecall to Untrusted / Dynamic Address
Solidity SWC-112

delegatecall() executes code from another contract but in the CALLER's storage
context. If the target address is user-controlled, attacker-supplied, or stored
in a mutable state variable (not an immutable/constant), an attacker can
supply a malicious contract that wipes or corrupts the caller's storage,
drains ETH, or takes ownership.
"""
from slither import Slither
from slither.slithir.operations import LowLevelCall
from slither.core.declarations import (
    Contract,
    SolidityVariableComposed,
)
from slither.core.variables.state_variable import StateVariable
from slither.core.variables.local_variable import LocalVariable


def _is_safe_address(destination) -> bool:
    """
    Returns True if the delegatecall destination is provably safe
    (hardcoded constant/immutable state variable).
    """
    if destination is None:
        return False

    # If it's a StateVariable that is constant or immutable → safe
    if isinstance(destination, StateVariable):
        return destination.is_constant or destination.is_immutable

    return False


def detect_dangerous_delegatecall(slither: Slither):
    """
    Detects low-level delegatecall() calls where the target address is not a
    hardcoded constant/immutable — i.e., it could be influenced by user input
    or a mutable state variable.
    Severity: Critical
    """
    findings = []
    seen = set()

    for contract in slither.contracts:
        if contract.is_interface or contract.is_library:
            continue

        for function in contract.functions + list(contract.modifiers):
            for node in function.nodes:
                for ir in node.irs:
                    if not isinstance(ir, LowLevelCall):
                        continue
                    if ir.function_name != "delegatecall":
                        continue

                    destination = ir.destination
                    key = (contract.name, function.name, str(destination))

                    if key in seen:
                        continue
                    seen.add(key)

                    if _is_safe_address(destination):
                        continue  # Fixed address — not dangerous

                    line = node.source_mapping.lines[0] if node.source_mapping else "Unknown"
                    dest_desc = str(destination) if destination else "unknown address"

                    findings.append({
                        "vulnerability": "Dangerous Delegatecall",
                        "contract": contract.name,
                        "function": function.name,
                        "line": line,
                        "severity": "Critical",
                        "explanation": (
                            f"Function '{function.name}' performs a delegatecall to a non-constant "
                            f"address ('{dest_desc}') at line {line}. delegatecall executes foreign "
                            f"bytecode inside this contract's own storage context. If the destination "
                            f"is user-controlled or can be changed by an attacker, they can destroy "
                            f"storage, steal ownership, or drain funds."
                        ),
                        "suggested_fix": (
                            "Ensure the delegatecall target is a hardcoded constant or an immutable "
                            "variable set only in the constructor. Never delegatecall to an address "
                            "supplied by msg.sender or stored in a mutable state variable. "
                            "Consider using OpenZeppelin's upgradeable proxy patterns which enforce "
                            "these constraints."
                        )
                    })

    return findings
