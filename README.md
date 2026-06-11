[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/4D-K6TBY)
# [Group 1] 車禍案件：精神慰撫金 AI 預測系統 (Predicting Mental Damages in Traffic Accidents)

本專案為國立政治大學資料科學課程期末專題，運用機器學習技術分析司法院裁判書開放資料，建立「車禍案件精神慰撫金」的預測模型，協助實務工作者與一般民眾預估合理的賠償金額，減少訴訟資源浪費。

目前 README 內容以 repo 可驗證的程式碼與資料 artifacts 為準。主要腳本位於 `code/`，路徑由 `code/config.py` 統一管理；`data/processed/dataset_cleaned.csv` 與 `models/rf_model.pkl` 已隨 repo 提供，可直接重跑建模與啟動展示。原始 RAR 與完整解壓資料未隨 repo 提供，需自行準備後才能重跑前段資料工程。

## Contributors
| 組員  |系級| 學號        |工作分配|
|-----|-|-----------|-|
| 莊一桂 |資科碩專一| 114971021 |協助獲取訓練資料及前處理基礎工作、README 與專案重現流程整理|
| 侯佳宏 |資科碩專一| 114971019 |打雜、工作架構設計|
| 熊恩 |資科碩專一| 114971007 |end to end testing、UI optimization|
| 王思承 |資科碩專一| 114971026 |協助改版優化程式、整理專案流程、簡報製作、報告、Debug|


## Quick start

安裝套件：

```bash
pip install -r requirements.txt
```

目前 checked-in 狀態已提供 `data/processed/dataset_cleaned.csv` 與 `models/rf_model.pkl`，因此可以直接重跑建模與啟動展示：

```bash
python3 code/04_model_training.py
streamlit run code/05_demo_app.py
```

若不想重新訓練，也可以在 `models/rf_model.pkl` 已存在時直接啟動 Streamlit App：

```bash
streamlit run code/05_demo_app.py
```

完整重現含資料工程的流程如下，但需先自行下載司法院裁判書 RAR、安裝 7-Zip，並確認 `code/config.py` 或環境變數中的資料路徑正確：

```bash
python3 code/01_extract_rar.py --years 2023-2025
python3 code/02_build_dataset.py
python3 code/03_exploratory_analysis.py
python3 code/04_model_training.py
streamlit run code/05_demo_app.py
```

## Folder organization and its related description
idea by Noble WS (2009) [A Quick Guide to Organizing Computational Biology Projects.](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1000424) PLoS Comput Biol 5(7): e1000424.

以下為目前 repo 與 `code/config.py` 對應的結構；實際路徑預設請以 `code/config.py` 為準。

```text
final-project/
├── code/
│   ├── config.py                    # 路徑統一管理，可用環境變數覆寫
│   ├── 01_extract_rar.py            # 解壓縮司法院 RAR 檔
│   ├── 02_build_dataset.py          # 篩選車禍損賠案件、正則擷取特徵
│   ├── 03_exploratory_analysis.py   # 清洗、EDA、特徵工程
│   ├── 04_model_training.py         # Random Forest 訓練與評估
│   └── 05_demo_app.py               # Streamlit 互動展示
├── data/
│   ├── raw/
│   │   ├── OPENDATA-原稿/              # 預設 SOURCE_DIR；原始 RAR 放置處
│   │   ├── Extracted_OpenData/         # 預設 DEST_DIR；解壓後 JSON 放置處
│   │   └── Selected_JSON(原始訓練資料)/ # 預設 SELECTED_DIR；命中案件 JSON 子集
│   └── processed/
│       ├── car_accident_dataset.csv    # 02 產出；目前未隨 repo 提供
│       └── dataset_cleaned.csv         # 03 產出；目前已隨 repo 提供
├── models/
│   └── rf_model.pkl                 # 04 產出，含模型與特徵欄位名
├── docs/                            # 報告、簡報與專案文件
├── image/                           # 圖片輸出位置
├── results/                         # 表格與預測結果輸出位置
├── tests/                           # 測試 scaffold
├── requirements.txt
└── README.md
```

