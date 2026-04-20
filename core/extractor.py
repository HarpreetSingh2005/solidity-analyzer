# core/extractor.py
from slither import Slither
from slither.slithir.operations import HighLevelCall, LowLevelCall, Send, Transfer

def extract_contract_features(slither: Slither) -> dict:
    """Extracts Slither features into JSON-serializable dictionaries for future ML use."""
    extracted_data = {"contracts": []}

    for contract in slither.contracts:
        contract_data = {
            "name": contract.name,
            "functions": []
        }

        for function in contract.functions:
            if function.is_constructor:
                continue
                
            func_data = {
                "name": function.name,
                "visibility": function.visibility,
                "modifiers": [mod.name for mod in function.modifiers],
                "nodes": []
            }

            for node in function.nodes:
                # Safely check for external calls using SlithIR types
                has_external_call = any(
                    isinstance(ir, (HighLevelCall, LowLevelCall, Send, Transfer)) 
                    for ir in node.irs
                )
                
                # Extract the actual string representation if it exists (for ML context)
                call_strings = []
                if has_external_call:
                    for ir in node.irs:
                        if isinstance(ir, (HighLevelCall, LowLevelCall)):
                            call_strings.append(str(ir.destination) + "." + str(ir.function_name))

                node_data = {
                    "line": node.source_mapping.lines[0] if node.source_mapping else None,
                    "state_vars_read": [var.name for var in node.state_variables_read],
                    "state_vars_written": [var.name for var in node.state_variables_written],
                    "external_calls": call_strings, 
                    # THE FIX: Use type().__name__ to safely get the operation name (e.g., "Index", "Assignment")
                    "ir_operations": [type(ir).__name__ for ir in node.irs]           
                }
                func_data["nodes"].append(node_data)

            contract_data["functions"].append(func_data)
        extracted_data["contracts"].append(contract_data)

    return extracted_data