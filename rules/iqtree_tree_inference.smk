rule iqtree_pars_tree:
    """
    Rule that infers a single ML tree using a parsimony starting tree in IQ-TREE 3.
    """
    output:
        iqtree_best_tree     = f"{iqtree_tree_inference_prefix_pars}.treefile",
        iqtree_starting_tree = f"{iqtree_tree_inference_prefix_pars}.iqtree",
        iqtree_best_model    = f"{iqtree_tree_inference_prefix_pars}.model.gz",
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
        iqtree_tree  = iqtree_tree_inference_prefix_rand + ".treefile",
        iqtree_model = iqtree_tree_inference_prefix_rand + ".iqtree",
        iqtree_log   = iqtree_tree_inference_prefix_rand + ".log"
    params:
        prefix  = iqtree_tree_inference_prefix_rand,
        msa     = lambda wc: msas[wc.msa],
        model   = lambda wc: iqtree_models[wc.msa],
        threads = config["software"]["iqtree"]["threads"]
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
        "-ninit 10 "
        "-van "
        "-van_nni_count 10 "
        "> {output.iqtree_log} 2>&1"