### docs
* Your presentation, 1142_DS-IS-FP_groupID.ppt/pptx/pdf (i.e.,1142_DS-IS-FP_group1.ppt), by **06.09**
* Any related document for the project, i.e.,
  * discussion log
  * software user guide
* 本專案文件與 artifacts：
  * 書面報告：`docs/report/車禍損害賠償預測_期末專題完整報告_正式版.docx`
  * 簡報：`docs/slides/`
  * 待辦紀錄：`todo-list.md`

### data
* Input
  * Source：司法院裁判書開放資料（JSON 格式），由司法院資料開放平臺下載「裁判書」壓縮檔。
  * Format：原始資料為依月份提供的 `.rar`；解壓後每筆裁判書為一個 `.json`。
  * Size：目前 repo 中 `data/raw/Selected_JSON(原始訓練資料)/` 有 7,531 份命中案件 JSON；`data/processed/dataset_cleaned.csv` 為 5,143 筆、78 欄。
* 目前資料狀態：
  * `data/processed/dataset_cleaned.csv` 已隨 repo 提供，可直接用於建模。
  * `data/processed/car_accident_dataset.csv` 目前未隨 repo 提供，若要重跑清洗步驟，需先執行 `code/02_build_dataset.py`。
  * 原始 RAR 與完整解壓資料未隨 repo 提供，需自行下載並遵守司法院開放資料使用條款。

### code
* Analysis steps
  * `code/01_extract_rar.py`：把 `SOURCE_DIR` 內的 `.rar` 以 7-Zip 解壓到 `DEST_DIR`，可用 `--years 2023-2025` 指定年份。
  * `code/02_build_dataset.py`：掃描解壓後 JSON，篩選交通事故損害賠償案件，擷取金額、傷亡、過失比例等特徵，輸出 `car_accident_dataset.csv`。
  * `code/03_exploratory_analysis.py`：清理缺失值與異常值，產生 `Injury_Level`、法院 one-hot 欄位與金額對數欄位，輸出 `dataset_cleaned.csv`。
  * `code/04_model_training.py`：訓練與評估 Random Forest Regressor，輸出 `models/rf_model.pkl`。
  * `code/05_demo_app.py`：以 Streamlit 建立互動式預測展示。
* Which method or package do you use?
  * 主要套件：`pandas`、`numpy`、`scikit-learn`、`joblib`、`streamlit`、`tqdm`。
  * 主要方法：中文裁判書正則擷取、表格資料清洗、`np.log1p` 金額轉換、Random Forest 迴歸。
* How do you perform training and evaluation?
  * 使用 80% / 20% train/test split。
  * 使用 `GridSearchCV` 做 3-fold cross-validation，評估指標為還原金額後的 MAE。
  * 訓練目標為 `Mental_Damage_log`，預測後以 `np.expm1` 還原金額。
  * 為避免資料洩漏，排除 `JID`、`Year`、`Injury`、原始目標欄、原始金額欄與 `Verdict_Total`。
* What is a null model for comparison?
  * Null Model 為不看任何案件特徵、一律預測訓練集精神慰撫金平均值。

### results
* What is your performance?
  * Null Model MAE：393,888 元。
  * 固定參數 Random Forest MAE：249,295 元；R-squared：0.4468。
  * GridSearchCV 交叉驗證 MAE：260,658 元。
  * 調參後 Random Forest MAE：244,958 元；R-squared：0.4478。
* Is the improvement significant?
  * 調參後模型相較盲猜基準的 MAE 改善約 37.8%。
  * 相較固定參數 Random Forest，調參後 MAE 降低 4,337 元。
* Top 5 feature importances
  1. `Injury_Level`（傷亡嚴重度）：35.15%
  2. `Care_Fee_log`（看護費用對數）：21.39%
  3. `Medical_Fee_log`（醫療費用對數）：21.02%
  4. `Work_Loss_log`（工作損失對數）：13.02%
  5. `Court_CYEV`（法院代碼）：1.72%

## 專案目標與輸入資料

### 研究目標
- 核心問題：精神慰撫金在實務上往往由法官依「自由心證」裁量，缺乏明確公式。
- 解決方案：透過大數據分析過往判決，找出影響判決金額的關鍵特徵，並建立預測模型。

