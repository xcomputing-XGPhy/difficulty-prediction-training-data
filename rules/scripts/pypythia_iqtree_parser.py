from pypythia.custom_types import *
from pypythia.utils import get_value_from_line
import re


def get_patterns_gaps_invariant(log_file: FilePath) -> Tuple[int, float, float]:
    """Method that parses the number of patterns, proportion of gaps, and proportion of invariant sites in the given log_file.

    Args:
        log_file (str): Filepath of an IQ-TREE log file.

    Returns:
        n_patterns (int): Number of unique patterns in the given MSA. 
        prop_gaps (float): Proportion of gaps in the given MSA.
        prop_inv (float): Proportion of invariant sites in the given MSA.

    Raises:
        ValueError: If the given log file does not contain the number of patterns, proportion of gaps or proportion of invariant sites.
    """
    patterns = None
    gaps = None
    invariant = None
    n_cols = None  # dùng để tính tỉ lệ invariant khi IQ-TREE chỉ in số lượng site hằng

    for raw in open(log_file, "r", encoding="utf-8", errors="ignore").readlines():
        line = raw.strip()

        # number of alignment patterns
        # IQ-TREE 3.x ví dụ:
        # Alignment has 26 sequences with 430 columns, 355 distinct patterns
        if "distinct patterns" in line:
            # lấy số đứng ngay trước "distinct patterns"
            m = re.search(r"(\d+)\s+distinct patterns", line, flags=re.I)
            if m:
                patterns = int(m.group(1))
            # đồng thời lấy tổng số cột để tính tỉ lệ invariant phía dưới
            mcols = re.search(r"with\s+(\d+)\s+columns", line, flags=re.I)
            if mcols:
                n_cols = int(mcols.group(1))

        # proportion invariant sites
        # IQ-TREE 3.x ví dụ:
        # 243 parsimony-informative, 60 singleton sites, 127 constant sites
        # -> invariant = 127 / 430
        if "constant sites" in line or "invariant sites" in line:
            # bắt số đứng trước 'constant sites' hoặc 'invariant sites'
            m = re.search(r"(\d+)\s+(?:constant|invariant)\s+sites", line, flags=re.I)
            if m:
                n_const = int(m.group(1))
                # cần n_cols (đã lấy ở dòng "Alignment has ... columns")
                if n_cols is not None and n_cols > 0:
                    invariant = n_const / n_cols

        # proportion of gaps
        # IQ-TREE 3.x in bảng "Gap/Ambiguity  Composition  p-value" với dòng tổng:
        # ****  TOTAL                                     41.55%  ...
        if line.startswith("*") and "TOTAL" in line and "%" in line:
            # lấy phần trăm đầu tiên trong dòng
            m = re.search(r"([0-9]*\.?[0-9]+)%", line)
            if m:
                gaps = float(m.group(1)) / 100.0

        # Fallback (một số build có thể in dạng khác):
        # Overall gap/ambiguity: 41.55%
        if gaps is None and ("gap" in line.lower() or "ambiguity" in line.lower()) and "%" in line:
            if "overall" in line.lower():
                m = re.search(r"([0-9]*\.?[0-9]+)%", line)
                if m:
                    gaps = float(m.group(1)) / 100.0

    if patterns is None or gaps is None or invariant is None:
        raise ValueError("Error parsing IQ-TREE log")

    return patterns, gaps, invariant


def get_iqtree_rfdist_results(log_file: FilePath) -> Tuple[float, float, float]:
    """Method that parses the number of unique topologies, relative RF-Distance, and absolute RF-Distance in the given log file.

    Args:
        log_file (str): Filepath of an IQ-TREE RF-distance log file.

    Returns:
        num_topos (int): Number of unique topologies of the given set of trees.
        rel_rfdist (float): Relative RF-Distance of the given set of trees. Computed as average over all pairwise RF-Distances. Value between 0.0 and 1.0.
        abs_rfdist (float): Absolute RF-Distance of the given set of trees.

    Raises:
        ValueError: If the given log file does not contain the unique topologies, relative RF-Distance, or absolute RF-Distance.
    """
    abs_rfdist = None
    rel_rfdist = None
    num_topos = None

    for raw in open(log_file, "r", encoding="utf-8", errors="ignore").readlines():
        line = raw.strip()

        # Number of unique topologies: 12
        if "Number of unique topologies" in line:
            # lấy số sau dấu ':'
            num_topos = int(get_value_from_line(line, "Number of unique topologies:"))

        # Average RF distance: 18.42 (relative 0.276)
        if "Average RF distance:" in line and "relative" in line:
            # lấy abs đứng sau dấu ':' và trước '('
            try:
                after = line.split(":", 1)[1].strip()
                abs_str = after.split("(", 1)[0].strip()
                abs_rfdist = float(abs_str)
            except Exception:
                pass
            # lấy rel trong ngoặc sau từ khóa 'relative'
            m = re.search(r"relative\s+([0-9]*\.?[0-9]+)", line, flags=re.I)
            if m:
                rel_rfdist = float(m.group(1))

        # Average relative RF distance: 0.276 (absolute 18.42)
        if "Average relative RF distance:" in line and "absolute" in line:
            # lấy rel sau dấu ':'
            try:
                rel_rfdist = float(get_value_from_line(line, "Average relative RF distance:"))
            except Exception:
                pass
            # lấy abs trong ngoặc sau từ khóa 'absolute'
            m = re.search(r"absolute\s+([0-9]*\.?[0-9]+)", line, flags=re.I)
            if m:
                abs_rfdist = float(m.group(1))

    if abs_rfdist is None or rel_rfdist is None or num_topos is None:
        raise ValueError("Error parsing IQ-TREE RF-distance log.")

    return num_topos, rel_rfdist, abs_rfdist
