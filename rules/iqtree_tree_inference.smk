rule iqtree_pars_tree:
    output:
        iqtree_tree  = iqtree_tree_inference_prefix_pars + ".treefile",
        iqtree_model = iqtree_tree_inference_prefix_pars + ".model.gz",
        iqtree_log   = iqtree_tree_inference_prefix_pars + ".log"
    params:
        prefix  = iqtree_tree_inference_prefix_pars,
        msa     = lambda wc: msas[wc.msa],
        model   = lambda wc: iqtree_models[wc.msa],
        threads = config["software"]["iqtree"]["threads"]
    log:
        iqtree_tree_inference_prefix_pars + ".snakelog"
    shell:
        "mkdir -p $(dirname {params.prefix}) && "
        "{iqtree_command} -s {params.msa} -m {params.model} -pre {params.prefix} "
        "-nt {params.threads} -seed {wildcards.seed} -t BIONJ "
        "> {log} 2>&1"


rule iqtree_rand_tree:
    output:
        iqtree_tree  = iqtree_tree_inference_prefix_rand + ".treefile",
        iqtree_model = iqtree_tree_inference_prefix_rand + ".model.gz",
        iqtree_log   = iqtree_tree_inference_prefix_rand + ".log"
    params:
        prefix  = iqtree_tree_inference_prefix_rand,
        msa     = lambda wc: msas[wc.msa],
        model   = lambda wc: iqtree_models[wc.msa],
        threads = config["software"]["iqtree"]["threads"]
    log:
        iqtree_tree_inference_prefix_rand + ".snakelog"
    shell:
        "mkdir -p $(dirname {params.prefix}) && "
        "{iqtree_command} -s {params.msa} -m {params.model} -pre {params.prefix} "
        "-nt {params.threads} -seed {wildcards.seed} -t RANDOM "
        "> {log} 2>&1"
