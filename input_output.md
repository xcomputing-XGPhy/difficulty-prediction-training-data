
# Pipeline Rule Input-Output Relationships

---

## Summary Table

| Rule                      | Inputs                                    | Outputs                              | Next Step(s)                  |
|---------------------------|-------------------------------------------|--------------------------------------|-------------------------------|
| Tree Inference            | MSA, model, seed                          | .treefile, .iqtree, .log, .vanvan    | Tree Evaluation, Collect Data |
| Tree Evaluation           | .treefile, .vanvan                        | .treefile, .log, .iqtree             | Collect Data                  |
| Collect Data              | .treefile, .vanvan, .log                  | AllSearchTrees.trees, AllEvalTrees.trees, AllSearchLogs.log | RFDistance, Significance Tests|
| RFDistance Calculation    | AllSearchTrees.trees, AllEvalTrees.trees  | .rfDistances.log                     | Significance Tests            |
| Significance Tests        | AllEvalTrees.trees, .rfDistances.log, best tree | filteredEvalTrees.trees, clusters.pkl, significance.iqtree | Data Saving                   |
| MSA Feature Extraction    | MSA, model                                | msa_features.json                    | Data Saving                   |
| Parsimony Tree Inference  | MSA, model, seed                          | .raxml.startTree, .raxml.log         | Data Saving                   |
| Data Saving               | All above outputs                         | {msa}_data.sqlite3                   | Final output                  |

---

## Step-by-Step Details


### 1. Tree Inference
#### Input
- MSA file
- Model
- Seed
#### Output
- Best tree (.treefile)
- Starting tree (.iqtree)
- Model file (.model.gz)
- Log file (.log)
- Random tree (.vanvan), random log

--- 

### 2. Tree Evaluation
#### Input
- Best tree from inference (.treefile or .vanvan)
#### Output
- Evaluation log (.log)
- Evaluated tree (.treefile)
- IQ-TREE log (.iqtree)

--- 

### 3. Collect Data
#### Input
- All search trees (.treefile, .vanvan)
- All search logs (.log)
- All eval trees (.treefile)
#### Output
- Concatenated tree files (AllSearchTrees.trees, AllEvalTrees.trees)
- Concatenated log files (AllSearchLogs.log)

---

### 4. RFDistance Calculation
#### Input
- All search trees (AllSearchTrees.trees)
- All eval trees (AllEvalTrees.trees)
#### Output
- RFDistance logs (inference.raxml.rfDistances.log, eval.raxml.rfDistances.log)

---

### 5. Significance Tests & Clustering
#### Input
- All eval trees (AllEvalTrees.trees)
- RFDistance logs
- Best tree from evaluation
#### Output
- Filtered trees (filteredEvalTrees.trees)
- Cluster assignments (filteredEvalTrees.clusters.pkl)
- Significance test results (significance.iqtree)
- Significance log

---

### 6. MSA Feature Extraction
#### Input
- MSA file
- Model
#### Output
- MSA features (msa_features.json)

---

### 7. Parsimony Tree Inference
#### Input
- MSA file
- Model
- Seed
#### Output
- Parsimony tree (.raxml.startTree)
- Parsimony log (.raxml.log)

---

### 8. Data Saving
#### Input
- All search trees/logs
- RFDistance logs
- All eval trees/logs
- Plausible tree logs
- Significance test results
- Cluster assignments
- MSA features
- Parsimony trees/logs
#### Output
- Final database ({msa}_data.sqlite3)


### 1. Tree Files (.treefile, .vanvan, .raxml.startTree)
Extract:
Tree topology (Newick string)
Branch lengths
Tree ID or seed
### 2. Log Files (.log, .iqtree, .raxml.log)
Extract:
Log-likelihood score (for each tree)
Parsimony score (if applicable)
Model parameters used
Runtime statistics (time, memory)
Any warnings/errors
### 3. RFDistance Logs (.rfDistances.log)
Extract:
RF distance values between tree pairs
### 4. MSA Feature Files (msa_features.json)
Extract:
Sequence length
Number of taxa
Diversity metrics
Any other computed features
### 5. Cluster Files (filteredEvalTrees.clusters.pkl)
Extract:
Cluster assignment for each tree
### 6. Significance Test Results (significance.iqtree)
Extract:
Test statistics (e.g., p-values)
Plausibility flag for each tree
### 7. Parsimony Tree Files (.raxml.startTree)
Extract:
Tree topology (Newick)
Parsimony score
### 8. Metadata
Extract:
MSA name/ID
Seed value
Model name