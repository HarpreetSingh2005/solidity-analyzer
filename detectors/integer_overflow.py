# detectors/integer_overflow.py
"""
Detector: Integer Overflow / Underflow Risk
SWC-101  |  Severity: High
Targets:  Solidity < 0.8.0 contracts only

In Solidity < 0.8.0, arithmetic operations on integers do NOT revert on
overflow or underflow — the value silently wraps around (modular arithmetic).
This has been exploited to mint unlimited tokens (overflow) or bypass balance
checks (underflow).

Solidity >= 0.8.0 includes built-in checked arithmetic; this detector
returns no findings for modern contracts.  For pre-0.8.0 contracts, it
checks whether SafeMath is already in use; if not, every arithmetic
operation on integer types is a potential vulnerability.

Detection strategy:
  1. Check pragma directives for Solidity version < 0.8.0.
  2. Skip contracts that inherit from SafeMath.
  3. Flag Binary IR ops (ADD, SUB, MUL) on integer-typed lvalues.
  4. Deduplicate to one finding per (contract, function, op-type).
"""
from __future__ import annotations

from slither import Slither
from slither.slithir.operations import Binary, BinaryType

_OVERFLOW_OPS  : frozenset = frozenset({BinaryType.ADDITION, BinaryType.MULTIPLICATION})
_UNDERFLOW_OPS : frozenset = frozenset({BinaryType.SUBTRACTION})
_ALL_RISKY_OPS : frozenset = _OVERFLOW_OPS | _UNDERFLOW_OPS


def _is_pre_08(slither: Slither) -> bool:
    """Return True if any compilation unit targets Solidity < 0.8.0."""
    for cu in slither.compilation_units:
        for pragma in cu.pragma_directives:
            directive = " ".join(pragma.directive)
            for part in directive.split():
                candidate = part.lstrip("^>=<= ")
                if candidate.startswith("0.") and len(candidate) >= 3:
                    try:
                        minor = int(candidate.split(".")[1])
                        if minor < 8:
                            return True
                    except (ValueError, IndexError):
                        pass
    return False


def _uses_safemath(contract) -> bool:
    """Return True if the contract inherits from a SafeMath library."""
    return any("safemath" in p.name.lower() for p in contract.inheritance)


def detect_integer_overflow(slither: Slither) -> list[dict]:
    """
    Flags unsafe arithmetic in Solidity < 0.8.0 contracts not using SafeMath.
    Returns no findings for Solidity >= 0.8.0.
    """
    findings: list[dict] = []

    if not _is_pre_08(slither):
        return findings  # >= 0.8.0 — native overflow protection

    seen: set[tuple] = set()

    for contract in slither.contracts:
        if contract.is_interface or contract.is_library:
            continue
        if _uses_safemath(contract):
            continue

        for function in contract.functions:
            if function.is_constructor:
                continue

            for node in function.nodes:
                for ir in node.irs:
                    if not isinstance(ir, Binary):
                        continue
                    if ir.type not in _ALL_RISKY_OPS:
                        continue

                    lvalue = ir.lvalue
                    if lvalue is None:
                        continue

                    type_str = str(lvalue.type).lower()
                    if "uint" not in type_str and "int" not in type_str:
                        continue

                    op_label = "Overflow" if ir.type in _OVERFLOW_OPS else "Underflow"
                    key = (contract.name, function.name, op_label)
                    if key in seen:
                        continue
                    seen.add(key)

                    line = node.source_mapping.lines[0] if node.source_mapping else "Unknown"
                    findings.append({
                        "vulnerability" : f"Integer {op_label} Risk",
                        "contract"      : contract.name,
                        "function"      : function.name,
                        "line"          : line,
                        "severity"      : "High",
                        "explanation"   : (
                            f"Function '{function.name}' performs '{ir.type.name}' "
                            f"arithmetic on an integer variable at line {line} in a "
                            f"Solidity < 0.8.0 contract without SafeMath. On {op_label.lower()}, "
                            f"the value wraps silently — e.g., a balance could wrap from "
                            f"0 to 2^256-1, giving an attacker unlimited funds."
                        ),
                        "suggested_fix" : (
                            "Upgrade the compiler pragma to '^0.8.0' to enable native "
                            "checked arithmetic, or wrap all arithmetic in "
                            "OpenZeppelin's SafeMath library functions "
                            "(SafeMath.add, SafeMath.sub, SafeMath.mul)."
                        ),
                    })

    return findings
