# detectors/dangerous_delegatecall.py
"""
Detector: Delegatecall to Untrusted / Dynamic Address
SWC-112  |  Severity: Critical

delegatecall() executes code from another contract but in the CALLER'S
storage context. If the target address is user-controlled, stored in a
mutable state variable, or derived from function arguments, an attacker can
supply a malicious contract that:
  - Wipes or corrupts the caller's storage layout
  - Resets the owner variable to the attacker's address
  - Drains all ETH from the contract

Safe delegatecall targets are constants or immutables set once at
construction time and never changed.

Detection strategy:
  Inspect all LowLevelCall IR operations where function_name == 'delegatecall'.
  If the destination is not a StateVariable marked constant/immutable, flag it.
"""
from __future__ import annotations

from slither import Slither
from slither.slithir.operations import LowLevelCall
from slither.core.variables.state_variable import StateVariable


def _is_safe_address(destination) -> bool:
    """Return True only if destination is a constant or immutable state variable."""
    if isinstance(destination, StateVariable):
        return destination.is_constant or destination.is_immutable
    return False


def detect_dangerous_delegatecall(slither: Slither) -> list[dict]:
    """
    Flags delegatecall() calls where the target address is not provably safe
    (i.e., not a constant/immutable state variable).
    """
    findings: list[dict] = []
    seen:     set[tuple] = set()

    for contract in slither.contracts:
        if contract.is_interface or contract.is_library:
            continue

        for function in list(contract.functions) + list(contract.modifiers):
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
                        continue  # constant/immutable address — safe

                    line      = node.source_mapping.lines[0] if node.source_mapping else "Unknown"
                    dest_desc = str(destination) if destination else "unknown address"

                    findings.append({
                        "vulnerability" : "Dangerous Delegatecall",
                        "contract"      : contract.name,
                        "function"      : function.name,
                        "line"          : line,
                        "severity"      : "Critical",
                        "explanation"   : (
                            f"Function '{function.name}' performs a delegatecall to a "
                            f"non-constant address ('{dest_desc}') at line {line}. "
                            f"delegatecall executes foreign bytecode inside this "
                            f"contract's own storage context. If the destination is "
                            f"user-controlled or mutable, an attacker can corrupt "
                            f"storage, steal ownership, or drain funds."
                        ),
                        "suggested_fix" : (
                            "Ensure the delegatecall target is a 'constant' or "
                            "'immutable' address set only in the constructor. Never "
                            "delegatecall to an address passed as a parameter or "
                            "stored in a mutable state variable. Prefer OpenZeppelin's "
                            "upgradeable proxy patterns which enforce these constraints."
                        ),
                    })

    return findings
