# 期末報告最後衝刺清單
* 各項目請自行認領自行增減調整，有更新就快點 commit & push 就好
* 先分三類就好吧？各項目要放到哪個分類可自行調整
* 本來有考慮 github project，簡單又酷炫，但我想想覺得先用 markdown todo list 就好了。<br>
格式寫成：[完成勾選框] 項目說明，細節放在項目符號下第二行起 (認領負責人)<br>
例如：<br>
```markdown
[x] 開始找新工作(Kevin)
年薪百萬以上
交通半小時內最好可WFH
主管同事拜託要有sense
工作項目有趣而且有高度成長空間
```


---



## P0
不做的話會爆炸

* [x] 只是用來展示打勾勾長什麼樣子的範例虛項目，上面 block 呈現不出來
### P0: 必須盡快完成，不然一定會被打爆或做事會很不方便
* [] macos 路徑相容性/相對路徑問題（Eni 已在PR中提出做法, Kevin 會再整合）
* [] double check 所有程式都會動，包含資料處理、模型訓練以及UI
* [] README/code/投影片的內容一致性
* [] 整合/優化 UI streamlit app
* [] 準備上台進行簡報

## P1
做了比較能 defend，不然可能會被老師 challenge 到爆炸
* [] 把程式碼/資料夾結構整理成老師建議的範本格式 (Kevin)
* [] 把程式碼推到老師指定的 github repo
* [] README 提到 GridSearchCV / hyperparameter tuning，但 code 目前看起來比較像固定參數 (Kevin)<br>
需要確認是否要補回調參過程或修改說明。
* [] Regex 規則釐清與修正（即我們在下課時的討論）<br>
從裁判書抽資料是整個專案最大的資料品質風險，可以在報告中補充說明，甚至簡單人工抽樣檢查幾筆。
* [] 重新整理投影片
* [] 初創專案程式碼時的 ai prompt (Kuei)
* [] 補充說明原始資料的定義 (Kuei)


## P2 
加分事項，有很好，沒有可能還好?以 P0, P1 為優先。

* [] outlier 定義和處理的改善<br>
03_exploratory_analysis.py:47-57 移除了範圍在 10,000 到 10,000,000 之外的案例，並將費用欄位限制（caps）在 50,000,000 以內。這樣做雖然能清除明顯的錯誤，但同時也有排除極端但合法（真實存在）案例的風險。更好的做法是：從實證角度說明這些閾值的合理性，或者與基於分位數的裁剪（quantile-based trimming）、縮尾處理（Winsorization）或強健模型（robust models）進行比較
* [] 現在是 random train/test split，如果目標是預測未來案件，可以考慮補一個 time-based split 的討論，<br>
例如用較早年度訓練、較新年度測試，至少放在 limitation / future work。
* [] 用較近期的資料進行回測
* [] 預測方式/演算法模型的改善<br>
目前唯一的基準模型只有「預測平均值」<br>作為 null model 固然可行，但在科學嚴謹性上還不夠。建議增加：
  - 中位數基準模型（median baseline）
  - 線性迴歸 / 正則化迴歸（linear / regularized regression）
  - 或者是 XGBoost、LightGBM 或 CatBoost<br>
如此一來，你才能證明隨機森林（Random Forest）是否真的是最合適的模型。
* [] 單點預測容易讓人誤會<br>
可以保留目前 Streamlit 的區間概念，但要說清楚那是模型參考區間，不是正式法律判斷或統計信賴區間。
* [] 錯誤分析（Error analysis）偏單薄
程式碼僅報告了整體的 MAE 和 $R^2$（04_model_training.py:88-97）。<br>
建議另外依據以下維度來衡量錯誤：
  - 傷害嚴重程度
  - 醉酒與非醉酒
  - 法院
  - 年份低／中／高判決金額區間<br>
  一個平均 MAE 表現不錯的模型，在最核心的子群體上仍可能表現得一塌糊塗。
