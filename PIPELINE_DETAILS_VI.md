## Pipeline Training Data – Chi tiết đầy đủ các bước và mã được gọi

Tài liệu này trình bày chi tiết toàn bộ pipeline (Snakemake), thứ tự các bước, và chính xác rule/script/command nào được gọi ở mỗi bước. Kết quả cuối cùng là file Parquet `training_data.parquet` cho mỗi MSA trong `config.yaml`.

### Môi trường và cấu hình
- Cấu hình: `config.yaml`
- Môi trường (thư viện chính): `environment.yml` (có `snakemake`, `pandas`, `pyarrow`, …)
- Mục tiêu cuối trong `Snakefile`:

```12:99:Snakefile
rule all:
    input:
        expand(f"{db_path}training_data.parquet", msa=msa_names)

include: "rules/raxmlng_tree_inference.smk"
include: "rules/raxmlng_tree_evaluation.smk"
include: "rules/collect_data.smk"
include: "rules/raxmlng_rfdistance.smk"
include: "rules/iqtree_significance_tests.smk"
include: "rules/msa_features.smk"
include: "rules/parsimony.smk"
include: "rules/save_data.smk"
```

### Tổng quan dữ liệu đầu ra
- Parquet: `outdir/{msa}/training_data.parquet` – dữ liệu huấn luyện (mỗi dòng = 1 dataset/MSA)
- SQLite: `outdir/{msa}/data.sqlite3` – cơ sở dữ liệu trung gian chi tiết
- Logs & Trees: toàn bộ file từ RAxML-NG và IQ-TREE

---

## Các bước chi tiết của pipeline

### 1) Sinh cây với RAxML-NG (parsimony/random)
File: `rules/raxmlng_tree_inference.smk`

- Parsimony starts (một rule/seed):

```18:26:rules/raxmlng_tree_inference.smk
shell:
    "{raxmlng_command} "
    "--msa {params.msa} "
    "--model {params.model} "
    "--prefix {params.prefix} "
    "--seed {wildcards.seed} "
    "--threads {params.threads} "
    "--tree pars{1} "
    "> {output.raxml_log} "
```

- Random starts (một rule/seed):

```44:51:rules/raxmlng_tree_inference.smk
shell:
    "{raxmlng_command} "
    "--msa {params.msa} "
    "--model {params.model} "
    "--prefix {params.prefix} "
    "--seed {wildcards.seed} "
    "--threads {params.threads} "
    "--tree rand{1} "
    "> {output.raxml_log} "
```

Kết quả: `.raxml.bestTree`, `.raxml.startTree` (parsimony), `.raxml.inference.log`.

### 2) Re-evaluate cây tốt nhất (RAxML-NG)
File: `rules/raxmlng_tree_evaluation.smk`

```19:27:rules/raxmlng_tree_evaluation.smk
shell:
    "{raxmlng_command} "
    "--eval "
    "--tree {input.best_tree_of_run} "
    "--msa {params.msa} "
    "--model {params.model} "
    "--prefix {params.prefix} "
    "--threads {params.threads} "
    "--seed 0 "
    "> {output.eval_log} "
```

Kết quả: `.raxml.eval.log`, `.raxml.bestTree` (đã re-evaluate).

### 3) Gom dữ liệu (cây, log, best tree, plausible)
File: `rules/collect_data.smk`

- Gom search trees/logs:

```5:12:rules/collect_data.smk
output:
    all_search_trees = f"{raxmlng_tree_inference_dir}AllSearchTrees.trees"
shell:
    "cat {input.raxmlng_pars_search_trees} {input.raxmlng_rand_search_trees} > {output.all_search_trees}"
```

- Gom eval trees/logs tương tự (`AllEvalTrees.trees`, `AllEvalLogs.log`).

- Lưu best eval tree – gọi script Python:

```54:66:rules/collect_data.smk
rule save_best_eval_tree:
    ...
    script:
        "scripts/save_best_eval_tree.py"
```

Script chọn cây có log-likelihood cao nhất:

```8:11:rules/scripts/save_best_eval_tree.py
def get_best_tree(all_llhs, all_trees):
    # get the tree with the highest likelihood
    return max(zip(all_llhs, all_trees), key=lambda x: x[0])
```

