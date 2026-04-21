# detectors/self_destruct.py
"""
Detector: Unprotected Self-Destruct (selfdestruct / suicide)
SWC-106  |  Severity: Critical

selfdestruct(recipient) destroys the contract and forwards its entire ETH
balance to the recipient.  When exposed in an unprotected public/external
function — one without an owner check or similar guard — any address can
permanently destroy the contract and steal its funds.

Detection strategy:
  For each public/external function that lacks a recognised access-control
  modifier, scan the SlithIR for a SolidityCall to selfdestruct/suicide, or
  fall back to a string scan for older Slither versions.
"""
from __future__ import annotations

from slither import Slither
from slither.slithir.operations import SolidityCall

_ACCESS_MOD_KEYWORDS: tuple[str, ...] = (
    "onlyowner", "onlyadmin", "onlyrole", "authorized",
    "onlygovernor", "onlyoperator",
)
_SELFDESTRUCT_NAMES: frozenset[str] = frozenset({"selfdestruct", "suicide"})


def detect_self_destruct(slither: Slither) -> list[dict]:
    """
    Flags public/external functions that contain selfdestruct/suicide without
    an access-control guard.
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

            # Skip functions that already have an access-control modifier
            mod_names = [m.name.lower() for m in function.modifiers]
            if any(kw in m for m in mod_names for kw in _ACCESS_MOD_KEYWORDS):
                continue

            for node in function.nodes:
                sd_line = _selfdestruct_line(node)
                if sd_line is None:
                    continue

                seen.add(key)
                findings.append({
                    "vulnerability" : "Unprotected Self-Destruct",
                    "contract"      : contract.name,
                    "function"      : function.name,
                    "line"          : sd_line,
                    "severity"      : "Critical",
                    "explanation"   : (
                        f"Function '{function.name}' contains a selfdestruct call at "
                        f"line {sd_line} and has no access-control guard. Any external "
                        f"address can call this function, permanently destroying the "
                        f"contract and forwarding its entire ETH balance to an arbitrary "
                        f"recipient."
                    ),
                    "suggested_fix" : (
                        f"Add an 'onlyOwner' modifier (or equivalent) to "
                        f"'{function.name}', or replace the selfdestruct pattern with a "
                        f"pausable/upgradeable design. If self-destruction is truly "
                        f"required, protect it with: "
                        f"require(msg.sender == owner, \"Not owner\")."
                    ),
                })
                break  # one finding per function

    return findings


# ── Helper ────────────────────────────────────────────────────────────────────

def _selfdestruct_line(node) -> int | None:
    """
    Return the source line of a selfdestruct/suicide call in `node`, or None.
    Tries typed IR first, then string fallback.
    """
    for ir in node.irs:
        # Typed check
        if isinstance(ir, SolidityCall):
            if ir.function.name in _SELFDESTRUCT_NAMES:
                return node.source_mapping.lines[0] if node.source_mapping and node.source_mapping.lines else "Unknown"
        # String fallback (covers different Slither versions)
        ir_str = str(ir).lower()
        if "selfdestruct" in ir_str or "suicide" in ir_str:
            return node.source_mapping.lines[0] if node.source_mapping and node.source_mapping.lines else "Unknown"
    return None
