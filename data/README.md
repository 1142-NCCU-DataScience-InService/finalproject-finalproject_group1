# Data

- `raw/`：未經修改的原始資料、解壓縮內容與精選 JSON。
- `processed/`：由 `code/` 腳本產生的中繼或清洗後資料集。
- 需要重建資料時，先執行 `code/01_extract_rar.py` 與 `code/02_build_dataset.py`。
