#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
05_demo_app.py
車禍精神慰撫金預測 - 互動式展示系統
對應期末專案 PPTX: 4. Demo (On-line visualization)

使用方式：在專案根目錄輸入 `streamlit run code/05_demo_app.py`
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib

from config import MODEL_PATH

# 設定頁面資訊
st.set_page_config(page_title="車禍精神慰撫金預測 AI", page_icon="⚖️", layout="centered")

@st.cache_resource
def load_model(model_path):
    if not model_path.exists():
        return None, None
    data = joblib.load(model_path)
    return data['model'], data['features']

model, feature_names = load_model(MODEL_PATH)

# ==========================================
# 介面設計
# ==========================================
st.title("⚖️ 車禍案件：精神慰撫金 AI 預測系統")
st.markdown("""
本系統基於 **司法院開放資料 (112-114年)**，透過機器學習 Random Forest 模型，分析 **7,050** 筆實際判決，協助預估車禍案件合理的「精神慰撫金」金額。
""")

if model is None:
    st.error("找不到訓練好的模型檔案，請先在專案根目錄執行 `python3 code/04_model_training.py`。")
    st.stop()

# 分割兩個版面
col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 案件基本特徵")
    injury = st.selectbox("傷亡程度 (最關鍵因素)", ["傷害", "重傷", "死亡"])
    drunk = st.radio("肇事者是否酒駕", ["否", "是"])
    fault_ratio = st.slider("原告與有過失比例 (%)", min_value=0, max_value=100, value=0, step=10, 
                            help="例如：原告自己也有 30% 肇事責任")

with col2:
    st.subheader("💰 實質損害金額 (元)")
    medical_fee = st.number_input("醫療費用", min_value=0, value=50000, step=10000)
    care_fee = st.number_input("看護費用", min_value=0, value=0, step=10000)
    work_loss = st.number_input("工作損失 (勞動力減損)", min_value=0, value=0, step=10000)

st.divider()

# ==========================================
# 預測邏輯
# ==========================================
if st.button("🚀 進行 AI 預測", use_container_width=True):
    # 建立一個全為 0 的 DataFrame，欄位與訓練時完全一致
    input_data = pd.DataFrame(0, index=[0], columns=feature_names)
    
    # 填入使用者輸入的數值
    # 1. 處理類別編碼
    injury_mapping = {'死亡': 3, '重傷': 2, '傷害': 1}
    input_data['Injury_Level'] = injury_mapping[injury]
    input_data['Drunk'] = 1 if drunk == "是" else 0
    input_data['Fault_Ratio'] = fault_ratio
    
    # 2. 處理金額對數轉換 (Log Transform)
    input_data['Medical_Fee_log'] = np.log1p(medical_fee)
    input_data['Care_Fee_log'] = np.log1p(care_fee)
    input_data['Work_Loss_log'] = np.log1p(work_loss)
    
    # (註：為了簡化，法院欄位我們保持預設全為 0，這代表以基準效應計算)
    
    with st.spinner("AI 模型運算中..."):
        # 預測的是 log 值
        pred_log = model.predict(input_data)[0]
        # 轉回真實金額
        pred_real = np.expm1(pred_log)
        
    st.success("✅ 預測完成！")
    
    # 顯示結果
    st.markdown(f"""
    <div style="background-color:#f0f2f6;padding:20px;border-radius:10px;text-align:center;">
        <h3 style="color:#31333F;">預估精神慰撫金</h3>
        <h1 style="color:#0068c9;font-size:48px;">NT$ {int(pred_real):,}</h1>
        <p style="color:#888;">(模型平均絕對誤差 MAE 約為 30.4 萬元)</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 顯示雷達圖或條形圖解釋 (Feature Importance Demo)
    st.markdown("### 📊 影響本次預測的關鍵因素")
    st.markdown("- **最主要因素**：傷亡程度 (`Injury_Level`) 與 實質損害 (`Medical_Fee`, `Care_Fee`)。")
    st.markdown("- **判決趨勢**：通常醫療與看護費越高，法官心證上會認為被害人受到的痛苦越大，連帶提高精神慰撫金。")
