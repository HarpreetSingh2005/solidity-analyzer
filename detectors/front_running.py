# detectors/front_running.py
"""
Detector: Front-Running Vulnerability
Solidity SWC-114 (Transaction Order Dependence)

Front-running occurs when an attacker observes a pending transaction in the
mempool and submits a competing transaction with higher gas to get theirs
executed first — profiting from the information advantage.

This detector flags two well-known static patterns:
  1. ERC-20 Approve Race Condition: approve() + transferFrom() without
     increaseAllowance / decreaseAllowance guards.
  2. Timestamp + Payable functions where the outcome depends on block.timestamp,
     allowing miners to influence who wins a time-sensitive competition.
"""
from slither import Slither
from slither.slithir.operations import SolidityCall
from slither.core.declarations.solidity_variables import SolidityVariableComposed


def _uses_timestamp(function) -> bool:
    """Returns True if function reads block.timestamp in any node."""
    for node in function.nodes:
        for ir in node.irs:
            for var in getattr(ir, "read", []):
                if isinstance(var, SolidityVariableComposed):
                    if var.name in ("block.timestamp", "now"):
                        return True
    return False


def _is_approve_pattern(function) -> bool:
    """
    Returns True if the function looks like a classic ERC-20 approve().
    Heuristic: named 'approve', sets an allowance state variable, and is public/external.
    """
    fname = function.name.lower()
    return (
        "approve" in fname
        and function.visibility in ("public", "external")
        and len(function.all_state_variables_written()) > 0
    )


def detect_front_running(slither: Slither):
    """
    Flags two front-running patterns:
      - ERC-20 approve() race condition susceptibility
      - Payable functions whose outcome depends on block.timestamp
    Severity: Medium
    """
    findings = []
    seen = set()

    for contract in slither.contracts:
        if contract.is_interface or contract.is_library:
            continue

        for function in contract.functions:
            if function.is_constructor:
                continue

            key = (contract.name, function.name)
            if key in seen:
                continue

            # --- Pattern 1: ERC-20 Approve Race ---
            if _is_approve_pattern(function):
                # Check if the contract has a transferFrom — confirms ERC-20 context
                has_transfer_from = any(
                    f.name.lower() == "transferfrom"
                    for f in contract.functions
                )
                if has_transfer_from:
                    seen.add(key)
                    line = (
                        function.source_mapping.lines[0]
                        if function.source_mapping else "Unknown"
                    )
                    findings.append({
                        "vulnerability": "Front-Running: ERC-20 Approve Race",
                        "contract": contract.name,
                        "function": function.name,
                        "line": line,
                        "severity": "Medium",
                        "explanation": (
                            f"The '{function.name}' function sets a new allowance directly. "
                            "If an approved spender is watching the mempool, they can call "
                            "transferFrom() before the allowance update is mined, then again "
                            "after — effectively spending both the old and new allowance."
                        ),
                        "suggested_fix": (
                            "Replace direct approve() with increaseAllowance() / "
                            "decreaseAllowance() (OpenZeppelin pattern). Alternatively, "
                            "require the sender to set allowance to 0 before changing it: "
                            "require(currentAllowance == 0 || newAmount == 0)."
                        )
                    })
                    continue

            # --- Pattern 2: Timestamp-dependent Payable ---
            if function.payable and _uses_timestamp(function):
                seen.add(key)
                line = (
                    function.source_mapping.lines[0]
                    if function.source_mapping else "Unknown"
                )
                findings.append({
                    "vulnerability": "Front-Running: Timestamp-Dependent Payable",
                    "contract": contract.name,
                    "function": function.name,
                    "line": line,
                    "severity": "Medium",
                    "explanation": (
                        f"Payable function '{function.name}' uses block.timestamp to determine "
                        "outcome (e.g., auction deadlines, lottery windows). An attacker or "
                        "miner can observe this transaction and front-run it, or manipulate "
                        "the timestamp by ~15s to change which transaction wins."
                    ),
                    "suggested_fix": (
                        "Use a commit-reveal scheme to hide transaction intent until after "
                        "the block is committed. For auctions, consider a blind auction "
                        "pattern. Avoid using block.timestamp as the sole decider for "
                        "financial outcomes."
                    )
                })

    return findings
