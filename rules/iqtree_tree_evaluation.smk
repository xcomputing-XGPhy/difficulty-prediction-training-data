# Re-evaluate pars start trees with IQ-TREE (fixed topology)
rule reevaluate_iqtree_pars_tree:
    input:
        tree = iqtree_tree_inference_prefix_pars + ".treefile",
        msa  = lambda wc: msas[wc.msa]
    output:
        tree  = iqtree_tree_eval_prefix_pars + ".treefile",
        model = iqtree_tree_eval_prefix_pars + ".model.gz",
        log   = iqtree_tree_eval_prefix_pars + ".log"
    params:
        prefix  = iqtree_tree_eval_prefix_pars,
        model   = lambda wc: iqtree_models[wc.msa],
        threads = config["software"]["iqtree"]["threads"]
    log:
        iqtree_tree_eval_prefix_pars + ".snakelog"
    shell:
        # -te: dùng topology input, -n 0: không search, chỉ tối ưu trên topology đó
        "mkdir -p $(dirname {params.prefix}) && "
        "{iqtree_command} -s {input.msa} -m {params.model} -pre {params.prefix} "
        "-nt {params.threads} -seed {wildcards.seed} -te {input.tree} -n 0 "
        "> {log} 2>&1"


# Re-evaluate rand start trees with IQ-TREE (fixed topology)
rule reevaluate_iqtree_rand_tree:
    input:
        tree = iqtree_tree_inference_prefix_rand + ".treefile",
        msa  = lambda wc: msas[wc.msa]
    output:
        tree  = iqtree_tree_eval_prefix_rand + ".treefile",
        model = iqtree_tree_eval_prefix_rand + ".model.gz",
        log   = iqtree_tree_eval_prefix_rand + ".log"
    params:
        prefix  = iqtree_tree_eval_prefix_rand,
        model   = lambda wc: iqtree_models[wc.msa],
        threads = config["software"]["iqtree"]["threads"]
    log:
        iqtree_tree_eval_prefix_rand + ".snakelog"
    shell:
        "mkdir -p $(dirname {params.prefix}) && "
        "{iqtree_command} -s {input.msa} -m {params.model} -pre {params.prefix} "
        "-nt {params.threads} -seed {wildcards.seed} -te {input.tree} -n 0 "
        "> {log} 2>&1"
