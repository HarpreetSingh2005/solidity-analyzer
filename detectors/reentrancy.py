from slither import Slither


# Logic :
#   critical_state_read → external_call → critical_state_write
#   and not 
#   any_state_read → external_call → any_state_write
def detect_reentrancy(slither: Slither):
    findings = []
    
    for contract in slither.contracts:
        for function in contract.functions:
            if function.is_constructor or function.visibility not in ["public", "external"]:
                continue

            external_call_nodes = []
            suspicious_reads = [] # state vars read before external call
            suspicious_writes = [] # state vars written after external call

            for node in function.nodes:
                # Use SlithIR to detect external calls reliably
                is_external = any("call" in str(ir).lower() or 
                                  "send" in str(ir).lower() or 
                                  "transfer" in str(ir).lower() 
                                  for ir in node.irs)

                if is_external:
                    external_call_nodes.append(node)

                # Track state variable writes
                if node.state_variables_written:
                    state_update_nodes.append(node)

            print('external and state update nodes', dir(external_call_nodes[0].source_mapping), state_update_nodes)

            # Classic reentrancy: external call BEFORE state update
            for call_node in external_call_nodes:
                for update_node in state_update_nodes:
                    if update_node.source_mapping and call_node.source_mapping:
                        if call_node.source_mapping.lines[0] < update_node.source_mapping.lines[0] :
                            findings.append({
                                "vulnerability": "Reentrancy",
                                "contract": contract.name,
                                "function": function.name,
                                "line": call_node.source_mapping.lines[0] ,
                                "severity": "High",
                                "explanation": f"External call at line {call_node.source_mapping.lines[0] } happens before state update at line {update_node.source_mapping.lines[0] }.",
                                "suggested_fix": f"Move state update (line {update_node.source_mapping.lines[0] }) BEFORE the external call (line {call_node.source_mapping.lines[0] }). Follow Checks-Effects-Interactions pattern.",
                                "used_features": "function.nodes + state_variables_written + SlithIR"
                            })
    return findings