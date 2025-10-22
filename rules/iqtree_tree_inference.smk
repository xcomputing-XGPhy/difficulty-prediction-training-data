rule iqtree_pars_tree:
    """
    Rule that infers a single ML tree using a parsimony starting tree in IQ-TREE 3.
    """
    output:
        iqtree_best_tree     = f"{iqtree_tree_inference_prefix_pars}.treefile",
        # iqtree_starting_tree = f"{iqtree_tree_inference_prefix_pars}.iqtree",
        iqtree_best_model    = f"{iqtree_tree_inference_prefix_pars}.iqtree",
        iqtree_log           = f"{iqtree_tree_inference_prefix_pars}.log",
    params:
        prefix  = iqtree_tree_inference_prefix_pars,
        msa     = lambda wildcards: msas[wildcards.msa],
        data_type   = lambda wildcards: data_types[wildcards.msa],
        threads = config["software"]["iqtree"]["threads"]
    log:
        f"{iqtree_tree_inference_prefix_pars}.snakelog",
    run:
        detectType = "-st DNA " if str(params.data_type) == "DataType.DNA" else (
        "-st AA " if str(params.data_type) == "DataType.AA" else "")

        shell(
            "{iqtree_command} "
            "-s {params.msa} "
            "{detectType} "
            "-pre {params.prefix} "
            "-seed {wildcards.seed} "
            "-ninit 1 "
            "-T {params.threads} "
            "-redo "
            "-n 0 "
            "-nt AUTO "
            "> {output.iqtree_log} 2>&1"
        )


rule iqtree_rand_tree:
    """
    Rule that infers multiple random trees in a single IQ-TREE run using -ninit.
    """
    output:
        treefiles = [f"{iqtree_tree_inference_dir}rand_tree{i}_xgphy.treefile" for i in range(config["_debug"]["_num_rand_trees"])],
        logs = [f"{iqtree_tree_inference_dir}rand_tree{i}_xgphy.log" for i in range(config["_debug"]["_num_rand_trees"])],
        iqtree_log = f"{iqtree_tree_inference_dir}rand.log"
    params:
        prefix  = iqtree_tree_inference_dir + "rand",
        msa     = lambda wc: msas[wc.msa],
        threads = config["software"]["iqtree"]["threads"],
        data_type   = lambda wildcards: data_types[wildcards.msa],
        num_rand_trees = config["_debug"]["_num_rand_trees"]
    log:
        iqtree_tree_inference_dir + "rand.snakelog",
    run:
        detectType = "-st DNA " if str(params.data_type) == "DataType.DNA" else (
        "-st AA " if str(params.data_type) == "DataType.AA" else "")

        shell(
            "{iqtree_command} "
            "-s {params.msa} "
            "{detectType}"
            "-pre {params.prefix} "
            "-seed 0 "
            "-t RANDOM "
            "-T {params.threads} "
            "-redo "
            "-n 3 "
            "-ninit {params.num_rand_trees} "
            "-xgphy "
            "-xgphy_nni_count 3 "
            "-nt AUTO "
            "> {output.iqtree_log} 2>&1"
        )                                                                       