from utils import read_file_contents
import regex
from custom_types import FilePath

def get_iqtree_llh(log_file: FilePath) -> float:
    """Extract final log-likelihood from IQ-TREE log."""
    for line in reversed(read_file_contents(log_file)):
        if "Optimal log-likelihood" in line or "BEST SCORE FOUND" in line:
            match = regex.search(r"([-+]?\d+\.\d+)", line)
            if match:
                return float(match.group(1))
    raise ValueError(f"Log-likelihood not found in {log_file}")

def get_all_iqtree_llhs(log_list_file: FilePath) -> list[float]:
    """Read list of log paths and extract log-likelihoods from each."""
    log_paths = read_file_contents(log_list_file)
    return [get_iqtree_llh(path) for path in log_paths]
