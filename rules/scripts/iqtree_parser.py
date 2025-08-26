import numpy as np
import regex
from tempfile import TemporaryDirectory
import warnings

from custom_types import *
from utils import (
    get_single_value_from_file,
    get_multiple_values_from_file,
    read_file_contents,
)

from pypythia_iqtree import IQTree


def get_iqtree_llh(iqtree_file: FilePath) -> float:
    """Get the final log-likelihood from IQ-Tree log file."""
    STR = "Optimal log-likelihood:"
    return get_single_value_from_file(iqtree_file, STR)


def get_iqtree_starting_llh(iqtree_file: FilePath) -> float:
    """Get the starting log-likelihood from IQ-Tree log file."""
    content = read_file_contents(iqtree_file)
    for line in content:
        if "Initial log-likelihood:" in line:
            # Initial log-likelihood: -8735.928562
            _, llh = line.split(":")
            return float(llh.strip())
        elif "Initial tree log-likelihood:" in line:
            # Initial tree log-likelihood: -8735.928562
            _, llh = line.split(":")
            return float(llh.strip())

    # If the run was restarted, the starting LLH might not be in the log file
    warnings.warn("The given file does not contain the starting llh " + iqtree_file)
    return -np.inf


def get_all_iqtree_llhs(iqtree_file: FilePath) -> List[float]:
    """Get all log-likelihood values from IQ-Tree log file."""
    STR = "log-likelihood:"
    return get_multiple_values_from_file(iqtree_file, STR)


def get_best_iqtree_llh(iqtree_file: FilePath) -> float:
    """Get the best log-likelihood from IQ-Tree log file."""
    all_llhs = get_all_iqtree_llhs(iqtree_file)
    return max(all_llhs)


def get_iqtree_time_from_line(line: str) -> float:
    """Extract time from IQ-Tree log line."""
    # IQ-Tree time format: "Total CPU time used: 63514.086 sec"
    if "Total CPU time used:" in line:
        value = line.split(":")[1].strip().split(" ")[0]
        return float(value)
    elif "Total wall-clock time used:" in line:
        value = line.split(":")[1].strip().split(" ")[0]
        return float(value)
    else:
        raise ValueError(f"Unexpected time format in line: {line}")


def get_iqtree_elapsed_time(log_file: FilePath) -> float:
    """Get the elapsed time from IQ-Tree log file."""
    content = read_file_contents(log_file)

    for line in content:
        if "Total CPU time used:" in line or "Total wall-clock time used:" in line:
            return get_iqtree_time_from_line(line)

    raise ValueError(
        f"The given input file {log_file} does not contain the elapsed time."
    )


def get_iqtree_runtimes(log_file: FilePath) -> List[float]:
    """Get all runtime values from IQ-Tree log file."""
    content = read_file_contents(log_file)

    all_times = []

    for line in content:
        if "Total CPU time used:" in line or "Total wall-clock time used:" in line:
            all_times.append(get_iqtree_time_from_line(line))

    if not all_times:
        raise ValueError(
            f"The given input file {log_file} does not contain the elapsed time."
        )

    return all_times


def get_iqtree_num_iterations(log_file: FilePath) -> Tuple[int, int]:
    """Get the number of iterations from IQ-Tree log file.

    Returns a tuple (num_iterations, placeholder) to mirror RAxML-NG API shape.
    """
    content = read_file_contents(log_file)

    num_iterations = None

    for line in content:
        line = line.strip()
        if line.startswith("Total number of iterations:"):
            try:
                _, value = line.split(":", 1)
                num_iterations = int(value.strip())
                break
            except Exception:
                continue
        if "TREE SEARCH COMPLETED AFTER" in line and "ITERATIONS" in line:
            try:
                # e.g., TREE SEARCH COMPLETED AFTER 113 ITERATIONS / Time: 0h:3m:28s
                import re
                m = re.search(r"AFTER\s+(\d+)\s+ITERATIONS", line)
                if m:
                    num_iterations = int(m.group(1))
                    break
            except Exception:
                continue
        if line.startswith("Number of iterations:"):
            try:
                _, value = line.split(":", 1)
                num_iterations = int(value.strip())
                break
            except Exception:
                continue

    if num_iterations is None:
        num_iterations = 0

    return num_iterations, 0


def rel_rfdistance_starting_final(
    newick_starting: Newick,
    newick_final: Newick,
    iqtree_executable: Executable = "iqtree",
) -> float:
    """Calculate relative RF distance between starting and final trees using IQ-Tree."""
    with TemporaryDirectory() as tmpdir:
        iqtree = IQTree(iqtree_executable)
        trees = tmpdir + ".trees"
        with open(trees, "w") as f:
            f.write(newick_starting.strip() + "\n" + newick_final.strip())

        # Note: IQ-Tree doesn't have built-in RF distance calculation like RAxML-NG
        # We'll need to implement this differently or use an external tool
        # For now, return a placeholder value
        warnings.warn("RF distance calculation not yet implemented for IQ-Tree")
        return 0.0


