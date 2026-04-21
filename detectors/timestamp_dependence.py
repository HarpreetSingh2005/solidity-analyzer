# detectors/timestamp_dependence.py
"""
Detector: Timestamp Dependence
Solidity SWC-116

Miners have ~15 seconds of discretion when setting block.timestamp. Contracts
that use block.timestamp (or the alias 'now') for critical logic — random
number generation, timelock decisions, or financial conditions — can be
manipulated by a miner to their advantage.
"""
from slither import Slither
from slither.slithir.operations import SolidityCall
from slither.core.declarations.solidity_variables import SolidityVariableComposed


def detect_timestamp_dependence(slither: Slither):
    """
    Detects use of block.timestamp / 'now' inside conditional checks
    (require / if / assert) in public/external functions.
    Severity: Medium — miner manipulation window is narrow (~15s) but real.
    """
    findings = []
    seen = set()  # (contract, function) pairs already flagged

    for contract in slither.contracts:
        if contract.is_interface or contract.is_library:
            continue

        for function in contract.functions:
            if function.is_constructor:
                continue
            if function.visibility not in ("public", "external"):
                continue

            key = (contract.name, function.name)

            for node in function.nodes:
                if key in seen:
                    break

                # Check IRs for block.timestamp access
                uses_timestamp = False
                for ir in node.irs:
                    for var in getattr(ir, "read", []):
                        if isinstance(var, SolidityVariableComposed):
                            if var.name in ("block.timestamp", "now"):
                                uses_timestamp = True
                                break
                    if uses_timestamp:
                        break

                if not uses_timestamp:
                    continue

                # Only flag if timestamp is used in a conditional context
                node_str = str(node).lower()
                is_conditional = any(
                    kw in node_str for kw in ("require", "if", "assert", "while", "for")
                )

                if not is_conditional:
                    continue

                line = node.source_mapping.lines[0] if node.source_mapping else "Unknown"
                seen.add(key)

                findings.append({
                    "vulnerability": "Timestamp Dependence",
                    "contract": contract.name,
                    "function": function.name,
                    "line": line,
                    "severity": "Medium",
                    "explanation": (
                        f"Function '{function.name}' uses 'block.timestamp' in conditional logic at "
                        f"line {line}. Miners can manipulate this value by up to ~15 seconds, "
                        f"potentially influencing time-sensitive operations such as timelocks, "
                        f"auctions, or random-seed generation."
                    ),
                    "suggested_fix": (
                        "Avoid using block.timestamp for critical randomness or precise timing. "
                        "Use a commit-reveal scheme for randomness, or design timelocks with "
                        "sufficiently large windows (e.g., > 15 minutes) so miner manipulation "
                        "is economically insignificant."
                    )
                })

    return findings
