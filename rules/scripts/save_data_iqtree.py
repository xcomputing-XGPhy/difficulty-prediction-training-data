import json
import numpy as np
import pickle
import uuid

from database import *
from iqtree_statstest_parser import get_iqtree_results, get_iqtree_results_for_eval_tree_str
from iqtree_parser import (
    get_all_iqtree_llhs,
    get_iqtree_llh,
    get_iqtree_elapsed_time,
    get_iqtree_starting_llh,
    get_iqtree_num_iterations,
    rel_rfdistance_starting_final,
    get_model_parameter_estimates,
    get_all_parsimony_scores,
    get_iqtree_runtimes
)

from iqtree_parser import get_iqtree_rfdist_results

from tree_metrics import (
    get_total_branch_length_for_tree,
    get_min_branch_length_for_tree,
    get_max_branch_length_for_tree,
    get_std_branch_lengths_for_tree,
    get_avg_branch_lengths_for_tree,
)

from pypythia.msa import MSA

db.init(snakemake.output.database)
db.connect()
db.create_tables(
    [
        Dataset,
        IQTreeTree,  # Use IQTreeTree instead of RaxmlNGTree
        ParsimonyTree,
        IQTreeTree
    ]
)
dataset_name = snakemake.wildcards.msa
iqtree_command = snakemake.params.iqtree_command  # Use IQ-Tree command instead

# tree search
pars_search_trees = snakemake.input.pars_search_trees
pars_starting_trees = snakemake.input.pars_starting_trees
pars_search_logs = snakemake.input.pars_search_logs
rand_search_trees = snakemake.input.rand_search_trees
rand_search_logs = snakemake.input.rand_search_logs
search_logs_collected = snakemake.input.search_logs_collected
search_rfdistance = snakemake.input.search_rfdistance

# eval
pars_eval_trees = snakemake.input.pars_eval_trees
pars_eval_logs = snakemake.input.pars_eval_logs
rand_eval_trees = snakemake.input.rand_eval_trees
rand_eval_logs = snakemake.input.rand_eval_logs
eval_logs_collected = snakemake.input.eval_logs_collected
eval_rfdistance = snakemake.input.eval_rfdistance

# plausible
plausible_rfdistance = snakemake.input.plausible_rfdistance
plausible_trees_collected = snakemake.input.plausible_trees_collected
iqtree_results = get_iqtree_results(snakemake.input.iqtree_results)
with open(snakemake.input.clusters, "rb") as f:
    clusters = pickle.load(f)

# msa features
with open(snakemake.input.msa_features) as f:
    msa_features = json.load(f)

# parsimony trees
parsimony_trees = snakemake.input.parsimony_trees
parsimony_logs = snakemake.input.parsimony_logs
parsimony_rfdistance = snakemake.input.parsimony_rfdistance

# Use IQ-Tree parser functions instead of RAxML-NG
llhs_search = get_all_iqtree_llhs(search_logs_collected)
llhs_eval = get_all_iqtree_llhs(eval_logs_collected)

parsimony_scores = get_all_parsimony_scores(parsimony_logs)
parsimony_runtimes = get_iqtree_runtimes(parsimony_logs)

num_searches = len(pars_search_trees) + len(rand_search_trees)
data_type = MSA(snakemake.params.msa).data_type

# for the starting tree features, we simply take the first parsimony tree inference
single_tree = pars_search_trees[0]
single_tree_log = pars_search_logs[0]
single_tree_starting = pars_starting_trees[0]

# Use IQ-Tree parser functions
slow_iter, fast_iter = get_iqtree_num_iterations(single_tree_log)
starting_llh = get_iqtree_starting_llh(single_tree_log)
final_llh = get_iqtree_llh(single_tree_log)
newick_starting = open(single_tree_starting).readline()
newick_final = open(single_tree).readline()
rate_het, base_freq, subst_rates = get_model_parameter_estimates(single_tree_log)