- Gom plausible trees – gọi script:

```68:79:rules/collect_data.smk
rule collect_plausible_trees:
    ...
    script:
        "scripts/collect_plausible_trees.py"
```

### 4) RF-distance (RAxML-NG)
File: `rules/raxmlng_rfdistance.smk`

- Search/Eval/Parsimony trees:

```15:19:rules/raxmlng_rfdistance.smk
shell:
    "{raxmlng_command} "
    "--rfdist "
    "--tree {input.all_search_trees} "
    "--prefix {params.prefix} "
    ">> {output.rfDist_log} "
```

- Plausible trees (nhánh điều kiện nếu < 2 cây): ghi log giả hoặc gọi `--rfdist` thực sự.

### 5) Lọc topology trùng + IQ-TREE significance tests
File: `rules/iqtree_significance_tests.smk`

- Lọc topology – gọi script:

```10:17:rules/iqtree_significance_tests.smk
script:
    "scripts/filter_tree_topologies.py"
```

- Chạy IQ-TREE tests (AU, SH, …):

```42:56:rules/iqtree_significance_tests.smk
run:
    morph = "-st MORPH " if params.data_type == "MORPH" else ""
    shell("{iqtree_command} "
    "-s {params.msa} "
    "{morph} "
    "{params.model_str} {params.model} "
    "-pre {params.prefix} "
    "-z {input.filtered_trees} "
    "-te {input.best_tree} "
    "-n 0 "
    "-zb 10000 "
    "-zw "
    "-au "
    "-nt {params.threads} "
    "-seed 0 "
    "> {output.iqtree_log} ")
```

### 6) Sinh các cây parsimony (RAxML-NG --start)
File: `rules/parsimony.smk`

```12:22:rules/parsimony.smk
run:
    cmd = [
        "{raxmlng_command} ",
        "--start "
        "--msa {params.msa} ",
        "--tree pars{1} ",
        "--prefix {params.prefix} ",
        "--model {params.model} ",
        "--seed {wildcards.seed} "
        "> {output.log} "
    ]
    shell("".join(cmd))
```

### 7) Tính MSA features
File: `rules/msa_features.smk`

```1:9:rules/msa_features.smk
rule compute_msa_features:
    output:
        msa_features =  f"{output_files_dir}msa_features.json"
    params:
        msa                 = lambda wildcards: msas[wildcards.msa],
        model               = lambda wildcards: raxmlng_models[wildcards.msa],
        raxmlng_command     = raxmlng_command
    script:
        "scripts/collect_msa_features.py"
```

### 8) Lưu dữ liệu vào SQLite và xuất Parquet
File: `rules/save_data.smk`

- Ghi DB SQLite – gọi script:

```1:46:rules/save_data.smk
rule save_data:
    ...
    script:
        "scripts/save_data.py"
```

- Di chuyển DB (workdir → output):

```49:56:rules/save_data.smk
rule move_db:
    input:
        "{msa}_data.sqlite3"
    output:
        database = f"{db_path}data.sqlite3"
    shell:
        "mv {input} {output}"
```

- Chuyển DB → Parquet – gọi script:

```59:69:rules/save_data.smk
rule database_to_training_dataframe:
    input:
        database = rules.move_db.output.database,
    output:
        dataframe = f"{db_path}training_data.parquet"
    params:
        num_pars_trees = num_pars_trees,
        num_rand_trees = num_rand_trees,
        num_parsimony_trees = num_parsimony_trees
    script:
        "scripts/database_to_dataframe.py"
```

Trong `rules/scripts/database_to_dataframe.py`:

- Tạo các cột tỉ lệ và tính nhãn `difficult`:

```58:66:rules/scripts/database_to_dataframe.py
df["num_topos_plausible/num_trees_plausible"]   = df["num_topos_plausible"] / df["num_trees_plausible"]
df["num_topos_parsimony/num_trees_parsimony"]   = df["num_topos_parsimony"] / num_parsimony_trees
df["num_topos_search/num_trees_search"]         = df["num_topos_search"] / num_trees
df["num_topos_eval/num_trees_eval"]             = df["num_topos_eval"] / num_trees
df["num_patterns/num_taxa"]                     = df["num_patterns"] / df["num_taxa"]
df["num_sites/num_taxa"]                        = df["num_sites"] / df["num_taxa"]
df["difficult"] = get_difficulty_labels(df)
```