### 資料來源
- 來源：司法院裁判書開放資料（JSON 格式）
- 資料工程預設範圍：`code/01_extract_rar.py` 的互動選單與範例指令以 2023-2025 年 RAR 作為近三年研究範圍。
- 目前可驗證資料量：
  - `data/raw/Selected_JSON(原始訓練資料)/`：7,531 份命中案件 JSON
  - `data/processed/dataset_cleaned.csv`：5,143 筆、78 欄
  - `Year` 欄位來自司法院 `JYEAR`，目前清洗後資料範圍為民國 107-114 年

## 原始資料說明

### 如何取得原始資料
1. 前往司法院資料開放平臺：<https://opendata.judicial.gov.tw/>
2. 下載「裁判書」開放資料的壓縮檔，通常依月份提供，副檔名為 `.rar`。
3. 將下載的 `.rar` 放入來源資料夾，並以 `code/config.py` 或環境變數 `SOURCE_DIR` 指向該資料夾。

原始裁判書屬司法院開放資料，請遵守其開放資料使用條款；資料本身可能含個資，請勿將原始檔或可識別個資的衍生資料公開上傳至 repo。

### 原始 RAR 檔命名規則
- 來源資料夾中的檔案為 `*.rar`，檔名前 6 碼為西元年月 `YYYYMM`，例如 `202401*.rar` 代表 2024 年 1 月。
- `code/01_extract_rar.py` 以檔名前 4 碼做年份過濾、以前 6 碼做月份分組。
- 同一月份若有多個版本，程式只取檔名排序最大的最新版，避免重複解壓。

### 裁判書 JSON 欄位結構
每個 JSON 檔代表一份裁判書。本專案實際依賴下列欄位：

| JSON 欄位 | 用途 | 在程式中的處理 |
| --- | --- | --- |
| `JTITLE` | 案由 | 篩選條件：必須包含「損害賠償」 |
| `JFULL` | 裁判書全文 | 篩選車禍關鍵字，並以正則擷取各項金額與特徵 |
| `JID` | 裁判書識別碼 | 取 `JID.split(",")[0]` 作為法院代碼；另存檔時將逗號換成底線 |
| `JYEAR` | 年度 | 寫入輸出欄位 `Year` |

### 路徑設定
所有主要路徑由 `code/config.py` 統一管理，預設使用專案內相對路徑，並可用環境變數覆寫。

| 環境變數 | 預設值 | 意義 | 對應步驟 |
| --- | --- | --- | --- |
| `SOURCE_DIR` | `data/raw/OPENDATA-原稿` | 原始 `.rar` 來源資料夾 | 01 輸入 |
| `DEST_DIR` | `data/raw/Extracted_OpenData` | 解壓後 JSON 的輸出資料夾 | 01 到 02 |
| `SELECTED_DIR` | `data/raw/Selected_JSON(原始訓練資料)` | 命中案件的 JSON 複製目的地 | 02 |
| `SEVEN_ZIP` | PATH 中的 `7zz` 或 `7z` | 7-Zip 執行檔路徑 | 01 |

```bash
export SEVEN_ZIP="/opt/homebrew/bin/7z"
export SOURCE_DIR="$HOME/judicial_opendata/rar"
export DEST_DIR="$HOME/judicial_opendata/extracted"
export SELECTED_DIR="./data/raw/Selected_JSON(原始訓練資料)"
```

## 資料前處理管線

完整重現順序為 ①→②→③，最終產出模型輸入檔 `data/processed/dataset_cleaned.csv`。

### Step 01：解壓縮
`code/01_extract_rar.py` 將 `SOURCE_DIR` 內的 `.rar` 解壓到 `DEST_DIR`。

```bash
python3 code/01_extract_rar.py
python3 code/01_extract_rar.py --years 2023-2025
python3 code/01_extract_rar.py --all
```

特點：
- 斷點續傳：若某月份資料夾解壓後的 JSON 數量已大於 1,000，視為已完成並自動跳過。
- 只取最新版：同月份多個壓縮檔只解壓檔名最大者。
- 解壓指令採 `7z x <rar> -o<dest> -y -aoa`。

