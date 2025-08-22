rule raxmlng_rfdistance_search_trees:
    """
    Compute RF distances between ALL IQ-TREE search trees using RAxML-NG.
    Input is the concatenated tree list from collect_search_trees (IQ-TREE .treefile).
    """
    input:
        # lấy từ IQ-TREE: AllSearchTrees.trees do collect_search_trees tạo
        output_files_iqtree_dir + "AllSearchTrees.trees"
    output:
        rfDist     = f"{raxmlng_tree_inference_dir}inference.raxml.rfDistances",
        rfDist_log = f"{raxmlng_tree_inference_dir}inference.raxml.rfDistances.log",
    params:
        prefix = f"{raxmlng_tree_inference_dir}inference"
    log:
        f"{raxmlng_tree_inference_dir}inference.raxml.rfDistances.snakelog",
    shell:
        "{raxmlng_command} "
        "--rfdist "
        "--tree {input} "
        "--prefix {params.prefix} "
        ">> {output.rfDist_log} "


rule raxmlng_rfdistance_eval_trees:
    """
    Compute RF distances between ALL eval trees using RAxML-NG.
    (giữ nguyên nguồn eval từ rule collect_eval_trees hiện có)
    """
    input:
        all_eval_trees = rules.collect_eval_trees.output.all_eval_trees
    output:
        rfDist     = f"{raxmlng_tree_eval_dir}eval.raxml.rfDistances",
        rfDist_log = f"{raxmlng_tree_eval_dir}eval.raxml.rfDistances.log",
    params:
        prefix = f"{raxmlng_tree_eval_dir}eval"
    log:
        f"{raxmlng_tree_eval_dir}eval.raxml.rfDistances.snakelog",
    shell:
        "{raxmlng_command} "
        "--rfdist "
        "--tree {input.all_eval_trees} "
        "--prefix {params.prefix} "
        ">> {output.rfDist_log} "


rule raxmlng_rfdistance_plausible_trees:
    """
    Compute RF distances between ALL plausible trees using RAxML-NG.
    Nếu số cây plausible <= 1, ghi log/đầu ra dummy để tránh lỗi.
    """
    input:
        all_plausible_trees = rules.collect_plausible_trees.output.all_plausible_trees
    output:
        rfDist     = f"{raxmlng_tree_eval_dir}plausible.raxml.rfDistances",
        rfDist_log = f"{raxmlng_tree_eval_dir}plausible.raxml.rfDistances.log",
    params:
        prefix = f"{raxmlng_tree_eval_dir}plausible"
    log:
        f"{raxmlng_tree_eval_dir}plausible.raxml.rfDistances.snakelog",
    run:
        num_plausible = sum(1 for _ in open(input.all_plausible_trees))
        if num_plausible <= 1:
            with open(output.rfDist_log, "w") as f:
                f.write(
                    "Number of unique topologies in this tree set: 1\n"
                    "Average absolute RF distance in this tree set: 0.0\n"
                    "Average relative RF distance in this tree set: 0.0\n"
                )
            with open(output.rfDist, "w") as f:
                f.write("0 1 0.0 0.0\n")
        else:
            shell(
                "{raxmlng_command} --rfdist --tree {input.all_plausible_trees} "
                "--prefix {params.prefix} >> {output.rfDist_log}"
            )


rule raxmlng_rfdistance_parsimony_trees:
    """
    Compute RF distances between ALL Parsimonator parsimony trees using RAxML-NG.
    """
    input:
        all_parsimony_trees = f"{output_files_parsimony_trees}AllParsimonyTrees.trees",
    output:
        rfDist     = f"{output_files_parsimony_trees}parsimony.raxml.rfDistances",
        rfDist_log = f"{output_files_parsimony_trees}parsimony.raxml.rfDistances.log",
    params:
        prefix = f"{output_files_parsimony_trees}parsimony"
    log:
        f"{output_files_parsimony_trees}parsimony.raxml.rfDistances.snakelog",
    shell:
        "{raxmlng_command} "
        "--rfdist "
        "--tree {input.all_parsimony_trees} "
        "--prefix {params.prefix} "
        ">> {output.rfDist_log} "
