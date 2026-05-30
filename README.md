# ⚖️ 車禍案件：精神慰撫金 AI 預測系統 (Predicting Mental Damages in Traffic Accidents)

本專案為國立政治大學資料科學課程期末專題，運用機器學習技術分析司法院裁判書開放資料，建立「車禍案件精神慰撫金」的預測模型，協助實務工作者與一般民眾預估合理的賠償金額，減少訴訟資源浪費。

> **本次更新重點**：補齊「原始資料說明」與完整的資料前處理管線文件，並同步說明以 `config.py` 統一管理的相對路徑與 macOS 相容性重構。目標是讓任何組員（或助教）拿到專案後，都能清楚知道「資料從哪來、如何一步步變成模型輸入、目前哪些步驟可直接重現」。

---

## 🧭 0. 重現狀態與專案結構 (Repro Status & Project Structure)

### 0.1 目前可重現狀態

經實測，**後段（建模與展示）可直接重現**，**前段（解壓與資料擷取）因原始資料未隨 repo 發佈，需自行準備來源資料後才能重跑**。

| 步驟 | 腳本 | 輸入 | 產出 | 狀態 |
| --- | --- | --- | --- | --- |
| ① 解壓縮 | `01_extract_rar.py` | 原始 `.rar`（`SOURCE_DIR`） | 解壓後 JSON（`DEST_DIR`） | ⚠️ 需自備原始資料 |
| ② 建立資料集 | `02_build_dataset.py` | 解壓後 JSON（`DEST_DIR`） | `car_accident_dataset.csv` + `Selected_JSON/` | ⚠️ 需先完成 ① |
| ③ 清洗 / 特徵工程 | `03_exploratory_analysis.py` | `car_accident_dataset.csv` | `dataset_cleaned.csv` | ⚠️ 需先完成 ② |
| ④ 模型訓練 | `04_model_training.py` | `dataset_cleaned.csv` | `rf_model.pkl` | ✅ **已實測可運作** |
| ⑤ 互動展示 | `05_demo_app.py` | `rf_model.pkl` | Streamlit Web App | ✅ **已實測可運作** |

