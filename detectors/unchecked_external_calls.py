# detectors/unchecked_external_calls.py
"""
Detector: Unchecked Low-Level Call Return Value
SWC-104  |  Severity: Medium

Low-level calls — address.call(), address.delegatecall(),
address.staticcall() — return a boolean indicating success.  Unlike
high-level calls, they do NOT revert on failure.  If the return value is
discarded (lvalue is None in SlithIR), the contract silently continues
execution even if the call failed, leading to inconsistent state or lost
funds.

Detection strategy:
  Walk all LowLevelCall IR operations.  If ir.lvalue is None, the return
  value is ignored — flag it.  Deduplicate to one finding per call site.
"""
from __future__ import annotations

from slither import Slither
from slither.slithir.operations import LowLevelCall


def detect_unchecked_external_calls(slither: Slither) -> list[dict]:
    """
    Flags low-level calls whose boolean return value is not captured.
    """
    findings: list[dict] = []
    seen:     set[tuple] = set()

    for contract in slither.contracts:
        if contract.is_interface or contract.is_library:
            continue

        for function in contract.functions:
            for node in function.nodes:
                for ir in node.irs:
                    if not isinstance(ir, LowLevelCall):
                        continue
                    if ir.lvalue is not None:
                        continue  # return value IS captured — safe

                    line = node.source_mapping.lines[0] if node.source_mapping else "Unknown"
                    key  = (contract.name, function.name, line)
                    if key in seen:
                        continue
                    seen.add(key)

                    call_name = getattr(ir, "function_name", "call")
                    findings.append({
                        "vulnerability" : "Unchecked Low-Level Call",
                        "contract"      : contract.name,
                        "function"      : function.name,
                        "line"          : line,
                        "severity"      : "Medium",
                        "explanation"   : (
                            f"The low-level '{call_name}' in function '{function.name}' "
                            f"at line {line} does not check the boolean return value. "
                            f"If the call fails (e.g., out-of-gas, reverted callee), "
                            f"execution continues silently, leaving the contract in an "
                            f"inconsistent state or silently losing funds."
                        ),
                        "suggested_fix" : (
                            "Capture and check the return value: "
                            "'(bool success, bytes memory data) = target.call{...}(payload); "
                            "require(success, \"Low-level call failed\");'. "
                            "Alternatively, prefer high-level calls to interfaces "
                            "(which revert automatically on failure)."
                        ),
                    })

    return findings
