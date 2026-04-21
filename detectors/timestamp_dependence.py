# detectors/timestamp_dependence.py
"""
Detector: Block Timestamp Dependence
SWC-116  |  Severity: Medium

Miners/validators have approximately 15 seconds of discretion when setting
block.timestamp (and its deprecated alias 'now').  Contracts that use
block.timestamp for critical conditional logic — timelocks, auction
deadlines, random-seed generation, financial conditions — can be
manipulated by a validator to skew the outcome in their favour.

Detection strategy:
  Flag public/external functions that read block.timestamp inside a
  conditional context (require / if / assert / while / for).  One finding
  per (contract, function) pair.
"""
from __future__ import annotations

from slither import Slither
from slither.core.declarations.solidity_variables import SolidityVariableComposed

_TIMESTAMP_NAMES: frozenset[str] = frozenset({"block.timestamp", "now"})
_CONDITION_KEYWORDS: tuple[str, ...] = ("require", "if", "assert", "while", "for")


def detect_timestamp_dependence(slither: Slither) -> list[dict]:
    """
    Flags public/external functions that use block.timestamp inside
    conditional logic.
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

            key = (contract.name, function.name)
            if key in seen:
                continue

            for node in function.nodes:
                if not _node_reads_timestamp(node):
                    continue

                node_str = str(node).lower()
                if not any(kw in node_str for kw in _CONDITION_KEYWORDS):
                    continue

                line = node.source_mapping.lines[0] if node.source_mapping else "Unknown"
                seen.add(key)
                findings.append({
                    "vulnerability" : "Timestamp Dependence",
                    "contract"      : contract.name,
                    "function"      : function.name,
                    "line"          : line,
                    "severity"      : "Medium",
                    "explanation"   : (
                        f"Function '{function.name}' uses 'block.timestamp' in "
                        f"conditional logic at line {line}. Miners/validators can "
                        f"manipulate this value by up to ~15 seconds, potentially "
                        f"influencing time-sensitive operations such as timelocks, "
                        f"auction deadlines, or random-seed generation."
                    ),
                    "suggested_fix" : (
                        "Avoid relying on block.timestamp for exact timing or "
                        "randomness. For timelocks, use sufficiently large windows "
                        "(> 15 minutes) so miner manipulation is economically "
                        "irrelevant. For randomness, use a commit-reveal scheme or "
                        "a verifiable random function (VRF) such as Chainlink VRF."
                    ),
                })
                break  # one finding per function

    return findings


# ── Helper ────────────────────────────────────────────────────────────────────

def _node_reads_timestamp(node) -> bool:
    """Return True if any IR in the node reads block.timestamp / now."""
    for ir in node.irs:
        for var in getattr(ir, "read", []):
            if isinstance(var, SolidityVariableComposed) and var.name in _TIMESTAMP_NAMES:
                return True
    return False