### Step 02：建立資料集
`code/02_build_dataset.py` 遞迴掃描 `DEST_DIR` 下各月份資料夾中的 JSON，篩選車禍損賠案件並以正則擷取特徵，輸出 `data/processed/car_accident_dataset.csv`，同時把命中 JSON 複製到 `SELECTED_DIR`。

篩選條件需同時成立：
1. `JTITLE` 含「損害賠償」
2. `JFULL` 含「車禍／交通事故／道路交通／汽車／機車／行車事故」任一關鍵字
3. 能從判決書擷取到法院認定的精神慰撫金金額

**擷取邏輯（皆以正則自 `JFULL` 取得）：**

| 輸出欄位 | 擷取目標 | 規則摘要 |
| --- | --- | --- |
| `Claimed_Mental_Damage` / `Mental_Damage` | 原告請求精神慰撫金／法院認定精神慰撫金（目標 y） | 優先從「本院得心證之理由」後與賠償項目段落擷取；比對「精神慰撫金／非財產上損害／慰撫金」等語句，法院認定額優先抓「准許／為當／不爭執／核屬有據」等句型。 |
| `Verdict_Total` | 判決給付總額 | 比對「被告應/須給付原告 … 元」「給付原告 … 元」等主文或結論句型。 |
| `Claimed_Medical_Fee` / `Medical_Fee` | 原告請求醫療費／法院認定醫療費 | 以賠償項目切割後比對「醫療費(用)」相關段落；明確駁回且無准許金額時記為 0。 |
| `Claimed_Care_Fee` / `Care_Fee` | 原告請求看護費／法院認定看護費 | 以賠償項目切割後比對「看護費(用)」相關段落；同時支援請求額與法院認定額。 |
| `Claimed_Work_Loss` / `Work_Loss` | 原告請求停工損失／法院認定停工損失或勞動能力喪失 | 比對「停工損失／工作損失／勞動能力損失」等語句，擷取請求額與認定額。 |
| `Claimed_Transportation_Fee` / `Transportation_Fee` | 原告請求交通費／法院認定交通費 | 比對「交通費」相關賠償項目，擷取請求額與認定額。 |
| `Claimed_Funeral_Or_Support_Fee` / `Funeral_Or_Support_Fee` | 原告請求喪葬費或扶養費／法院認定喪葬費或扶養費 | 比對「喪葬費／扶養費」相關賠償項目，擷取請求額與認定額。 |
| `Fault_Ratio` | 與有過失比例 | 比對「與有過失 … N%（或百分之 N）」等句型；未命中時預設 0。 |
| `Compulsory_Insurance_Deducted` | 強制險扣除金額 | 比對強制險、保險給付、扣除等相關句型並擷取金額。 |
| `Injury` | 傷亡類型 | 死亡/往生/殞命/不治→「死亡」；重傷/截肢/植物人→「重傷」；其餘→「傷害」。 |
| `Labor_Capacity_Loss_Rate` | 勞動能力喪失率 | 比對「勞動能力喪失 … %／百分之 …」等比例句型。 |
| `Hospital_Days` / `Surgery_Count` | 住院天數／手術次數 | 比對住院日數與手術次數描述，轉為數值欄位。 |
| `Plaintiff_Age` / `Defendant_Age` | 原告／被告年齡 | 從當事人背景、學經歷或審酌情節段落擷取年齡描述。 |
| `Plaintiff_Education` / `Defendant_Education` | 原告／被告教育程度 | 比對高中、大學、碩士等教育程度關鍵詞。 |
| `Plaintiff_Income` / `Defendant_Income` | 原告／被告收入 | 比對薪資、所得、收入等金額描述。 |
| `Plaintiff_Gender` / `Defendant_Gender` | 原告／被告性別 | 依當事人稱謂與語句線索推定性別。 |
| `Plaintiff_Occupation` / `Defendant_Occupation` | 原告／被告職業 | 比對職業、工作、任職等背景描述。 |
| `Drunk` | 酒駕 | 全文含酒駕、酒後駕車、飲酒後駕車等語句時為 1，否則 0。 |
| `Vehicle_Type` | 事故車種 | 比對汽車、機車等事故車種描述。 |
| `Plaintiff_Has_Lawyer` / `Defendant_Has_Lawyer` | 原告／被告是否有律師代理 | 比對訴訟代理人、律師等相關資訊。 |
| `Court` / `Year` / `Instance` / `JID` / `PDF_Path` | 法院、年度、審級、裁判識別碼、來源路徑 | `Court` 取 `JID.split(",")[0]`；`Year` 取 `JYEAR`；審級與來源資訊依裁判內容或來源檔資訊寫入。 |
| 金額與項目共通規則 | 金額格式、項目切割與擷取範圍 | 金額支援阿拉伯數字、逗號、`萬` 單位與常見中文大寫金額；項目切割支援 `㈠`、`一`、`1.`、`(1)`、`⑴`、`⒈` 等格式，降低把傷勢或過失認定段落誤判為金額項目的風險。 |