> **為什麼 ①〜③ 目前還無法重現？**
> 司法院裁判書原始開放資料（數十 GB 的 `.rar` / JSON）**體積龐大、且應依司法院開放資料條款自行下載**，因此未隨本 repo 一併發佈。只要依 [§2 原始資料說明](#-2-原始資料說明--data-source-documentation) 取得來源檔並設定路徑，即可由 ① 重跑到 ③。
>
> 由於 ③ 的產物 `dataset_cleaned.csv` 已隨 repo 提供，**想直接驗證模型者可略過 ①〜③，直接執行 ④、⑤。**

### 0.2 建議專案結構

> 以下為依目前腳本與 `config.py` 重構後的「建議」結構；實際資料夾命名與預設路徑請以 repo 內的 **`config.py` 為準**，不一致處以 `config.py` 為主。

```text
finalproject_group1/
├── config.py                    # 路徑統一管理（相對路徑預設、可用環境變數覆寫）
├── requirements.txt             # 套件相依
├── README.md
├── 01_extract_rar.py            # ① 解壓縮（需 7-Zip）
├── 02_build_dataset.py          # ② 篩選車禍損賠案件、正則擷取特徵
├── 03_exploratory_analysis.py   # ③ 清洗、異常值處理、特徵工程
├── 04_model_training.py         # ④ Random Forest 訓練與評估
├── 05_demo_app.py               # ⑤ Streamlit 互動展示
├── data/
│   ├── car_accident_dataset.csv # ② 產出（中繼資料）
│   ├── dataset_cleaned.csv      # ③ 產出（模型輸入）
│   └── Selected_JSON/           # ② 另存的「精選裁判書」JSON 子集
├── models/
│   └── rf_model.pkl             # ④ 產出（含模型與特徵欄位名）
└── （原始 RAR / 解壓後 JSON：不在 repo 內，需自行下載並以 config.py 指定位置）
```

### 0.3 環境需求

- **Python**：3.12（其餘版本未測）
- **作業系統**：Windows 11 / macOS 皆可（本次已做 macOS 路徑相容性重構）
- **7-Zip**：僅 ①（解壓縮）需要
  - Windows：安裝官方 7-Zip，預設 `C:\Program Files\7-Zip\7z.exe`
  - macOS：`brew install p7zip`，並將 `SEVEN_ZIP` 環境變數指向 `7z`（或 `7zz`）的實際路徑
- **磁碟空間**：原始 `.rar` 解壓後約為壓縮檔的 5〜10 倍，請預留足夠空間
- **套件**：`pip install -r requirements.txt`（主要為 `pandas`、`numpy`、`scikit-learn`、`streamlit`、`joblib`、`tqdm`）

---

## 🎯 1. 專案目標與輸入資料 (Input)

### 1.1 研究目標 (Goal)
- **核心問題**：精神慰撫金在實務上往往由法官依「自由心證」裁量，缺乏明確公式。
- **解決方案**：透過大數據分析過往判決，找出影響判決金額的關鍵特徵，並建立預測模型。

### 1.2 資料來源 (Data Source)
- **來源**：司法院裁判書開放資料（JSON 格式）
- **範圍**：2023 年 01 月至 2025 年 04 月（民國 112–114 年）
- **樣本數**：擷取「損害賠償」且包含「車禍／交通事故」之有效案件共 **7,536 筆**（清洗後保留 **7,050 筆**，詳見 §3）。

---

## 🗂️ 2. 原始資料說明 (Data Source Documentation)

> 本節為本次更新的補充重點，說明「原始資料長什麼樣、如何取得、如何被程式讀取」，讓 ①〜③ 的步驟可被完整重現。

### 2.1 如何取得原始資料

1. 前往 **司法院資料開放平臺**：<https://opendata.judicial.gov.tw/>
2. 下載「裁判書」開放資料的壓縮檔（依月份提供，副檔名為 `.rar`）。
3. 將下載的 `.rar` 全部放入同一個來源資料夾，並把 `config.py` 的 `SOURCE_DIR` 指向該資料夾。

> ⚠️ **授權與隱私**：原始裁判書屬司法院開放資料，請遵守其開放資料使用條款；資料本身可能含個資，請勿將原始檔或可識別個資的衍生資料公開上傳至 repo。本 repo 僅保留去識別化、彙整後的特徵資料表（CSV）。

### 2.2 原始 RAR 檔命名規則

- 來源資料夾中的檔案為 `*.rar`，**檔名前 6 碼為西元年月 `YYYYMM`**（例如 `202401*.rar` 代表 2024 年 1 月）。
- `01_extract_rar.py` 即以「檔名前 4 碼（西元年）」做年份過濾、以「前 6 碼（年月）」做月份分組。
- **同一月份若有多個版本（如含更新版）**，程式只取檔名排序最大的最新版（`sorted(month_rars)[-1]`），避免重複解壓。

### 2.3 解壓後的目錄與檔案

- 每個月份解壓到 `DEST_DIR/YYYYMM/` 之下（保留原壓縮檔內的子目錄結構）。
- 解壓後每筆裁判書為一個 `.json` 檔；②（建立資料集）會以 `rglob("*.json")` 遞迴掃描每個月份資料夾。

### 2.4 裁判書 JSON 欄位結構

每個 JSON 檔代表一份裁判書。本專案實際讀取並依賴下列欄位（其餘欄位未使用）：

| JSON 欄位 | 用途 | 在程式中的處理 |
| --- | --- | --- |
| `JTITLE` | 案由 | 篩選條件：必須包含「損害賠償」 |
| `JFULL` | 裁判書全文 | 篩選車禍關鍵字、並以正則擷取各項金額／特徵 |
| `JID` | 裁判書識別碼 | **以逗號分隔**，取第一段作為法院代碼（`JID.split(",")[0]`）；另存檔時將逗號換成底線 |
| `JYEAR` | 年度 | 寫入輸出欄位 `Year` |

> 註：`JID` 在本資料集為逗號分隔字串（約略對應「法院,年度,字別,案號,…」），程式僅取第一段為 `Court`。若日後司法院調整欄位格式，需同步檢查 `02_build_dataset.py` 的 `JID.split(",")` 邏輯。

### 2.5 「精選裁判書」子集（Selected_JSON）

- ② 在篩選出有效案件的同時，會把命中的原始 JSON **複製一份**到 `SELECTED_DIR/`（`COPY_MATCHED_FILES = True`），檔名為 `JID` 將逗號換成底線後的 `{...}.json`。
- 這個子集（約 7,536 筆）即為本研究真正使用到的裁判書。**若已保留此子集，未來想重建 CSV，可把 `SOURCE_DIR`/掃描目錄指向它，省去重新解壓全部原始 RAR 的時間。**

### 2.6 路徑設定（`config.py` 與環境變數）

所有主要路徑現由專案根目錄的 **`config.py` 統一管理，預設使用專案內相對路徑**（取代舊版散落於各腳本的 `F:\`、`H:\`、`e:\...` 絕對路徑），以支援 macOS 與跨機器協作。

若你的原始 RAR 檔、解壓輸出位置或 7-Zip 不在預設位置，可用環境變數覆寫：

| 環境變數 | 意義 | 對應步驟 |
| --- | --- | --- |
| `SOURCE_DIR` | 原始 `.rar` 來源資料夾 | ① 輸入 |
| `DEST_DIR` | 解壓後 JSON 的輸出資料夾 | ①→② |
| `SELECTED_DIR` | 命中案件的 JSON 複製目的地 | ② |
| `SEVEN_ZIP` | 7-Zip 執行檔路徑 | ① |

**設定範例：**

```bash
# macOS / Linux
export SEVEN_ZIP="/opt/homebrew/bin/7z"
export SOURCE_DIR="$HOME/judicial_opendata/rar"
export DEST_DIR="$HOME/judicial_opendata/extracted"
export SELECTED_DIR="./data/Selected_JSON"
```

```powershell
# Windows PowerShell
$env:SEVEN_ZIP   = "C:\Program Files\7-Zip\7z.exe"
$env:SOURCE_DIR  = "D:\judicial_opendata\rar"
$env:DEST_DIR    = "D:\judicial_opendata\extracted"
$env:SELECTED_DIR= ".\data\Selected_JSON"
```

> 各變數的**實際預設值以 `config.py` 為準**；未設定環境變數時，會使用 `config.py` 內的相對路徑預設。

---

## ⚙️ 3. 資料前處理管線 (Preprocessing Pipeline)

完整重現順序為 ①→②→③，最終產出模型輸入檔 `dataset_cleaned.csv`。

### Step ① 解壓縮 — `01_extract_rar.py`

把 `SOURCE_DIR` 內的 `.rar` 以 7-Zip 解壓到 `DEST_DIR`。

```bash
python 01_extract_rar.py                  # 互動選單
python 01_extract_rar.py --years 2023-2025 # 只解壓特定西元年份
python 01_extract_rar.py --all             # 全部解壓
```

特點：
- **斷點續傳**：若某月份資料夾解壓後的 JSON 數量已 > 1,000，視為已完成而自動跳過，可安全分多次執行。
- **只取最新版**：同月份多個壓縮檔只解壓檔名最大者。
- 解壓指令採 `7z x <rar> -o<dest> -y -aoa`（自動覆寫、不互動）。

### Step ② 建立資料集 — `02_build_dataset.py`

遞迴掃描 `DEST_DIR` 下所有 JSON，篩選車禍損賠案件並以正則擷取特徵，輸出 `car_accident_dataset.csv`，同時把命中 JSON 複製到 `SELECTED_DIR`。

**篩選條件（需同時成立）：**
1. `JTITLE` 含「損害賠償」
2. `JFULL` 含「車禍／交通事故／道路交通」任一關鍵字
3. 能從全文擷取到「精神慰撫金」金額（抓不到者視為非主體判決而跳過）

**擷取邏輯（皆以正則自 `JFULL` 取得）：**

| 輸出欄位 | 擷取目標 | 規則摘要 |
| --- | --- | --- |
| `Mental_Damage` | 精神慰撫金（目標 y） | 比對「精神慰撫金／非財產上損害／慰撫金 … 元」 |
| `Verdict_Total` | 判決給付總額 | 比對「被告應/須給付原告 … 元」「給付原告 … 元」 |
| `Medical_Fee` | 醫療費 | 比對「醫療費(用) … 元」 |
| `Care_Fee` | 看護費 | 比對「看護費(用) … 元」 |
| `Work_Loss` | 工作／勞動能力損失 | 比對「(勞動能力\|工作)損失 … 元」 |
| `Fault_Ratio` | 與有過失比例 | 比對「與有過失 … N%（或百分之 N）」，預設 0 |
| `Injury` | 傷亡類型 | 死亡/往生/殞命/不治→「死亡」；重傷/截肢/植物人→「重傷」；其餘→「傷害」 |
| `Drunk` | 酒駕 | 全文含 酒駕/酒後駕車/飲酒…駕 → 1，否則 0 |
| `Court` | 法院 | `JID.split(",")[0]` |
| `Year` | 年度 | `JYEAR` |

```bash
python 02_build_dataset.py
# → data/car_accident_dataset.csv（中繼資料）
# → data/Selected_JSON/（精選裁判書）
```

### Step ③ 清洗與特徵工程 — `03_exploratory_analysis.py`

讀入 `car_accident_dataset.csv`，輸出 `dataset_cleaned.csv`。

1. **缺失值**：`Medical_Fee`、`Care_Fee`、`Work_Loss` 缺值補 0（視為未請求）；`Mental_Damage` 缺值則整筆刪除。
2. **異常值**：保留 `Mental_Damage` 介於 **10,000〜10,000,000** 元；各費用欄上限 **50,000,000** 元；`Fault_Ratio` 夾限於 0〜100。
3. **特徵編碼**：`Injury` 順序編碼為 `Injury_Level`（死亡=3、重傷=2、傷害=1、未知=0）；`Court` 做 One-Hot（`drop_first=True`）。
4. **特徵縮放**：對 `Medical_Fee`、`Care_Fee`、`Work_Loss`、`Mental_Damage` 做 `log1p`，新增 `*_log` 欄位以穩定訓練。

```bash
python 03_exploratory_analysis.py
# → data/dataset_cleaned.csv（最終模型輸入，7,050 筆）
```

### 中繼資料字典 (Data Dictionary)

**`car_accident_dataset.csv`（② 產出）原始欄位：**

| 欄位 | 型別 | 說明 |
| --- | --- | --- |
| `JID` | 字串 | 裁判書識別碼（逗號分隔） |
| `Court` | 類別 | 法院代碼（`JID` 第一段） |
| `Year` | 整數 | 年度（`JYEAR`） |
| `Injury` | 類別 | 傷亡類型：死亡／重傷／傷害 |
| `Drunk` | 0/1 | 是否酒駕 |
| `Medical_Fee` | 數值（元） | 醫療費 |
| `Care_Fee` | 數值（元） | 看護費 |
| `Work_Loss` | 數值（元） | 工作／勞動能力損失 |
| `Fault_Ratio` | 數值（%） | 與有過失比例 |
| `Verdict_Total` | 數值（元） | 判決給付總額（**含目標值，建模時排除以防資料洩漏**） |
| `Mental_Damage` | 數值（元） | 精神慰撫金（**預測目標 y**） |

**`dataset_cleaned.csv`（③ 額外新增）欄位：**

| 欄位 | 說明 |
| --- | --- |
| `Injury_Level` | `Injury` 的順序編碼（3/2/1/0） |
| `Court_*` | `Court` 的 One-Hot 欄位（多欄） |
| `Medical_Fee_log` / `Care_Fee_log` / `Work_Loss_log` / `Mental_Damage_log` | 對數轉換後特徵 |

---

## 🧠 4. 模型建構 (Modeling)

### 4.1 演算法選擇
針對具高度非線性關係的表格型特徵，選用樹狀模型 **Random Forest Regressor（隨機森林迴歸）**。

### 4.2 訓練策略
- **Train/Test Split**：80%（5,640 筆）/ 20%（1,410 筆）隨機切割。
- **超參數**：`max_depth=10`、`min_samples_leaf=5`、`n_estimators=100` 以防止 Overfitting。
- **防資料洩漏**：訓練特徵排除 `Verdict_Total` 與各原始金額欄，改用 `*_log` 特徵；預測目標為 `Mental_Damage_log`，輸出時以 `expm1` 還原。

### 4.3 基準模型 (Null Model)
- **策略**：無論案件特徵為何，一律「盲猜」訓練集的精神慰撫金平均值。
- **基準誤差**：MAE 高達 494,720 元。

```bash
python 04_model_training.py
# → models/rf_model.pkl（含模型與特徵欄位名）
```

---

## 📊 5. 成效評估 (Results)

### 5.1 評估指標
選用 **MAE（平均絕對誤差）**：相較 RMSE，更能直觀反映「預測金額與法官真實判決金額平均差了幾元」，在法律實務上最具解釋力。

### 5.2 顯著進步
- **Null Model MAE**：494,720 元
- **Random Forest MAE**：304,969 元
- **進步幅度**：較盲猜基準**顯著提升 38.4%**，R-squared 達 **0.4618**。

### 5.3 特徵重要性（Top 3）
1. `Care_Fee`（看護費用）— 39%
2. `Injury_Level`（傷亡嚴重度）— 28%
3. `Medical_Fee`（醫療費用）— 18%

> **洞察**：被害人所需的照護與醫療支出越高，法官越容易認定其精神痛苦巨大，進而判賠更高的慰撫金。

---

## 💻 6. 系統展示與重現 (Demo & Reproducibility)

### 6.1 線上視覺化
使用 `Streamlit` 開發互動式 Web App，可輸入案件條件（傷亡程度、醫療費、是否酒駕等），即時呼叫模型試算賠償金額。

### 6.2 快速啟動（已實測可運作）

```bash
pip install -r requirements.txt
python 04_model_training.py          # 由 dataset_cleaned.csv 訓練，產出 rf_model.pkl
streamlit run 05_demo_app.py         # 啟動互動展示
```

### 6.3 完整重現（含前處理，需自備原始資料）

```bash
# 0) 先依 §2 取得原始 RAR、設定 config.py / 環境變數
python 01_extract_rar.py --years 2023-2025
python 02_build_dataset.py
python 03_exploratory_analysis.py
python 04_model_training.py
streamlit run 05_demo_app.py
```

### 6.4 專案挑戰 (Challenges)
- **非結構化資料擷取**：司法文書格式極不統一，最大挑戰在於以正則表達式從數十萬字的中文裁判書中精準提取各項賠償金額，並排除和解、調解案件。

---

## 🤖 7. 生成式 AI 協作歷程 (AI Collaboration Journey)

> 本節記錄本專題「從零到一」與生成式 AI 助理協作的努力過程——我們相信，在大型語言模型逐漸成為工程標配的當下，**如何下達指令、如何分工、如何在 AI 出錯時導正方向**，與最終模型的準確度同等重要。

### 7.1 開發環境與時程

| 項目 | 內容 |
| --- | --- |
| AI 助理核心 | Google DeepMind Antigravity（Agentic 程式開發助理） |
| 作業環境 | Windows 11（PowerShell 環境） |
| 語言與套件 | Python 3.12、scikit-learn、Streamlit 1.57.0 |
| 資料來源 | 司法院資料開放平臺（<https://opendata.judicial.gov.tw/>） |
| AI 協作啟動 | 2026/5/15 上午 11:37 |
| 初步架構完成 | 2026/5/16 上午 08:03 |
| 總花費時間 | 專案總跨距約 **20 小時**；實際下達 Prompt 與除錯的高密度作業時間僅約 **3〜4 小時** |

> **前置作業**：所有原始資料皆由本組親自前往司法院開放資料平臺下載至本機（`DEST_DIR`）。由於開放資料檔案極度龐大，光是下載與環境準備就耗費了相當漫長的時間——這也呼應 §0 中「①〜③ 因原始資料未隨 repo 發佈而暫無法重現」的現況。

依「精力投入比例」而非「掛機時間」來看，最耗心力的並非建模或寫網頁，而是**前期把非結構化中文裁判書轉成可用資料表**的資料工程（約佔 35%），其次為清洗與 EDA（約 25%），建模與 Demo 各約 20%。

### 7.2 階段性 Prompt 與產出結果

以下節錄不同階段下達給 Antigravity 的具體 Prompt（提示詞），以及 AI 反饋的程式碼與結果：

| 階段（時間） | 具體 Prompt（節錄） | 產出與效益 |
| --- | --- | --- |
| 啟動與架構（5/15 11:37） | 「請參考這份簡報 `topic99_finalProject.pptx`，引導我完成這個專題。」「1. 如貼圖，資料集擷取中…」 | AI 讀取期末報告 PPT，規劃出 Input → Modeling → Results → Demo 四大階段的開發藍圖。 |
| 資料工程（5/15 下午） | 「請問會將對應的裁判書存到特定的地方嗎？」「我剛剛已經執行中了，怎麼辦？」 | AI 撰寫 `01_extract_rar.py`，並在我們反映執行中斷後，迅速加入「斷點續傳」防呆機制。 |
| 資料集說明（5/15 晚上） | 「關於資料集，請給我一份 word 檔說明。」 | AI 不僅完成特徵工程腳本 `02_build_dataset.py`（正則擷取），還自動產出 Data Dictionary 說明文件。 |
| 建模與展示（5/16 08:03） | 「請問有按照我們老師的 ppt 要求方向製作嗎？」「好，請繼續指導我。」 | AI 依循 PPT 建立含 Null Model 基準比較的 `04_model_training.py`，並以 Streamlit 開發出 `05_demo_app.py`。 |

### 7.3 人機協作的反思與價值

面對如此龐大的非結構化中文法律文件，若僅靠純人力編寫腳本，開發時間恐需數週。Antigravity 展現了極高的執行力：當 Regex 抓取金額失敗時，我們只需把報錯資訊或遺漏樣本拋給 AI，幾秒內即可拿到修正後的新版程式碼。

但我們也清楚意識到 **AI 的輸出必須經過人類驗收**——它可能抓錯金額、誤納和解案件，也可能在缺乏領域提醒時忽略資料洩漏（如將 `Verdict_Total` 納入特徵），這些都得靠具法律與資料判斷力的組員把關。

在這次從零到一的協作中，我們深刻體會到：工程師的角色已從「**撰寫語法的打字員**」，轉變為「**制定策略、設計架構、提供領域知識與品管測試的專案經理**」。透過精準的 Prompt 與持續的人機迭代，我們將原本需耗時數週的期末專案，壓縮在約 20 小時的跨距內落地。

> 📄 完整協作歷程另見組內文件《生成式 AI 協作歷程報告（補充）》。

---

## 🧩 8. 已知問題與待辦 (Known Issues & TODO)

- [ ] 將 ①〜③ 的可重現性自動化（提供小型範例 JSON 或 `Selected_JSON` 子集，讓不下載完整原始資料者也能跑通）。
- [ ] 補上 `requirements.txt` 的版本鎖定（pinned versions）以利跨機器一致。
- [ ] 確認 `config.py` 各預設相對路徑與本 README §0.2 的建議結構一致。
- [ ] 未來導入 LLM 直接理解判決抗辯與情節，突破正則表達式的極限，提升預測表現。

---

## 👥 貢獻紀錄 (Changelog)

- **PR #1（`bagel211-svg`）**：優化 macOS 執行路徑與升級 Streamlit 預測功能；相對路徑／`config.py` 重構的基礎。
- **PR #2（`stevenwangCR`）**：新增 Final Project 檔案（資料前處理與建模等腳本）。
- **本次更新（`juangig6` / 莊一桂）**：補充本 README 的「原始資料說明」、前處理管線文件、重現狀態、資料字典，以及「生成式 AI 協作歷程」。

---
*本專題為國立政治大學資料科學課程期末專案（第一組）*


