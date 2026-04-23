# ml/feature_extractor.py
from slither import Slither
from slither.slithir.operations import HighLevelCall, LowLevelCall, Send, Transfer, Assignment, Binary

def extract_features(slither: Slither) -> dict:
    features = {
        "num_functions": 0,
        "num_external_calls": 0,
        "calls_before_state_update": 0,
        "num_state_vars": 0,
        "has_tx_origin": 0,
        "has_selfdestruct": 0,
        "avg_function_size": 0,
        "num_payable_functions": 0,
        "num_modifiers": 0,
        "num_state_writes": 0,
        
        # === New Semantic Features ===
        "has_delegatecall": 0,
        "has_assembly": 0,
        "uses_tx_origin_in_condition": 0,
        "external_call_before_any_state_update": 0,
        "has_unchecked_external_call": 0,
        "num_user_controlled_inputs_to_state": 0,
        "has_balance_check_before_send": 0,
        "max_call_depth": 0,
        "has_reentrancy_guard_pattern": 0,
    }

    total_nodes = 0

    for contract in slither.contracts:
        features["num_functions"] += len(contract.functions)
        features["num_state_vars"] += len(contract.state_variables)

        for func in contract.functions:
            if func.is_constructor:
                continue

            features["num_modifiers"] += len(func.modifiers)
            if getattr(func, 'payable', False):
                features["num_payable_functions"] += 1

            external_calls = 0
            call_seen = False
            node_count = len(func.nodes)
            total_nodes += node_count
            local_call_depth = 0

            for node in func.nodes:
                local_call_depth += 1
                features["max_call_depth"] = max(features["max_call_depth"], local_call_depth)

                for ir in node.irs:
                    ir_str = str(ir).lower()

                    if isinstance(ir, (HighLevelCall, LowLevelCall, Send, Transfer)):
                        external_calls += 1
                        call_seen = True

                        # Check for unchecked external calls
                        if not any("require" in str(s) for s in node.sons):
                            features["has_unchecked_external_call"] = 1

                    if isinstance(ir, Assignment):
                        features["num_state_writes"] += 1

                    if "delegatecall" in ir_str:
                        features["has_delegatecall"] = 1
                    if "assembly" in ir_str:
                        features["has_assembly"] = 1
                    if "tx.origin" in ir_str:
                        features["has_tx_origin"] = 1
                        features["uses_tx_origin_in_condition"] = 1

                    if "selfdestruct" in ir_str or "suicide" in ir_str:
                        features["has_selfdestruct"] = 1

                # Reentrancy pattern detection
                if call_seen and len(node.state_variables_written) > 0:
                    features["calls_before_state_update"] += 1

                # Very basic balance check before send
                if call_seen and "balance" in str(node).lower() and "require" in str(node).lower():
                    features["has_balance_check_before_send"] = 1

            features["num_external_calls"] += external_calls

    if features["num_functions"] > 0:
        features["avg_function_size"] = total_nodes / features["num_functions"]

    return features