```bash
python3 code/02_build_dataset.py
# → data/processed/car_accident_dataset.csv
# → data/raw/Selected_JSON(原始訓練資料)/
```

> 目前隨 repo 提供的 `data/processed/dataset_cleaned.csv` 與 `models/rf_model.pkl` 未因這次資料擷取欄位擴充而重新產生；若重跑 ②〜④，請同步更新樣本數、欄位數、模型指標與特徵重要性。

### Step 03：清洗與特徵工程
`code/03_exploratory_analysis.py` 讀入 `data/processed/car_accident_dataset.csv`，輸出 `data/processed/dataset_cleaned.csv`。

1. 缺失值：`Medical_Fee`、`Care_Fee`、`Work_Loss` 缺值補 0；`Mental_Damage` 缺值則刪除。
2. 異常值：保留 `Mental_Damage` 介於 10,000 到 10,000,000 元；各費用欄上限 50,000,000 元；`Fault_Ratio` 夾限於 0 到 100。
3. 特徵編碼：`Injury` 順序編碼為 `Injury_Level`；`Court` 做 one-hot。
4. 特徵縮放：對 `Medical_Fee`、`Care_Fee`、`Work_Loss`、`Mental_Damage` 做 `log1p`，新增 `*_log` 欄位。

## 中繼資料字典

### `car_accident_dataset.csv` 原始欄位
`code/02_build_dataset.py` 預設輸出 11 欄以維持與清洗、建模流程相容；其餘 parser 可擷取欄位可透過 `config.py` 設定 `OUTPUT_COLUMNS = "ALL"` 或自訂欄位清單後另行驗證。

| 欄位 | 輸出狀態 | 型別 | 說明 |
| --- | --- | --- | --- |
| `JID` | 預設輸出 | 字串 | 裁判書識別碼 |
| `Court` | 預設輸出 | 類別 | 法院代碼 |
| `Year` | 預設輸出 | 整數 | 年度 |
| `Injury` | 預設輸出 | 類別 | 傷亡類型：死亡／重傷／傷害 |
| `Drunk` | 預設輸出 | 0/1 | 是否酒駕 |
| `Medical_Fee` | 預設輸出 | 數值（元） | 法院認定醫療費用 |
| `Care_Fee` | 預設輸出 | 數值（元） | 法院認定看護費 |
| `Work_Loss` | 預設輸出 | 數值（元） | 法院認定停工損失／勞動能力喪失 |
| `Fault_Ratio` | 預設輸出 | 數值（%） | 與有過失比例 |
| `Verdict_Total` | 預設輸出 | 數值（元） | 判決給付總額，建模時排除以防資料洩漏 |
| `Mental_Damage` | 預設輸出 | 數值（元） | 精神慰撫金，預測目標 |
| `Claimed_*` 與當事人背景欄位 | 擴充欄位 | 數值／文字／類別 | 原告請求額、當事人背景、訴訟代理、車種、住院與手術資訊等 |

### `dataset_cleaned.csv` 新增欄位
| 欄位 | 說明 |
| --- | --- |
| `Injury_Level` | `Injury` 的順序編碼，死亡=3、重傷=2、傷害=1、未知=0 |
| `Court_*` | `Court` 的 one-hot 欄位 |
| `Medical_Fee_log` / `Care_Fee_log` / `Work_Loss_log` / `Mental_Damage_log` | 對數轉換後特徵 |

## 模型建構

### 演算法選擇
針對具高度非線性關係的表格型特徵，選用樹狀模型 Random Forest Regressor。

