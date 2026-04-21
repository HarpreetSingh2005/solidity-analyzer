# detectors/reentrancy.py
"""
Detector: Reentrancy (Checks-Effects-Interactions Violation)
SWC-107  |  Severity: High

The Checks-Effects-Interactions (CEI) pattern requires that all state changes
happen BEFORE any external call.  If an external call is made while the
contract's state still reflects the "before" values, a malicious callee can
re-enter the same function (or another function that reads the same state)
before the update is committed — draining funds or corrupting state.

Detection strategy:
  For each public/external function, scan for an external call node followed
  by a state-variable write node that touches a variable already READ before
  the call.  This CEI-violation heuristic catches the classic withdraw-before-
  balance-update pattern with high precision.
"""
from __future__ import annotations

from slither import Slither
from slither.slithir.operations import HighLevelCall, LowLevelCall, Send, Transfer

_EXTERNAL_CALL_OPS = (HighLevelCall, LowLevelCall, Send, Transfer)


def detect_reentrancy(slither: Slither) -> list[dict]:
    """
    Flags functions where an external call precedes a state-variable write
    that touches a variable read before the call (CEI violation).
    """
    findings: list[dict] = []
    seen:     set[tuple] = set()

    for contract in slither.contracts:
        if contract.is_interface or contract.is_library:
            continue

        for function in contract.functions:
            if function.is_constructor:
                continue
            if function.visibility not in ("public", "external"):
                continue

            call_nodes         = []
            state_update_nodes = []

            for node in function.nodes:
                has_external_call = any(
                    isinstance(ir, _EXTERNAL_CALL_OPS)
                    for ir in node.irs
                )
                if has_external_call:
                    call_nodes.append(node)
                if node.state_variables_written:
                    state_update_nodes.append(node)

            for call_node in call_nodes:
                if not call_node.source_mapping:
                    continue
                call_line = call_node.source_mapping.lines[0]

                # Collect state variables read before this call
                vars_read_before: set = set()
                for node in function.nodes:
                    if node.source_mapping and node.source_mapping.lines[0] < call_line:
                        vars_read_before.update(node.state_variables_read)

                # Look for state writes that happen AFTER the call
                for update_node in state_update_nodes:
                    if not update_node.source_mapping:
                        continue
                    update_line = update_node.source_mapping.lines[0]
                    if update_line <= call_line:
                        continue

                    vulnerable = vars_read_before.intersection(
                        update_node.state_variables_written
                    )
                    if not vulnerable:
                        continue

                    key = (contract.name, function.name, call_line)
                    if key in seen:
                        break
                    seen.add(key)

                    var_names = ", ".join(v.name for v in vulnerable)
                    findings.append({
                        "vulnerability" : "Reentrancy (CEI Violation)",
                        "contract"      : contract.name,
                        "function"      : function.name,
                        "line"          : call_line,
                        "severity"      : "High",
                        "explanation"   : (
                            f"Function '{function.name}' makes an external call at line "
                            f"{call_line} before updating state variable(s) "
                            f"({var_names}) at line {update_line}. "
                            f"A malicious callee can re-enter this function before "
                            f"the state is updated, potentially draining funds."
                        ),
                        "suggested_fix" : (
                            f"Move all state updates (including setting {var_names} to "
                            f"their new values) to BEFORE the external call at line "
                            f"{call_line}. Alternatively, add a ReentrancyGuard "
                            f"(e.g., OpenZeppelin's nonReentrant modifier)."
                        ),
                    })
                    break  # one finding per call node

    return findings