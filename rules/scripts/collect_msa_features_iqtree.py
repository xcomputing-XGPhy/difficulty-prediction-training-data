import json

from pypythia.msa import MSA
from pypythia_iqtree import IQTree

msa_file = snakemake.params.msa
model = snakemake.params.model

msa = MSA(msa_file)

# the Biopython DistanceCalculator does not support morphological data
# so for morphological data we cannot compute the treelikeness at the moment
compute_treelikeness = msa.data_type != "MORPH"

data_type_str = getattr(msa.data_type, "name", str(msa.data_type)).replace("DataType.", "")
sequence_type = {"DNA": "DNA", "AA": "AA", "MORPH": "MORPH"}.get(data_type_str, None)
iqtree = IQTree(snakemake.params.iqtree_command)

patterns, gaps, invariant = iqtree.get_patterns_gaps_invariant(msa_file, model,sequence_type=sequence_type)

msa_features = {
    "data_type": str(msa.data_type),
    "taxa": msa.number_of_taxa(),
    "sites": msa.number_of_sites(),
    "patterns": patterns,
    "gaps": gaps,
    "invariant": invariant,
    "entropy": msa.entropy(),
    "column_entropies": msa.column_entropies(),
    "bollback": msa.bollback_multinomial(),
    "treelikeness": msa.treelikeness_score() if compute_treelikeness else None,
}

with open(snakemake.output.msa_features, "w") as f:
    json.dump(msa_features, f)
