# detectors/shadowed_variable.py
"""
Detector: State Variable Shadowing
SWC-119  |  Severity: Medium

When a child contract declares a state variable with the same name as a
variable in a parent contract, the parent's variable is "shadowed".
Developers may inadvertently read/write the wrong variable, leading to
logic errors, incorrect access-control checks, or funds being sent to an
unexpected address.

Detection strategy:
  For each contract, compare its own state variable names against all
  variables in its inheritance chain.  Report any name collision.
"""
from __future__ import annotations

from slither import Slither


def detect_shadowed_variables(slither: Slither) -> list[dict]:
    """
    Flags state variables in child contracts that shadow a variable with the
    same name in a parent contract.
    """
    findings: list[dict] = []
    seen:     set[tuple] = set()

    for contract in slither.contracts:
        if contract.is_interface or contract.is_library:
            continue
        if not contract.inheritance:
            continue

        # Variables declared directly in this contract (not inherited)
        own_vars = {
            var.name: var
            for var in contract.state_variables
            if var.contract == contract
        }

        for parent in contract.inheritance:
            parent_var_names = {v.name for v in parent.state_variables}

            for name, var in own_vars.items():
                if name not in parent_var_names:
                    continue

                key = (contract.name, parent.name, name)
                if key in seen:
                    continue
                seen.add(key)

                line = var.source_mapping.lines[0] if var.source_mapping else "Unknown"
                findings.append({
                    "vulnerability" : "State Variable Shadowing",
                    "contract"      : contract.name,
                    "function"      : "(state variable)",
                    "line"          : line,
                    "severity"      : "Medium",
                    "explanation"   : (
                        f"State variable '{name}' declared in contract '{contract.name}' "
                        f"at line {line} shadows a variable with the same name in parent "
                        f"contract '{parent.name}'. Code that reads '{name}' may "
                        f"accidentally operate on the wrong copy, causing logic errors or "
                        f"incorrect access-control outcomes."
                    ),
                    "suggested_fix" : (
                        f"Rename '{name}' in '{contract.name}' to a unique identifier "
                        f"(e.g., '_{name}' or '{contract.name.lower()}_{name}') to "
                        f"eliminate the ambiguity. If the intent is to override the "
                        f"parent's value, explicitly set it in the constructor instead "
                        f"of re-declaring it."
                    ),
                })

    return findings
