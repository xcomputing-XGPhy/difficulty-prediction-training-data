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


# Collect eval trees (IQ-TREE) -> AllEvalTrees.trees cho bước RF bằng RAxML-NG
rule collect_eval_trees:
    input:
        pars = lambda wc: expand(iqtree_tree_eval_dir + "pars_{seed}.treefile", seed=pars_seeds, msa=wc.msa),
        rand = lambda wc: expand(iqtree_tree_eval_dir + "rand_{seed}.treefile", seed=rand_seeds, msa=wc.msa)
    output:
        all_eval_trees = iqtree_tree_eval_dir + "AllEvalTrees.trees"
    run:
        with open(output.all_eval_trees, "w") as out:
            for p in list(input.pars) + list(input.rand):
                with open(p) as f:
                    out.write(f.read().strip() + "\n")


# Collect eval logs (IQ-TREE) -> AllEvalLogs.log (nếu bạn còn dùng ở downstream)
rule collect_eval_logs:
    input:
        pars = lambda wc: expand(iqtree_tree_eval_dir + "pars_{seed}.log", seed=pars_seeds, msa=wc.msa),
        rand = lambda wc: expand(iqtree_tree_eval_dir + "rand_{seed}.log", seed=rand_seeds, msa=wc.msa)
    output:
        all_eval_logs = iqtree_tree_eval_dir + "AllEvalLogs.log"
    shell:
        "cat {input.pars} {input.rand} > {output.all_eval_logs}"
