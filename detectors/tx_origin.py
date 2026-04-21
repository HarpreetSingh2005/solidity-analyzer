# detectors/tx_origin.py
"""
Detector: Vulnerable Use of tx.origin for Authentication
SWC-115  |  Severity: High

tx.origin is the original externally-owned account that initiated the
transaction chain.  Using it for authentication is dangerous: a malicious
intermediate contract can call your contract on behalf of a victim, and
tx.origin will still be the victim's address — allowing the malicious
contract to bypass the check.

Unlike msg.sender (the direct caller), tx.origin cannot be set by a smart
contract — it is always an EOA. This makes it useless for distinguishing
who is the *immediate* caller, which is what authentication requires.

Detection strategy:
  Flag any public/external function that references tx.origin inside a
  conditional context (require, if, assert).
"""
from __future__ import annotations

from slither import Slither
from slither.core.declarations.solidity_variables import SolidityVariableComposed

_CONDITION_KEYWORDS: tuple[str, ...] = ("require", "if", "assert", "revert")


def detect_tx_origin_phishing(slither: Slither) -> list[dict]:
    """
    Flags public/external functions that use tx.origin for authentication.
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
                if not _node_uses_tx_origin(node):
                    continue

                # Only flag if in a conditional context
                node_str = str(node).lower()
                if not any(kw in node_str for kw in _CONDITION_KEYWORDS):
                    continue

                line = node.source_mapping.lines[0] if node.source_mapping and node.source_mapping.lines else "Unknown"
                seen.add(key)
                findings.append({
                    "vulnerability" : "Vulnerable Use of tx.origin",
                    "contract"      : contract.name,
                    "function"      : function.name,
                    "line"          : line,
                    "severity"      : "High",
                    "explanation"   : (
                        f"Function '{function.name}' uses 'tx.origin' for authorization "
                        f"at line {line}. A malicious contract can call this function on "
                        f"behalf of a legitimate user — 'tx.origin' will still be the "
                        f"user's address, bypassing the check and giving the attacker "
                        f"full access."
                    ),
                    "suggested_fix" : (
                        f"Replace 'tx.origin' with 'msg.sender' in function "
                        f"'{function.name}'. 'msg.sender' always refers to the "
                        f"immediate caller and cannot be spoofed by an intermediate "
                        f"contract."
                    ),
                })
                break  # one finding per function

    return findings


# ── Helper ────────────────────────────────────────────────────────────────────

def _node_uses_tx_origin(node) -> bool:
    """Return True if any IR in the node reads tx.origin."""
    for ir in node.irs:
        for var in getattr(ir, "read", []):
            if isinstance(var, SolidityVariableComposed) and var.name == "tx.origin":
                return True
    # Fallback: string scan of the IR representation
    return any("tx.origin" in str(ir) for ir in node.irs)