- Công thức nhãn `difficult` (trung bình các thành phần hợp lệ):

```8:43:rules/scripts/database_to_dataframe.py
def get_difficulty_labels(df: pd.DataFrame) -> List[float]:
    """
    difficult if:
    - avg_rfdist_plausible is close to 1.0 -> + val
    - num_topos_plausible/num_trees_plausible is close to 1.0 -> + val
    - proportion_plausible is closer to 0.0 -> + (1-val)
    """
    labels = []
    for idx, row in df.iterrows():
        diff_proba = 0
        ct = 0
        for col in [
            "avg_rfdist_eval",
            "avg_rfdist_plausible",
            "num_topos_eval/num_trees_eval",
            "num_topos_plausible/num_trees_plausible",
        ]:
            if (row[col] > -np.inf) and (row[col] < np.inf) and (row[col] is not None):
                diff_proba += row[col]
                ct += 1
        for col in [
            "proportion_plausible"
        ]:
            if ((row[col] > -np.inf) and (row[col] < np.inf) and (row[col] is not None)):
                diff_proba += 1 - row[col]
                ct += 1
        labels.append(diff_proba / ct)
    return labels
```

- Ghi Parquet:

```68:69:rules/scripts/database_to_dataframe.py
df.to_parquet(parquet_path)
```

### Schema nguồn (bảng `dataset` trong SQLite)
File: `rules/scripts/database.py` – lớp `Dataset` định nghĩa các trường gốc được ghi vào DB, sau đó được đọc lên DataFrame.

```7:66:rules/scripts/database.py
class Dataset(P.Model):
    uuid = P.UUIDField()
    verbose_name = P.TextField(null=True)
    data_type = P.TextField(null=True)
    # Label features (search/eval/plausible)
    num_searches = P.IntegerField(null=True)
    avg_rfdist_search = P.FloatField(null=True)
    num_topos_search = P.IntegerField(null=True)
    mean_llh_search = P.FloatField(null=True)
    std_llh_search = P.FloatField(null=True)
    avg_rfdist_eval = P.FloatField(null=True)
    num_topos_eval = P.IntegerField(null=True)
    mean_llh_eval = P.FloatField(null=True)
    std_llh_eval = P.FloatField(null=True)
    avg_rfdist_plausible = P.FloatField(null=True)
    num_topos_plausible = P.IntegerField(null=True)
    mean_llh_plausible = P.FloatField(null=True)
    std_llh_plausible = P.FloatField(null=True)
    num_trees_plausible = P.IntegerField(null=True)
    proportion_plausible = P.FloatField(null=True)
    # Single inference / MSA / Parsimony features ...
```

### Tên nhãn và lưu ý khi dùng feature
- Tên cột nhãn: `features.py`

```4:4:features.py
LABEL = "difficult"
```

- Các feature dùng để sinh nhãn nằm trong `LABEL_GENERATION_FEATURES`. Khi huấn luyện, không nên dùng các cột này cùng với `LABEL` để tránh rò rỉ thông tin.

### Đọc dữ liệu kết quả

```python
import pandas as pd
df = pd.read_parquet("training_data.parquet")  # yêu cầu pyarrow hoặc fastparquet
print(df.shape)
print(df.dtypes)
print(df.columns.tolist())
print(df[["difficult"]].head())
```

---

## Tóm tắt luồng thực thi
1. RAxML-NG: Inference (parsimony/random) → Re-evaluate best trees
2. Gom dữ liệu: trees/logs, chọn best eval tree, plausible trees
3. RF-distance (RAxML-NG) + Lọc topo + IQ-TREE significance tests
4. Parsimony trees + MSA features
5. Lưu SQLite (`save_data.py`) → Chuyển DB → Sinh nhãn & cột dẫn xuất → Xuất Parquet (`database_to_dataframe.py`)


