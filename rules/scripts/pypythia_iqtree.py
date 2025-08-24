from pypythia.custom_types import *
from pypythia_custom_errors import IQTreeError
from pypythia_iqtree_parser import *

from tempfile import TemporaryDirectory
import os
import subprocess


def run_iqtree_command(cmd: Command) -> None:
    try:
        subprocess.check_output(cmd, encoding="utf-8")
    except subprocess.CalledProcessError as e:
        raise IQTreeError(subprocess_exception=e)
    except Exception as e:
        raise RuntimeError("Running IQ-Tree command failed.") from e


class IQTree:
    """Class structure for features computed using IQ-Tree.

    This class provides methods for computing MSA attributes using IQ-Tree.

    Args:
        exe_path (Executable): Path to an executable of IQ-Tree. See http://www.iqtree.org for install instructions.

    Attributes:
        exe_path (Executable): Path to an executable of IQ-Tree.
    """

    def __init__(self, exe_path: Executable):
        self.exe_path = exe_path

    def _base_cmd(
            self, msa_file: FilePath, model: Model, prefix: str, **kwargs
    ) -> Command:
        additional_settings = []
        for key, value in kwargs.items():
            if value is None:
                additional_settings += [f"-{key}"]
            else:
                additional_settings += [f"-{key}", str(value)]

        return [
            self.exe_path,
            "-s",
            msa_file,
            "-m",
            model,
            "-pre",
            prefix,
            *additional_settings,
        ]

    def _run_alignment_parse(
            self, msa_file: FilePath, model: Model, prefix: str, **kwargs
    ) -> None:
        cmd = self._base_cmd(msa_file, model, prefix, **kwargs)
        run_iqtree_command(cmd)

    def _run_rfdist(self, trees_file: FilePath, prefix: str, **kwargs) -> None:
        additional_settings = []
        for key, value in kwargs.items():
            if value is None:
                additional_settings += [f"-{key}"]
            else:
                additional_settings += [f"-{key}", str(value)]
        cmd = [
            self.exe_path,
            "-rfdist",
            trees_file,
            "-pre",
            prefix,
            *additional_settings,
        ]
        run_iqtree_command(cmd)

    def infer_parsimony_trees(
            self,
            msa_file: FilePath,
            model: Model,
            prefix: str,
            n_trees: int = 100,
            **kwargs,
    ) -> FilePath:
        """Method that infers n_trees using the IQ-Tree implementation of maximum parsimony.

        Args:
            msa_file (str): Filepath of the MSA to compute the parsimony trees for.
            model (str): String representation of the substitution model to use. Needs to be a valid IQ-Tree model. For example "GTR+G" for DNA data or "LG+G" for protein data.
            prefix (str): Prefix of where to store the IQ-Tree results.
            n_trees (int): Number of parsimony trees to compute.
            **kwargs: Optional additional IQ-Tree settings.
                The name of the kwarg needs to be a valid IQ-Tree flag.
                For flags with a value pass it like this: "flag=value", for flags without a value pass it like this: "flag=None".
                See http://www.iqtree.org for all options.

        Returns:
            output_trees_file (str): Filepath pointing to the computed trees.

        """
        cmd = self._base_cmd(
            msa_file, model, prefix, start=None, tree=f"pars{{{n_trees}}}", **kwargs
        )
        run_iqtree_command(cmd)
        return prefix + ".treefile"

    def get_rfdistance_results(
            self, trees_file: FilePath, prefix: str = None, **kwargs
    ) -> Tuple[float, float, float]:
        """Method that computes the number of unique topologies, relative RF-Distance, and absolute RF-Distance for the given set of trees.

        Args:
            trees_file: Filepath of a file containing > 1 Newick strings.
            prefix (str): Optional prefix to use when running IQ-Tree

        Returns:
            num_topos (float): Number of unique topologies of the given set of trees.
            rel_rfdist (float): Relative RF-Distance of the given set of trees. Computed as average over all pairwise RF-Distances. Value between 0.0 and 1.0.
            abs_rfdist (float): Absolute RF-Distance of the given set of trees.
        """
        with TemporaryDirectory() as tmpdir:
            if not prefix:
                prefix = os.path.join(tmpdir, "rfdist")
            self._run_rfdist(trees_file, prefix, **kwargs)
            log_file = prefix + ".log"
            return get_iqtree_rfdist_results(log_file)

    def get_patterns_gaps_invariant(
            self, msa_file: FilePath, model: Model, prefix: str = None
    ) -> Tuple[int, float, float]:
        """Method that obtains the number of patterns, proportion of gaps, and proportion of invariant sites in the given MSA.

        Args:
            msa_file (str): Filepath of the MSA to compute the parsimony trees for.
            model (str): String representation of the substitution model to use. Needs to be a valid IQ-Tree model. For example "GTR+G" for DNA data or "LG+G" for protein data.
            prefix (str): Optional prefix to use when running IQ-Tree

        Returns:
            n_patterns (int): Number of unique patterns in the given MSA.
            prop_gaps (float): Proportion of gaps in the given MSA.
            prop_inv (float): Proportion of invariant sites in the given MSA.
        """
        with TemporaryDirectory() as tmpdir:
            if not prefix:
                prefix = os.path.join(tmpdir, "parse")
            self._run_alignment_parse(msa_file, model, prefix)
            return get_patterns_gaps_invariant(f"{prefix}.log")

    def infer_tree(
            self,
            msa_file: FilePath,
            model: Model,
            prefix: str,
            starting_tree: str = "pars",
            **kwargs,
    ) -> FilePath:
        """Method that infers a single tree using IQ-Tree.

        Args:
            msa_file (str): Filepath of the MSA to compute the tree for.
            model (str): String representation of the substitution model to use.
            prefix (str): Prefix of where to store the IQ-Tree results.
            starting_tree (str): Type of starting tree. Options: "pars" (parsimony), "rand" (random), "bionj" (BIONJ).
            **kwargs: Optional additional IQ-Tree settings.

        Returns:
            output_tree_file (str): Filepath pointing to the computed tree.
        """
        cmd = self._base_cmd(
            msa_file, model, prefix, start=starting_tree, **kwargs
        )
        run_iqtree_command(cmd)
        return prefix + ".treefile"

    def evaluate_tree(
            self,
            msa_file: FilePath,
            tree_file: FilePath,
            model: Model,
            prefix: str,
            **kwargs,
    ) -> FilePath:
        """Method that evaluates a given tree using IQ-Tree.

        Args:
            msa_file (str): Filepath of the MSA.
            tree_file (str): Filepath of the tree to evaluate.
            model (str): String representation of the substitution model to use.
            prefix (str): Prefix of where to store the IQ-Tree results.
            **kwargs: Optional additional IQ-Tree settings.

        Returns:
            output_log_file (str): Filepath pointing to the evaluation log.
        """
        cmd = [
            self.exe_path,
            "-s", msa_file,
            "-t", tree_file,
            "-m", model,
            "-pre", prefix,
            "-n", "0",  # No tree search, just evaluation
        ]
        # Add additional kwargs
        for k, v in kwargs.items():
            if v is None:
                cmd.append(f"-{k}")
            else:
                cmd.extend([f"-{k}", str(v)])
        run_iqtree_command(cmd)
        return prefix + ".log"

    def run_significance_tests(
            self,
            msa_file: FilePath,
            trees_file: FilePath,
            reference_tree: FilePath,
            model: Model,
            prefix: str,
            **kwargs,
    ) -> FilePath:
        """Method that runs statistical significance tests on a set of trees.

        Args:
            msa_file (str): Filepath of the MSA.
            trees_file (str): Filepath containing multiple trees to test.
            reference_tree (str): Filepath of the reference tree.
            model (str): String representation of the substitution model to use.
            prefix (str): Prefix of where to store the IQ-Tree results.
            **kwargs: Optional additional IQ-Tree settings.

        Returns:
            output_summary_file (str): Filepath pointing to the test summary.
        """
        cmd = [
            self.exe_path,
            "-s", msa_file,
            "-z", trees_file,
            "-te", reference_tree,
            "-m", model,
            "-pre", prefix,
            "-n", "0",  # No tree search
            "-zb", "10000",  # Bootstrap replicates
            "-zw",  # Weighted tests
            "-au",  # Approximately unbiased test
        ]
        # Add additional kwargs
        for k, v in kwargs.items():
            if v is None:
                cmd.append(f"-{k}")
            else:
                cmd.extend([f"-{k}", str(v)])
        run_iqtree_command(cmd)
        return prefix + ".iqtree"

    def get_tree_info(
            self, log_file: FilePath
    ) -> Dict[str, any]:
        """Method that extracts comprehensive tree information from IQ-Tree log file.

        Args:
            log_file (str): Filepath of the IQ-Tree log file.

        Returns:
            tree_info (dict): Dictionary containing tree statistics and information.
        """
        return get_iqtree_tree_info(log_file)

    def get_model_selection(
            self, log_file: FilePath
    ) -> Dict[str, any]:
        """Method that extracts model selection information from IQ-Tree log file.

        Args:
            log_file (str): Filepath of the IQ-Tree log file.

        Returns:
            model_info (dict): Dictionary containing model selection results.
        """
        return get_iqtree_model_selection(log_file)

    def get_likelihood(
            self, log_file: FilePath
    ) -> float:
        """Method that extracts the final log-likelihood from IQ-Tree log file.

        Args:
            log_file (str): Filepath of the IQ-Tree log file.

        Returns:
            llh (float): Final log-likelihood value.
        """
        return get_iqtree_llh(log_file)

    def get_runtime(
            self, log_file: FilePath
    ) -> float:
        """Method that extracts the runtime from IQ-Tree log file.

        Args:
            log_file (str): Filepath of the IQ-Tree log file.

        Returns:
            runtime (float): Runtime in seconds.
        """
        return get_iqtree_elapsed_time(log_file)
