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
        model   = lambda wildcards: iqtree_models[wildcards.msa],
        threads = config["software"]["iqtree"]["threads"]
    log:
        f"{iqtree_tree_inference_prefix_pars}.snakelog",
    shell:
        "{iqtree_command} "
        "-s {params.msa} "
        "-pre {params.prefix} "
        "-seed {wildcards.seed} "
        "-ninit 1 "
        "-T {params.threads} "
        "-redo "
        "-n 0 "
        "> {output.iqtree_log} 2>&1"


rule iqtree_rand_tree:
    output:
        iqtree_tree  = iqtree_tree_inference_prefix_rand + ".xgphy.treefile",
        iqtree_log   = iqtree_tree_inference_prefix_rand + ".xgphy.log"
    params:
        prefix  = iqtree_tree_inference_dir + "rand",
        msa     = lambda wc: msas[wc.msa],
        threads = config["software"]["iqtree"]["threads"],
        num_rand_trees = num_rand_trees
    log:
        f"{iqtree_tree_inference_prefix_rand}.snakelog",
    shell:
        "{iqtree_command} "
        "-s {params.msa} "
        "-pre {params.prefix} "
        "-seed {wildcards.seed} "
        "-t RANDOM "
        "-T {params.threads} "
        "-redo "
        "-n 3 "
        "-ninit {num_rand_trees} "
        "-xgphy "
        "-xgphy_nni_count 3 "
        "> {output.iqtree_log} 2>&1"