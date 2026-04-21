# detectors/integer_overflow.py
"""
Detector: Integer Overflow / Underflow
Targets: Solidity contracts compiled with pragma < 0.8.0

In Solidity < 0.8.0, arithmetic operations on integers do NOT revert on
overflow/underflow. This can lead to catastrophic logical errors (e.g., a
balance wrapping from 0 to 2^256-1). Solidity >= 0.8.0 has built-in
overflow protection, making this a non-issue for modern contracts.
"""
from slither import Slither
from slither.slithir.operations import Binary, BinaryType

# Arithmetic IR operations that can overflow/underflow
_OVERFLOW_OPS = {BinaryType.ADDITION, BinaryType.MULTIPLICATION}
_UNDERFLOW_OPS = {BinaryType.SUBTRACTION}
_ALL_RISKY_OPS = _OVERFLOW_OPS | _UNDERFLOW_OPS


def _is_pre_08(slither: Slither) -> bool:
    """Returns True if any compilation unit targets a Solidity version < 0.8.0."""
    for cu in slither.compilation_units:
        for pragma in cu.pragma_directives:
            directive = " ".join(pragma.directive)
            # Look for explicit version pinning like ^0.7.x, 0.6.x, >=0.4.x, etc.
            for part in directive.split():
                for prefix in ("^", ">=", "<=", "=", ""):
                    candidate = part.lstrip(prefix)
                    if candidate.startswith("0.") and len(candidate) >= 3:
                        try:
                            minor = int(candidate.split(".")[1])
                            if minor < 8:
                                return True
                        except (ValueError, IndexError):
                            pass
    return False


def detect_integer_overflow(slither: Slither):
    """
    Detects unsafe arithmetic on integer types in contracts compiled with
    Solidity < 0.8.0 (no built-in overflow protection).
    Flags: addition, subtraction, multiplication on uint/int state variables
    without SafeMath wrapping.
    """
    findings = []

    if not _is_pre_08(slither):
        return findings  # >= 0.8.0 has native overflow checks — safe

    for contract in slither.contracts:
        if contract.is_interface or contract.is_library:
            continue

        # Check if contract uses SafeMath (inheritance or library usage)
        uses_safemath = any(
            "safemath" in parent.name.lower()
            for parent in contract.inheritance
        )

        for function in contract.functions:
            if function.is_constructor:
                continue

            for node in function.nodes:
                for ir in node.irs:
                    if not isinstance(ir, Binary):
                        continue
                    if ir.type not in _ALL_RISKY_OPS:
                        continue

                    # Only flag operations on integer types
                    lvalue = ir.lvalue
                    if lvalue is None:
                        continue

                    type_str = str(lvalue.type).lower()
                    if not ("uint" in type_str or "int" in type_str):
                        continue

                    if uses_safemath:
                        continue  # SafeMath guards this contract

                    line = node.source_mapping.lines[0] if node.source_mapping else "Unknown"
                    op_name = "overflow" if ir.type in _OVERFLOW_OPS else "underflow"

                    # Deduplicate: one finding per function per op type
                    already_flagged = any(
                        f["function"] == function.name and
                        f["contract"] == contract.name and
                        op_name in f["vulnerability"].lower()
                        for f in findings
                    )
                    if already_flagged:
                        continue

                    findings.append({
                        "vulnerability": f"Integer {op_name.capitalize()} Risk",
                        "contract": contract.name,
                        "function": function.name,
                        "line": line,
                        "severity": "High",
                        "explanation": (
                            f"Function '{function.name}' performs arithmetic ({ir.type.name}) on an integer "
                            f"at line {line} in a Solidity < 0.8.0 contract. Without SafeMath or built-in "
                            f"overflow protection, this can silently wrap around and corrupt balances or "
                            f"counters."
                        ),
                        "suggested_fix": (
                            "Either upgrade the pragma to ^0.8.0 (which enables native overflow checks) "
                            "or use OpenZeppelin's SafeMath library for all arithmetic operations."
                        )
                    })

    return findings