# Use IQ-Tree RF distance results
num_topos_search, avg_rfdist_search, _ = get_iqtree_rfdist_results(search_rfdistance)
num_topos_eval, avg_rfdist_eval, _ = get_iqtree_rfdist_results(eval_rfdistance)
num_topos_plausible, avg_rfdist_plausible, _ = get_iqtree_rfdist_results(plausible_rfdistance)
num_topos_parsimony, avg_rfdist_parsimony, _ = get_iqtree_rfdist_results(parsimony_rfdistance)

# Create dataset
Dataset.create(
    name=dataset_name,
    data_type=data_type,
    taxa=msa_features["taxa"],
    sites=msa_features["sites"],
    patterns=msa_features["patterns"],
    gaps=msa_features["gaps"],
    invariant=msa_features["invariant"],
    entropy=msa_features["entropy"],
    column_entropies=msa_features["column_entropies"],
    bollback=msa_features["bollback"],
    treelikeness=msa_features["treelikeness"],
    num_searches=num_searches,
    num_evaluations=len(pars_eval_trees) + len(rand_eval_trees),
    num_plausible=len(plausible_trees_collected),
    num_parsimony=len(parsimony_trees),
    num_topos_search=num_topos_search,
    num_topos_eval=num_topos_eval,
    num_topos_plausible=num_topos_plausible,
    num_topos_parsimony=num_topos_parsimony,
    avg_rfdist_search=avg_rfdist_search,
    avg_rfdist_eval=avg_rfdist_eval,
    avg_rfdist_plausible=avg_rfdist_plausible,
    avg_rfdist_parsimony=avg_rfdist_parsimony,
    avg_llh_search=np.mean(llhs_search),
    avg_llh_eval=np.mean(llhs_eval),
    std_llh_search=np.std(llhs_search),
    std_llh_eval=np.std(llhs_eval),
    avg_parsimony_score=np.mean(parsimony_scores),
    std_parsimony_score=np.std(parsimony_scores),
    avg_parsimony_runtime=np.mean(parsimony_runtimes),
    std_parsimony_runtime=np.std(parsimony_runtimes),
    rfdistance_starting_final=rel_rfdistance_starting_final(newick_starting, newick_final, iqtree_command),
    starting_llh=starting_llh,
    final_llh=final_llh,
    rate_het=rate_het,
    base_freq=base_freq,
    subst_rates=subst_rates,
    slow_iter=slow_iter,
    fast_iter=fast_iter,
)

# Save parsimony trees
for tree_path, log_path in zip(parsimony_trees, parsimony_logs):
    with open(tree_path) as f:
        newick = f.readline().strip()

    ParsimonyTree.create(
        dataset=dataset_name,
        newick=newick,
        parsimony_score=get_all_parsimony_scores(log_path)[0],
        compute_time=get_iqtree_elapsed_time(log_path),
        total_branch_length=get_total_branch_length_for_tree(newick),
        min_branch_length=get_min_branch_length_for_tree(newick),
        max_branch_length=get_max_branch_length_for_tree(newick),
        std_branch_lengths=get_std_branch_lengths_for_tree(newick),
        avg_branch_lengths=get_avg_branch_lengths_for_tree(newick),
    )

# Save plausible trees
for tree_path in plausible_trees_collected:
    with open(tree_path) as f:
        newick = f.readline().strip()

    # Get IQ-Tree results for this tree
    iqtree_result, cluster_id = get_iqtree_results_for_eval_tree_str(iqtree_results, newick, clusters)

    IQTreeTree.create(
        dataset=dataset_name,
        newick=newick,
        cluster_id=cluster_id,
        plausible=iqtree_result["plausible"],
        logL=iqtree_result["logL"],
        deltaL=iqtree_result["deltaL"],
        bp_RELL=iqtree_result["tests"]["bp-RELL"]["score"],
        bp_RELL_significant=iqtree_result["tests"]["bp-RELL"]["significant"],
        p_KH=iqtree_result["tests"]["p-KH"]["score"],
        p_KH_significant=iqtree_result["tests"]["p-KH"]["significant"],
        p_SH=iqtree_result["tests"]["p-SH"]["score"],
        p_SH_significant=iqtree_result["tests"]["p-SH"]["significant"],
        p_WKH=iqtree_result["tests"]["p-WKH"]["score"],
        p_WKH_significant=iqtree_result["tests"]["p-WKH"]["significant"],
        p_WSH=iqtree_result["tests"]["p-WSH"]["score"],
        p_WSH_significant=iqtree_result["tests"]["p-WSH"]["significant"],
        c_ELW=iqtree_result["tests"]["c-ELW"]["score"],
        c_ELW_significant=iqtree_result["tests"]["c-ELW"]["significant"],
        p_AU=iqtree_result["tests"]["p-AU"]["score"],
        p_AU_significant=iqtree_result["tests"]["p-AU"]["significant"],
        total_branch_length=get_total_branch_length_for_tree(newick),
        min_branch_length=get_min_branch_length_for_tree(newick),
        max_branch_length=get_max_branch_length_for_tree(newick),
        std_branch_lengths=get_std_branch_lengths_for_tree(newick),
        avg_branch_lengths=get_avg_branch_lengths_for_tree(newick),
    )


