# detectors/front_running.py
"""
Detector: Front-Running Vulnerability
SWC-114  |  Severity: Medium

Front-running occurs when an attacker observes a pending transaction in the
mempool and submits a competing transaction with higher gas, getting theirs
executed first to exploit the information advantage.

This detector flags two well-known static patterns:

  1. ERC-20 Approve Race Condition
     A direct approve() call lets a watcher call transferFrom() with the OLD
     allowance right before the update, then AGAIN with the NEW allowance —
     effectively spending both.  The mitigation is increaseAllowance() /
     decreaseAllowance() or a "zero first" pattern.

  2. Timestamp-Dependent Payable
     A payable function whose outcome depends on block.timestamp allows a
     miner or MEV bot to manipulate the timestamp by ~15 s to choose who
     "wins" a time-sensitive competition (auction, lottery, etc.).
"""
from __future__ import annotations

from slither import Slither
from slither.core.declarations.solidity_variables import SolidityVariableComposed

_TIMESTAMP_NAMES: frozenset[str] = frozenset({"block.timestamp", "now"})


def detect_front_running(slither: Slither) -> list[dict]:
    """
    Flags two front-running patterns:
      - ERC-20 approve() race condition susceptibility
      - Payable functions whose outcome depends on block.timestamp
    """
    findings: list[dict] = []
    seen:     set[tuple] = set()

    for contract in slither.contracts:
        if contract.is_interface or contract.is_library:
            continue

        has_transfer_from = any(
            f.name.lower() == "transferfrom"
            for f in contract.functions
        )

        for function in contract.functions:
            if function.is_constructor:
                continue

            key = (contract.name, function.name)
            if key in seen:
                continue

            # ── Pattern 1: ERC-20 approve() race ─────────────────────────────
            if _is_approve_pattern(function) and has_transfer_from:
                seen.add(key)
                line = _function_line(function)
                findings.append({
                    "vulnerability" : "Front-Running: ERC-20 Approve Race",
                    "contract"      : contract.name,
                    "function"      : function.name,
                    "line"          : line,
                    "severity"      : "Medium",
                    "explanation"   : (
                        f"Function '{function.name}' sets an allowance directly. "
                        "An approved spender watching the mempool can call "
                        "transferFrom() with the OLD allowance before this update "
                        "is mined, then call it again with the NEW allowance — "
                        "spending both the old and new amounts."
                    ),
                    "suggested_fix" : (
                        "Replace direct approve() with increaseAllowance() / "
                        "decreaseAllowance() (OpenZeppelin ERC-20 extension). "
                        "Alternatively, require the caller to first reset the "
                        "allowance to zero: "
                        "require(allowance[msg.sender][spender] == 0 || amount == 0)."
                    ),
                })
                continue

            # ── Pattern 2: Timestamp-dependent payable ────────────────────────
            if function.payable and _function_reads_timestamp(function):
                seen.add(key)
                line = _function_line(function)
                findings.append({
                    "vulnerability" : "Front-Running: Timestamp-Dependent Payable",
                    "contract"      : contract.name,
                    "function"      : function.name,
                    "line"          : line,
                    "severity"      : "Medium",
                    "explanation"   : (
                        f"Payable function '{function.name}' uses block.timestamp "
                        "to determine the outcome (e.g., auction deadline, lottery "
                        "window). A miner or MEV bot can observe this transaction and "
                        "manipulate the timestamp by ~15 seconds to decide who wins "
                        "the time-sensitive competition."
                    ),
                    "suggested_fix" : (
                        "Use a commit-reveal scheme so transaction intent is hidden "
                        "until after the block is committed. For auctions, consider "
                        "a sealed-bid / blind-auction pattern. Avoid using "
                        "block.timestamp as the sole arbiter of financial outcomes."
                    ),
                })

    return findings


# ── Helpers ───────────────────────────────────────────────────────────────────

def _is_approve_pattern(function) -> bool:
    """Heuristic: named 'approve', public/external, writes at least one state var."""
    return (
        "approve" in function.name.lower()
        and function.visibility in ("public", "external")
        and len(function.all_state_variables_written()) > 0
    )


def _function_reads_timestamp(function) -> bool:
    """True if the function reads block.timestamp or 'now' anywhere."""
    for node in function.nodes:
        for ir in node.irs:
            for var in getattr(ir, "read", []):
                if isinstance(var, SolidityVariableComposed) and var.name in _TIMESTAMP_NAMES:
                    return True
    return False


def _function_line(function) -> int | str:
    """Return first source line of a function."""
    if function.source_mapping:
        return function.source_mapping.lines[0]
    if function.nodes and function.nodes[0].source_mapping:
        return function.nodes[0].source_mapping.lines[0]
    return "Unknown"
