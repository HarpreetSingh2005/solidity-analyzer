# detectors/reentrancy.py
from slither import Slither
from slither.slithir.operations import HighLevelCall, LowLevelCall, Send, Transfer

def detect_reentrancy(slither: Slither):
    """
    Detects potential reentrancy vulnerabilities by checking for
    external calls that occur before state variable updates.
    """
    findings = []
    
    for contract in slither.contracts:
        for function in contract.functions:
            # Skip private/internal/constructor as they are less likely to be reentrancy targets
            if function.is_constructor or function.visibility not in ["public", "external"]:
                continue

            call_nodes = []
            state_update_nodes = []

            for node in function.nodes:
                # Check for any external call operation in the node
                has_external_call = any(
                    isinstance(ir, (HighLevelCall, LowLevelCall, Send, Transfer)) 
                    for ir in node.irs
                )

                if has_external_call:
                    call_nodes.append(node)
                
                # Track nodes that write to storage
                if node.state_variables_written:
                    state_update_nodes.append(node)

            # Checks-Effects-Interactions (CEI) Violation Check
            for call_node in call_nodes:
                if not call_node.source_mapping:
                    continue
                    
                call_line = call_node.source_mapping.lines[0]
                
                # Find state variables read BEFORE this call
                vars_read_before_call = set()
                for node in function.nodes:
                    if node.source_mapping and node.source_mapping.lines[0] < call_line:
                        vars_read_before_call.update(node.state_variables_read)

                # Find state variables written AFTER this call
                for update_node in state_update_nodes:
                    if not update_node.source_mapping:
                        continue
                        
                    update_line = update_node.source_mapping.lines[0]
                    
                    # Only look at nodes that happen AFTER the call
                    if call_line < update_line:
                        vars_written_after_call = set(update_node.state_variables_written)
                        
                        # Intersection: Read before AND written after
                        vulnerable_vars = vars_read_before_call.intersection(vars_written_after_call)
                        
                        if vulnerable_vars:
                            var_names = [v.name for v in vulnerable_vars]
                            
                            findings.append({
                                "vulnerability": "Reentrancy (CEI Violation)",
                                "contract": contract.name,
                                "function": function.name,
                                "line": call_line,
                                "severity": "High",
                                "explanation": f"The external call at line {call_line} occurs before state variables ({', '.join(var_names)}) are updated at line {update_line}. This violates the Checks-Effects-Interactions pattern.",
                                "suggested_fix": f"Reorder the operations in function '{function.name}' to update the state variables ({', '.join(var_names)}) before the external call at line {call_line}."
                            })
                            break # Found one violation for this call, move to next
                            
    return findings