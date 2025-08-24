from pypythia.custom_types import *
import re


def get_patterns_gaps_invariant(log_file: FilePath) -> Tuple[int, float, float]:
    """
    Parse number of patterns, proportion of gaps, and invariant sites from an IQ-TREE log file.

    Args:
        log_file (str): Path to IQ-TREE log file.

    Returns:
        n_patterns (int): Number of unique patterns.
        prop_gaps (float): Proportion of gaps (0.0 - 1.0).
        prop_inv (float): Proportion of invariant sites (0.0 - 1.0).
    """
    patterns = None
    gaps = None
    invariant = None

    with open(log_file, "r") as f:
        for line in f:
            if line.startswith("Alignment sites"):
                # Example: Alignment sites / patterns: 1940 / 933
                try:
                    _, numbers = line.split(":")
                    parts = [int(x.strip()) for x in numbers.split("/") if x.strip()]
                    if len(parts) == 2:
                        _, patterns = parts
                except Exception:
                    continue
            elif line.startswith("Gaps"):
                # Example: Gaps: 12.5%
                try:
                    _, value = line.split(":")
                    perc = re.findall(r"[\d.]+", value)
                    if perc:
                        gaps = float(perc[0]) / 100.0
                except Exception:
                    continue
            elif line.startswith("Invariant sites") or line.startswith("Constant sites"):
                # Example: Invariant sites: 45.2%
                try:
                    _, value = line.split(":")
                    perc = re.findall(r"[\d.]+", value)
                    if perc:
                        invariant = float(perc[0]) / 100.0
                except Exception:
                    continue

    if patterns is None or gaps is None or invariant is None:
        raise ValueError(f"Error parsing IQ-TREE log file: {log_file}")

    return patterns, gaps, invariant


def get_iqtree_rfdist_results(log_file: FilePath) -> Tuple[float, float, float]:
    """
    Parse RF distances and number of topologies from IQ-TREE RF distance log file.

    Args:
        log_file (str): Path to IQ-TREE RF distance log.

    Returns:
        num_topos (int): Number of topologies compared.
        rel_rfdist (float): Average relative RF distance.
        abs_rfdist (float): Average absolute RF distance.
    """
    abs_rfdist = []
    rel_rfdist = []

    with open(log_file, "r") as f:
        for line in f:
            line = line.strip()
            if "Robinson-Foulds" in line or "RF distance" in line:
                try:
                    values = re.findall(r"[\d.]+", line)
                    if len(values) == 2:
                        abs_rfdist.append(float(values[0]))
                        rel_rfdist.append(float(values[1]))
                except Exception:
                    continue

    if not abs_rfdist or not rel_rfdist:
        raise ValueError(f"Error parsing RF distances from IQ-TREE log: {log_file}")

    return len(abs_rfdist), np.mean(rel_rfdist), np.mean(abs_rfdist)
