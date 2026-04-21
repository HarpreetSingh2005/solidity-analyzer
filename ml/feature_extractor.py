# ml/feature_extractor.py
import pandas as pd
import numpy as np

def extract_features_from_slither(slither):
    """
    Extracts simple, lightweight features from a Slither object for ML analysis.
    Designed for fast local execution on limited resources.
    """
    features_list = []
    
    for contract in slither.contracts:
        # We focus on the main contracts, skipping libraries/interfaces to keep it light
        if contract.is_interface or contract.is_library:
            continue
            
        for function in contract.functions:
            # Skip shadowed or internal Slither-generated functions
            if function.is_shadowed or function.full_name.startswith('slither_'):
                continue

            # Basic complexity and size features
            feat = {
                "contract_name": contract.name,
                "function_name": function.full_name,
                "line_number": function.source_mapping.lines[0] if function.source_mapping else 0,
                "num_nodes": len(function.nodes),
                "num_lines": len(function.source_mapping.lines) if function.source_mapping else 0,
                "num_parameters": len(function.parameters),
                "num_modifiers": len(function.modifiers),
                "is_payable": 1 if getattr(function, 'payable', False) else 0,
                "is_constructor": 1 if function.is_constructor else 0,
                "visibility_score": {"public": 3, "external": 2, "internal": 1, "private": 0}.get(function.visibility, 0),
            }

            # Security-relevant counts
            feat["num_external_calls"] = len(function.high_level_calls)
            feat["num_internal_calls"] = len(function.internal_calls)
            feat["num_state_reads"] = len(function.all_state_variables_read())
            feat["num_state_writes"] = len(function.all_state_variables_written())
            
            # Semantic boolean flags
            all_irs = []
            for node in function.nodes:
                all_irs.extend([str(ir).lower() for ir in node.irs])
            
            feat["has_tx_origin"] = 1 if any('tx.origin' in ir for ir in all_irs) else 0
            feat["has_msg_value"] = 1 if any('msg.value' in ir for ir in all_irs) else 0
            feat["can_send_eth"] = 1 if function.can_send_eth else 0
            feat["has_assembly"] = 1 if getattr(function, 'contains_assembly', False) else 0
            
            # Reentrancy-like pattern: State update after an external call
            from slither.slithir.operations import HighLevelCall, LowLevelCall, Send, Transfer, Assignment
            
            state_write_after_call = 0
            found_call = False
            for node in function.nodes:
                # Check for high level calls in IR
                if any(isinstance(ir, (HighLevelCall, LowLevelCall, Send, Transfer)) for ir in node.irs):
                    found_call = True
                # If we found a call and now see a state write
                if found_call and any(isinstance(ir, Assignment) for ir in node.irs):
                    state_write_after_call = 1
                    break
            feat["calls_before_state_update"] = state_write_after_call

            features_list.append(feat)
            
    return features_list

def get_feature_names():
    """Returns the list of numerical feature names used for training/prediction."""
    return [
        "num_nodes", "num_lines", "num_parameters", "num_modifiers", 
        "is_payable", "is_constructor", "visibility_score", "num_external_calls", 
        "num_internal_calls", "num_state_reads", "num_state_writes", 
        "has_tx_origin", "has_msg_value", "can_send_eth", "has_assembly", 
        "calls_before_state_update"
    ]

def prepare_for_prediction(features_list):
    """Converts extracted features into a format ready for the ML model."""
    df = pd.DataFrame(features_list)
    if df.empty:
        return None, None
        
    feature_names = get_feature_names()
    X = df[feature_names].fillna(0).values
    return X, df

if __name__ == "__main__":
    import os
    from pathlib import Path
    import csv
    from slither import Slither

    print("=" * 60)
    print("  SESA — Feature Extractor")
    print("=" * 60)

    project_root = Path(__file__).parent.parent
    labels_file = project_root / "dataset" / "labels.csv"
    output_file = project_root / "dataset" / "features.csv"

    if not labels_file.exists():
        print(f"[ERROR] {labels_file} not found. Run scripts/create_dataset.py first.")
        exit(1)

    labels_df = pd.read_csv(labels_file)
    all_features = []

    print(f"Extracting features from {len(labels_df)} contracts...")
    for index, row in labels_df.iterrows():
        contract_path = project_root / row['contract_path']
        if not contract_path.exists():
            print(f"  [WARN] File missing: {contract_path}")
            continue
            
        print(f"  [SCAN] {row['contract_path']}")
        try:
            # We disable color and ignore solc output for cleaner logs
            slither_obj = Slither(str(contract_path), disable_color=True)
            extracted = extract_features_from_slither(slither_obj)
            
            # Attach label and metadata to each extracted function
            for feat in extracted:
                feat['contract_path'] = row['contract_path']
                feat['label'] = row['label']
                feat['category'] = row['category']
                feat['description'] = row['description']
                all_features.append(feat)
        except Exception as e:
            print(f"  [ERROR] Failed to parse {contract_path.name}: {e}")

    if all_features:
        final_df = pd.DataFrame(all_features)
        final_df.to_csv(output_file, index=False)
        print("\n" + "=" * 60)
        print(f"  Done! Extracted {len(all_features)} function-level features.")
        print(f"  Saved to: {output_file.relative_to(project_root)}")
        print("=" * 60)
    else:
        print("\n[ERROR] No features were extracted.")
