Tôi sẽ phân tích pipeline training data để hiểu cách hoạt động và thứ tự các bước được thực hiện. Hãy để tôi xem xét các file chính của pipeline.

Read file: Snakefile
Bây giờ hãy xem các rule files để hiểu chi tiết từng bước:

Read file: rules/collect_data.smk
Read file: rules/save_data.smk
Read file: rules/raxmlng_tree_inference.smk
Read file: rules/raxmlng_tree_evaluation.smk
Read file: rules/iqtree_significance_tests.smk
Read file: rules/msa_features.smk
Read file: rules/parsimony.smk
Read file: rules/raxmlng_rfdistance.smk
Bây giờ hãy xem file config để hiểu các tham số:

Read file: config.yaml
Dựa trên việc phân tích các file, tôi có thể giải thích pipeline training data hoạt động như thế nào:

## **Pipeline Training Data - Cách Hoạt Động**

Pipeline này được xây dựng bằng **Snakemake** để tạo ra training data cho việc dự đoán độ khó của phylogenetic tree inference. Dưới đây là các bước cụ thể và thứ tự thực hiện:

### **1. Khởi tạo và Cấu hình (Snakefile)**

- Đọc file `config.yaml` để lấy các tham số
- Xác định loại dữ liệu (DNA/AA/MORPH) từ MSA files
- Thiết lập các model phù hợp cho RAxML-NG và IQ-Tree
- Tạo các đường dẫn output và seed ranges

### **2. Tree Inference (raxmlng_tree_inference.smk)**

**Song song thực hiện:**

- **Parsimony trees**: Tạo `num_pars_trees` (mặc định 50) cây bắt đầu từ parsimony
- **Random trees**: Tạo `num_rand_trees` (mặc định 50) cây bắt đầu ngẫu nhiên
- Mỗi tree được tạo với seed khác nhau để đảm bảo tính đa dạng

### **3. Tree Evaluation (raxmlng_tree_evaluation.smk)**

**Song song thực hiện:**

- Đánh giá lại tất cả trees đã tạo ở bước 2
- Tính toán log-likelihood scores chính xác
- Tạo ra các file evaluation logs

### **4. Parsimony Trees (parsimony.smk)**

- Tạo `num_parsimony_trees` (mặc định 100) cây parsimony thuần túy
- Sử dụng RAxML-NG với `--start` flag

### **5. MSA Features (msa_features.smk)**

- Tính toán các đặc trưng của Multiple Sequence Alignment
- Lưu vào file JSON

### **6. RF Distance Calculations (raxmlng_rfdistance.smk)**

**Song song thực hiện:**

- Tính RF distance giữa các search trees
- Tính RF distance giữa các eval trees  
- Tính RF distance giữa các parsimony trees
- Tính RF distance giữa các plausible trees (sau khi filter)

### **7. Data Collection (collect_data.smk)**

**Thu thập và tổ chức dữ liệu:**

- Gộp tất cả search trees và logs
- Gộp tất cả eval trees và logs
- Gộp tất cả parsimony trees và logs
- Lưu tree tốt nhất (highest log-likelihood)
- Thu thập plausible trees

### **8. IQ-Tree Significance Tests (iqtree_significance_tests.smk)**

- Filter duplicate tree topologies
- Thực hiện các test thống kê (AU test, SH test, etc.)
- Tạo clusters để mapping kết quả

### **9. Data Saving (save_data.smk)**

- Lưu tất cả dữ liệu vào SQLite database
- Chuyển database đến thư mục output
- Chuyển đổi database thành training dataframe (Parquet format)

### **Thứ Tự Thực Hiện Cụ Thể:**

```
1. Tree Inference (pars + rand) → 2. Tree Evaluation → 3. Parsimony Trees
                                    ↓
4. MSA Features → 5. RF Distances → 6. Data Collection → 7. IQ-Tree Tests → 8. Save Data
```

### **Output Cuối Cùng:**

- **Training data**: File `.parquet` chứa tất cả features và metrics
- **Database**: File `.sqlite3` với schema chi tiết
- **Log files**: Tất cả output từ RAxML-NG và IQ-Tree
- **Trees**: Các cây phylogenetic đã được tạo và đánh giá

Pipeline này tạo ra một dataset phong phú với nhiều loại trees khác nhau, các metrics đánh giá, và features của MSA để training model dự đoán độ khó của phylogenetic inference.
