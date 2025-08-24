rule compute_msa_features:
    output:
        msa_features =  f"{output_files_dir}msa_features.json"
    params:
        msa                 = lambda wildcards: msas[wildcards.msa],
        model               = lambda wildcards: iqtree_models[wildcards.msa],  # Use IQ-Tree models
        iqtree_command      = iqtree_command  # Use IQ-Tree command
    script:
        "scripts/collect_msa_features_iqtree.py"  # Use IQ-Tree script
