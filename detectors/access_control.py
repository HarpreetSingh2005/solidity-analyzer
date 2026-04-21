# detectors/access_control.py
"""
Detector: Missing Access Control on Privileged Operations
SWC-105  |  Severity: Critical

Functions that write to ownership/admin state variables (owner, admin,
governor, etc.) or perform privileged actions (pause, upgrade, etc.) must
be protected by an explicit access control mechanism — a modifier like
onlyOwner, or an inline require(msg.sender == owner) check.  When such
protection is absent, ANY external address can take over or disrupt the
contract.

Detection strategy:
  1. Identify state variables with privileged names (owner, admin, …).
  2. Find public/external functions that write to those variables.
  3. Flag functions that have neither a recognised access modifier NOR an
     inline msg.sender comparison.
"""
from __future__ import annotations

from slither import Slither

# Variable names that indicate privileged/ownership state
_PRIVILEGED_NAMES: frozenset[str] = frozenset({
    "owner", "admin", "governor", "authority", "operator",
    "controller", "superuser", "multisig",
})

# Substrings that indicate an access-control modifier
_ACCESS_MOD_KEYWORDS: tuple[str, ...] = (
    "onlyowner", "onlyadmin", "onlyrole", "authorized",
    "onlygovernor", "onlyoperator", "onlycontroller",
)


def detect_access_control(slither: Slither) -> list[dict]:
    """
    Flags public/external functions that modify a privileged state variable
    without any access-control guard.
    """
    findings: list[dict] = []
    seen:     set[tuple] = set()

    for contract in slither.contracts:
        if contract.is_interface or contract.is_library:
            continue

        # Collect privileged state variables defined in this contract
        privileged_vars = [
            v for v in contract.state_variables
            if v.name.lower() in _PRIVILEGED_NAMES
        ]
        if not privileged_vars:
            continue

        for function in contract.functions:
            if function.is_constructor:
                continue
            if function.visibility in ("private", "internal"):
                continue

            key = (contract.name, function.name)
            if key in seen:
                continue

            # Check if function writes to any privileged variable
            target_var = _writes_privileged(function, privileged_vars)
            if target_var is None:
                continue

            # Check for modifier-based guard
            mod_names = [m.name.lower() for m in function.modifiers]
            is_modifier_protected = any(
                kw in m for m in mod_names for kw in _ACCESS_MOD_KEYWORDS
            )

            # Check for inline require/revert involving msg.sender
            is_inline_protected = _has_sender_check(function)

            if is_modifier_protected or is_inline_protected:
                continue

            seen.add(key)
            line = _first_line(function)
            findings.append({
                "vulnerability" : "Missing Access Control",
                "contract"      : contract.name,
                "function"      : function.name,
                "line"          : line,
                "severity"      : "Critical",
                "explanation"   : (
                    f"Function '{function.name}' modifies the privileged state "
                    f"variable '{target_var}' but has no access-control guard "
                    f"(no onlyOwner modifier, no require(msg.sender == ...) check). "
                    f"Any external address can call this function and take control "
                    f"of the contract."
                ),
                "suggested_fix" : (
                    f"Add an access control modifier to '{function.name}' — e.g., "
                    f"'modifier onlyOwner {{ require(msg.sender == owner, "
                    f"\"Not owner\"); _; }}' — or add "
                    f"'require(msg.sender == owner, \"Not owner\");' at the start "
                    f"of the function body."
                ),
            })

    return findings


# ── Helpers ───────────────────────────────────────────────────────────────────

def _writes_privileged(function, privileged_vars: list) -> str | None:
    """Return the name of the first privileged var written, or None."""
    for node in function.nodes:
        for var in node.state_variables_written:
            if var in privileged_vars:
                return var.name
    return None


def _has_sender_check(function) -> bool:
    """True if any IR node contains a msg.sender comparison in require/revert."""
    for node in function.nodes:
        for ir in node.irs:
            ir_str = str(ir).lower()
            if "msg.sender" in ir_str and any(
                kw in ir_str for kw in ("require", "revert", "assert")
            ):
                return True
    return False


def _first_line(function) -> int | str:
    """Return the first source line of a function, or 'Unknown'."""
    if function.nodes and function.nodes[0].source_mapping:
        return function.nodes[0].source_mapping.lines[0]
    if function.source_mapping:
        return function.source_mapping.lines[0]
    return "Unknown"