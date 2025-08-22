rule iqtree_pars_tree:
    """
    Rule that infers a single tree based on a parsimony starting tree using IQ-TREE.
    """
    output:
        iqtree_tree  = f"{iqtree_tree_inference_prefix_pars}.treefile",
        iqtree_model = f"{iqtree_tree_inference_prefix_pars}.model.gz",
        iqtree_log   = f"{iqtree_tree_inference_prefix_pars}.log",
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
        "-m {params.model} "
        "-pre {params.prefix} "
        "-nt {params.threads} "
        "-seed {wildcards.seed} "
        "-t BIONJ "
        "> {output.iqtree_log} 2>&1"


rule iqtree_rand_tree:
    """
    Rule that infers a single tree based on a random starting tree using IQ-TREE.
    """
    output:
        iqtree_tree  = f"{iqtree_tree_inference_prefix_rand}.treefile",
        iqtree_model = f"{iqtree_tree_inference_prefix_rand}.model.gz",
        iqtree_log   = f"{iqtree_tree_inference_prefix_rand}.log",
    params:
        prefix  = iqtree_tree_inference_prefix_rand,
        msa     = lambda wildcards: msas[wildcards.msa],
        model   = lambda wildcards: iqtree_models[wildcards.msa],
        threads = config["software"]["iqtree"]["threads"]
    log:
        f"{iqtree_tree_inference_prefix_rand}.snakelog",
    shell:
        "{iqtree_command} "
        "-s {params.msa} "
        "-m {params.model} "
        "-pre {params.prefix} "
        "-nt {params.threads} "
        "-seed {wildcards.seed} "
        "-t RANDOM "
        "> {output.iqtree_log} 2>&1"