def save_iqtree_tree(search_trees, search_logs, eval_trees, eval_logs, starting_type):
    """
    Save IQ-Tree tree data to database.
    
    Args:
        search_trees: List of search tree paths
        search_logs: List of search log paths  
        eval_trees: List of evaluation tree paths
        eval_logs: List of evaluation log paths
        starting_type: Type of starting tree ("parsimony" or "random")
    
    Returns:
        List of likelihoods for plausible trees
    """
    plausible_llhs = []
    
    for search_tree, search_log, eval_tree, eval_log in zip(search_trees, search_logs, eval_trees, eval_logs):
        with open(search_tree) as f:
            newick_search = f.readline().strip()
        
        with open(eval_tree) as f:
            newick_eval = f.readline().strip()
        
        # Create IQ-Tree tree record
        IQTreeTree.create(
            dataset=dataset_name,
            newick_search=newick_search,
            newick_eval=newick_eval,
            starting_type=starting_type,
            llh_search=get_iqtree_llh(search_log),
            compute_time_search=get_iqtree_elapsed_time(search_log),
            total_branch_length_search=get_total_branch_length_for_tree(newick_search),
            min_branch_length_search=get_min_branch_length_for_tree(newick_search),
            max_branch_length_search=get_max_branch_length_for_tree(newick_search),
            std_branch_lengths_search=get_std_branch_lengths_for_tree(newick_search),
            avg_branch_lengths_search=get_avg_branch_lengths_for_tree(newick_search),
            llh_eval=get_iqtree_llh(eval_log),
            compute_time_eval=get_iqtree_elapsed_time(eval_log),
            total_branch_length_eval=get_total_branch_length_for_tree(newick_eval),
            min_branch_length_eval=get_min_branch_length_for_tree(newick_eval),
            max_branch_length_eval=get_max_branch_length_for_tree(newick_eval),
            std_branch_lengths_eval=get_std_branch_lengths_for_tree(newick_eval),
            avg_branch_lengths_eval=get_avg_branch_lengths_for_tree(newick_eval),
        )
        
        # Check if this tree is plausible based on IQ-Tree results
        iqtree_result, _ = get_iqtree_results_for_eval_tree_str(iqtree_results, newick_eval, clusters)
        if iqtree_result["plausible"]:
            plausible_llhs.append(get_iqtree_llh(eval_log))
    
    return plausible_llhs


# Save search and evaluation trees
plausible_llhs_pars = save_iqtree_tree(pars_search_trees, pars_search_logs, pars_eval_trees, pars_eval_logs, "parsimony")
plausible_llhs_rand = save_iqtree_tree(rand_search_trees, rand_search_logs, rand_eval_trees, rand_eval_logs, "random")

# Update dataset with plausible likelihoods
dataset = Dataset.get(Dataset.name == dataset_name)
dataset.avg_plausible_llh_pars = np.mean(plausible_llhs_pars) if plausible_llhs_pars else None
dataset.std_plausible_llh_pars = np.std(plausible_llhs_pars) if plausible_llhs_pars else None
dataset.avg_plausible_llh_rand = np.mean(plausible_llhs_rand) if plausible_llhs_rand else None
dataset.std_plausible_llh_rand = np.std(plausible_llhs_rand) if plausible_llhs_rand else None
dataset.save()

db.close()