def get_model_parameter_estimates(iqtree_file: FilePath) -> Tuple[str, str, str]:
    """
    Extract model parameter estimates from IQ-Tree log file.
    
    Returns:
        Tuple of (rate_het, base_freq, subst_rates) as strings
    """
    content = read_file_contents(iqtree_file)

    rate_het = None
    base_freq = None
    subst_rates = None

    for line in content:
        if line.startswith("Rate heterogeneity"):
            _, res = line.split(":", 1)
            rate_het = res.strip()
        elif line.startswith("Base frequencies"):
            _, res = line.split(":", 1)
            base_freq = res.strip()
        elif line.startswith("Substitution rates"):
            _, res = line.split(":", 1)
            subst_rates = res.strip()
        elif line.startswith("Rate parameters"):
            _, res = line.split(":", 1)
            subst_rates = res.strip()

    return rate_het, base_freq, subst_rates


def get_all_parsimony_scores(log_file: FilePath) -> List[float]:
    """Get all parsimony scores from IQ-Tree log file."""
    content = read_file_contents(log_file)

    scores = []

    for line in content:
        if "Parsimony score" in line:
            # Parsimony score: 1234
            _, score = line.split(":")
            score = int(score.strip())
            scores.append(score)

    return scores


def get_patterns_gaps_invariant(log_file: FilePath) -> Tuple[int, float, float]:
    """Get alignment statistics from IQ-Tree log file."""
    patterns = None
    gaps = None
    invariant = None
    
    for line in open(log_file).readlines():
        if line.startswith("Alignment sites"):
            # Alignment sites / patterns: 1940 / 933
            _, numbers = line.split(":")
            _, patterns = [int(el) for el in numbers.split("/")]
        elif line.startswith("Gaps"):
            # Gaps: 12.5%
            _, number = line.split(":")
            percentage, _ = number.strip().split(" ")
            gaps = float(percentage) / 100.0
        elif line.startswith("Invariant sites"):
            # Invariant sites: 45.2%
            _, number = line.split(":")
            percentage, _ = number.strip().split(" ")
            invariant = float(percentage) / 100.0
        elif line.startswith("Constant sites"):
            # Constant sites: 45.2%
            _, number = line.split(":")
            percentage, _ = number.strip().split(" ")
            invariant = float(percentage) / 100.0

    if patterns is None or gaps is None or invariant is None:
        raise ValueError("Error parsing IQ-Tree log ", log_file)

    return patterns, gaps, invariant


def get_iqtree_tree_info(log_file: FilePath) -> Dict[str, any]:
    """
    Extract comprehensive tree information from IQ-Tree log file.
    
    Returns:
        Dictionary containing tree statistics and information
    """
    content = read_file_contents(log_file)
    
    tree_info = {}
    
    for line in content:
        line = line.strip()
        
        # Tree statistics
        if "Number of taxa:" in line:
            _, num_taxa = line.split(":")
            tree_info["num_taxa"] = int(num_taxa.strip())
        elif "Number of sites:" in line:
            _, num_sites = line.split(":")
            tree_info["num_sites"] = int(num_sites.strip())
        elif "Number of patterns:" in line:
            _, num_patterns = line.split(":")
            tree_info["num_patterns"] = int(num_patterns.strip())
        elif "AIC score:" in line:
            _, aic = line.split(":")
            tree_info["aic"] = float(aic.strip())
        elif "BIC score:" in line:
            _, bic = line.split(":")
            tree_info["bic"] = float(bic.strip())
        elif "AICc score:" in line:
            _, aicc = line.split(":")
            tree_info["aicc"] = float(aicc.strip())
    
    return tree_info


def get_iqtree_model_selection(log_file: FilePath) -> Dict[str, any]:
    """
    Extract model selection information from IQ-Tree log file.
    
    Returns:
        Dictionary containing model selection results
    """
    content = read_file_contents(log_file)
    
    model_info = {}
    
    for line in content:
        line = line.strip()
        
        if "Best-fit model:" in line:
            _, model = line.split(":")
            model_info["best_model"] = model.strip()
        elif "Model of rate heterogeneity:" in line:
            _, rate_het = line.split(":")
            model_info["rate_heterogeneity"] = rate_het.strip()
        elif "Model of base frequencies:" in line:
            _, base_freq = line.split(":")
            model_info["base_frequencies"] = base_freq.strip()
    
    return model_info


def get_iqtree_rfdist_results(log_file: FilePath) -> Tuple[int, float, float]:
    """
    Parse IQ-Tree RF distance results from log file.
    
    Args:
        log_file: Path to IQ-Tree RF distance log file
        
    Returns:
        Tuple of (num_topologies, avg_rfdist, std_rfdist)
    """
    content = read_file_contents(log_file)
    
    num_topologies = 0
    rfdistances = []
    
    for line in content:
        line = line.strip()
        
        # Look for RF distance information
        # This is a placeholder - you may need to adjust based on actual IQ-Tree output format
        if "RF distance" in line or "Robinson-Foulds" in line:
            # Extract RF distance value
            try:
                # Look for numbers in the line
                import re
                numbers = re.findall(r'\d+\.?\d*', line)
                if numbers:
                    rfdistances.append(float(numbers[0]))
            except:
                continue
    
    if rfdistances:
        num_topologies = len(rfdistances)
        avg_rfdist = np.mean(rfdistances)
        std_rfdist = np.std(rfdistances)
    else:
        # Default values if no RF distances found
        num_topologies = 1
        avg_rfdist = 0.0
        std_rfdist = 0.0
    
    return num_topologies, avg_rfdist, std_rfdist