### 訓練策略
- Train/Test Split：80%（4,114 筆）/ 20%（1,029 筆）隨機切割。
- 超參數調整：使用 `GridSearchCV` 做 3-fold 交叉驗證，評分指標為還原真實金額後的 MAE。
- 最佳超參數：`n_estimators=200`、`max_depth=8`、`min_samples_leaf=2`、`min_samples_split=5`、`max_features=0.7`、`random_state=42`、`n_jobs=-1`。
- 模型 artifact：`models/rf_model.pkl` 是 `joblib` 檔，內容為 `{"model": rf, "features": X.columns.tolist()}`；目前保存 69 個模型輸入特徵。

### 4.3 基準模型 (Null Model)
- **策略**：無論案件特徵為何，一律「盲猜」訓練集的精神慰撫金平均值。
- **基準誤差**：MAE 為 **393,888 元**。

```bash
python3 code/04_model_training.py
# → models/rf_model.pkl（含模型與特徵欄位名）
```

---

##  成效評估 (Results)

### 評估指標
選用 **MAE（平均絕對誤差）**：相較 RMSE，更能直觀反映「預測金額與法官真實判決金額平均差了幾元」，在法律實務上最具解釋力。

### 顯著進步
- **Null Model MAE**：393,888 元
- **固定參數 Random Forest MAE**：249,295 元；R-squared：0.4468
- **GridSearchCV 交叉驗證 MAE**：260,658 元
- **調參後 Random Forest MAE**：244,958 元
- **進步幅度**：較盲猜基準提升 **37.8%**；相較固定參數 RF 的 MAE 降低 **4,337 元**
- **R-squared**：**0.4478**（以 log 目標計算）

### 特徵重要性（Top 5）
1. `Injury_Level`（傷亡嚴重度）— 35.15%
2. `Care_Fee_log`（看護費用對數）— 21.39%
3. `Medical_Fee_log`（醫療費用對數）— 21.02%
4. `Work_Loss_log`（工作損失對數）— 13.02%
5. `Court_CYEV`（法院代碼）— 1.72%

> **洞察**：傷亡嚴重程度、醫療支出、看護需求與工作損失越高，模型越傾向預測較高的精神慰撫金；與有過失比例也提供部分責任分配資訊。

## 系統展示與重現

使用 Streamlit 開發互動式 Web App，可輸入案件條件（傷亡程度、醫療費、是否酒駕等），即時呼叫模型試算賠償金額。

### 快速啟動（使用目前 checked-in artifacts）

```bash
pip install -r requirements.txt
python3 code/04_model_training.py
streamlit run code/05_demo_app.py
```

若不想重新訓練，也可在 `models/rf_model.pkl` 已存在時直接啟動 App：

```bash
streamlit run code/05_demo_app.py
```

### 完整重現（含前處理，需自備原始資料）

```bash
# 0) 先依 §2 取得原始 RAR、設定 code/config.py / 環境變數
python3 code/01_extract_rar.py --years 2023-2025
python3 code/02_build_dataset.py
python3 code/03_exploratory_analysis.py
python3 code/04_model_training.py
streamlit run code/05_demo_app.py
```

## 專案挑戰：
- 非結構化資料擷取：司法文書格式極不統一，最大挑戰在於以正則表達式從中文裁判書中擷取各項賠償金額與案件特徵。
- 資料洩漏風險：`Verdict_Total` 可能包含精神慰撫金本身，因此模型訓練時必須排除。
- 重現成本：完整原始裁判書資料體積大，前段資料工程需要額外下載、解壓與磁碟空間。

## 生成式 AI 協作歷程

本專案保留的可驗證協作成果主要體現在目前 repo 的工作流腳本、報告與展示 artifacts。README 僅列出 repo 內可直接檢查的文件位置，不重複未由檔案佐證的 prompt 時間線。

| 類型 | 目前檔案 | 說明 |
| --- | --- | --- |
| 程式工作流 | `code/01_extract_rar.py` 到 `code/05_demo_app.py` | 從解壓、資料集建立、清洗、建模到 Streamlit 展示 |
| 路徑設定 | `code/config.py` | 集中管理 raw / processed / model 路徑與環境變數覆寫 |
| 書面報告 | `docs/report/車禍損害賠償預測_期末專題完整報告_正式版.docx` | 期末專題報告 artifact |
| 簡報 | `docs/slides/` | 期末報告與展示簡報 |
| 待辦紀錄 | `todo-list.md` | 專案後續事項紀錄 |

## 目前可重現狀態

經目前 repo 檔案檢查，**後段（建模與展示）可直接重現**，**前段（解壓與資料擷取）需自行準備司法院原始資料或解壓後 JSON 後才能重跑**。

| 步驟 | 腳本 | 輸入 | 產出 | 狀態 |
| --- | --- | --- | --- | --- |
| ① 解壓縮 | `code/01_extract_rar.py` | 原始 `.rar`（`SOURCE_DIR`） | 解壓後 JSON（`DEST_DIR`） | ⚠️ 需自備原始資料與 7-Zip |
| ② 建立資料集 | `code/02_build_dataset.py` | 解壓後 JSON（`DEST_DIR`） | `data/processed/car_accident_dataset.csv` + `SELECTED_DIR/` | ⚠️ 需先完成 ①；中繼 CSV 目前未隨 repo 提供 |
| ③ 清洗 / 特徵工程 | `code/03_exploratory_analysis.py` | `data/processed/car_accident_dataset.csv` | `data/processed/dataset_cleaned.csv` | ⚠️ 需先完成 ②；清洗後 CSV 目前已提供 |
| ④ 模型訓練 | `code/04_model_training.py` | `data/processed/dataset_cleaned.csv` | `models/rf_model.pkl` | ✅ 可直接執行 |
| ⑤ 互動展示 | `code/05_demo_app.py` | `models/rf_model.pkl` | Streamlit Web App | ✅ 可直接執行 |

> **為什麼 ①〜③ 不能從乾淨 clone 完整重現？**
> 司法院裁判書原始開放資料（RAR / JSON）體積龐大，且應依司法院開放資料條款自行下載，因此完整原始資料與解壓資料未隨 repo 發佈。只要依 [§2 原始資料說明](#-2-原始資料說明--data-source-documentation) 取得來源檔並設定路徑，即可由 ① 重跑到 ③。
>
> 由於 ③ 的產物 `data/processed/dataset_cleaned.csv` 已隨 repo 提供，**想直接驗證模型者可略過 ①〜③，直接執行 ④、⑤。**

## 已知問題與待辦

- [ ] `data/processed/car_accident_dataset.csv` 目前未隨 repo 提供；若要重跑 03，需先由 02 重新產生。
- [ ] 原始 RAR 與完整解壓資料未隨 repo 提供；01 到 02 需自行下載司法院資料並準備足夠磁碟空間。
- [ ] 目前沒有正式自動化測試；`tests/` 僅保留 scaffold。
- [ ] `requirements.txt` 尚未鎖定版本；跨機器重現時可能需要補上 pinned versions。
- [x] 正則擷取仍可能受裁判書格式差異影響；未來可加入抽樣人工驗證或更完整的 parser 測試。
- [ ] 未來可導入 LLM 輔助理解判決情節與抗辯內容，突破純正則表達式的限制。

## 貢獻紀錄

- 目前 README 已對齊 `code/` 編號工作流、`code/config.py` 路徑設定、checked-in artifacts 與目前可重算的模型指標。
- 目前 repo 可直接使用的核心 artifacts 為 `data/processed/dataset_cleaned.csv` 與 `models/rf_model.pkl`。
- 若未來重新產生 `data/processed/car_accident_dataset.csv`、`data/processed/dataset_cleaned.csv` 或 `models/rf_model.pkl`，請同步更新本 README 的樣本數、評估指標與特徵重要性。

## References
* Packages you use
  * `pandas`
  * `numpy`
  * `scikit-learn`
  * `joblib`
  * `streamlit`
  * `tqdm`
* Related publications
  * Noble WS (2009). [A Quick Guide to Organizing Computational Biology Projects.](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1000424) PLoS Comput Biol 5(7): e1000424.
  * 司法院資料開放平臺：<https://opendata.judicial.gov.tw/>

---

本專題為國立政治大學資料科學課程期末專案（第一組）。
