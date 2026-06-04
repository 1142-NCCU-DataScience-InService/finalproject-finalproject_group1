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
import altair as alt
from pathlib import Path

from config import MODEL_PATH, CLEANED_DATASET_CSV

# 頁面基本設定
st.set_page_config(
    page_title="車禍精神慰撫金 AI 預測與分析系統",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# 法院代碼與中文名稱對照表
# ─────────────────────────────────────────────
COURT_CODE_TO_NAME = {
    "CCEV": "臺灣屏東地方法院（潮州簡易庭）",
    "CDEV": "臺灣橋頭地方法院",
    "CHDV": "臺灣彰化地方法院",
    "CHEV": "臺灣彰化地方法院（員林簡易庭）",
    "CLEV": "臺灣桃園地方法院（中壢簡易庭）",
    "CPEV": "臺灣新竹地方法院（竹北簡易庭）",
    "CSEV": "臺灣橋頭地方法院（民事/簡易分庭）",
    "CTDM": "臺灣橋頭地方法院（簡易庭）",
    "CTDV": "臺灣橋頭地方法院（民事庭）",
    "CYDV": "臺灣嘉義地方法院",
    "CYEV": "臺灣嘉義地方法院（朴子/嘉義簡易庭）",
    "FSEV": "臺灣高雄地方法院（鳳山簡易庭）",
    "FYEV": "臺灣臺中地方法院（豐原簡易庭）",
    "GSEV": "臺灣橋頭地方法院（岡山簡易庭）",
    "HLDV": "臺灣花蓮地方法院",
    "HLEV": "臺灣花蓮地方法院（玉里簡易庭）",
    "HLHM": "臺灣高等法院花蓮分院（民事庭）",
    "HLHV": "臺灣高等法院花蓮分院（簡易庭）",
    "HUEV": "臺灣雲林地方法院（虎尾簡易庭）",
    "ILDV": "臺灣宜蘭地方法院",
    "ILEV": "臺灣宜蘭地方法院（羅東簡易庭）",
    "KLDV": "臺灣基隆地方法院",
    "KMDM": "福建金門地方法院",
    "KMEV": "福建金門地方法院（簡易庭）",
    "KSDM": "臺灣高雄地方法院（簡易庭）",
    "KSDV": "臺灣高雄地方法院（民事庭）",
    "KSEV": "臺灣高雄地方法院（岡山/旗山簡易庭）",
    "KSHM": "臺灣高等法院高雄分院（民事庭）",
    "KSHV": "臺灣高等法院高雄分院（簡易庭）",
    "LTEV": "臺灣宜蘭地方法院（宜蘭簡易庭）",
    "MKEM": "臺灣澎湖地方法院",
    "MKEV": "臺灣澎湖地方法院（簡易庭）",
    "MLDV": "臺灣苗栗地方法院",
    "NHEV": "臺灣士林地方法院（內湖簡易庭）",
    "NTDV": "臺灣南投地方法院",
    "NTEV": "臺灣南投地方法院（埔里/竹山簡易庭）",
    "OLEV": "臺灣彰化地方法院（北斗簡易庭）",
    "PCDV": "臺灣新北地方法院（民事庭）",
    "PCEV": "臺灣新北地方法院（板橋簡易庭）",
    "PDEV": "臺灣彰化地方法院（員林簡易庭）",
    "PHDM": "臺灣澎湖地方法院（簡易庭）",
    "PHDV": "臺灣澎湖地方法院",
    "PKEV": "臺灣雲林地方法院（北港簡易庭）",
    "PTDV": "臺灣屏東地方法院",
    "PTEV": "臺灣屏東地方法院（屏東簡易庭）",
    "SCDV": "臺灣新竹地方法院",
    "SDEV": "臺灣臺中地方法院（沙鹿簡易庭）",
    "SJEV": "臺灣新北地方法院（三重簡易庭）",
    "SLDV": "臺灣士林地方法院",
    "SLEV": "臺灣士林地方法院（士林簡易庭）",
    "SSEV": "臺灣臺南地方法院（新市/柳營簡易庭）",
    "STEV": "臺灣臺北地方法院（新店簡易庭）",
    "SYEV": "臺灣臺南地方法院（新營簡易庭）",
    "TCDV": "臺灣臺中地方法院",
    "TCEV": "臺灣臺中地方法院（臺中簡易庭）",
    "TCHV": "臺灣高等法院臺中分院",
    "TLEV": "臺灣雲林地方法院（斗六簡易庭）",
    "TNDV": "臺灣臺南地方法院",
    "TNEV": "臺灣臺南地方法院（臺南簡易庭）",
    "TNHV": "臺灣高等法院臺南分院",
    "TPDV": "臺灣臺北地方法院",
    "TPEV": "臺灣臺北地方法院（臺北簡易庭）",
    "TPHV": "臺灣高等法院",
    "TTEV": "臺灣臺東地方法院",
    "TYDV": "臺灣桃園地方法院",
    "TYEV": "臺灣桃園地方法院（桃園簡易庭）",
    "ULDV": "臺灣雲林地方法院",
}

# ─────────────────────────────────────────────
# 快取加載模型與資料
# ─────────────────────────────────────────────
@st.cache_resource
def load_model_data(model_path):
    if not model_path.exists():
        return None, None
    data = joblib.load(model_path)
    return data['model'], data['features']

@st.cache_data
def load_dataset(cleaned_csv_path):
    if not cleaned_csv_path.exists():
        return None
    return pd.read_csv(cleaned_csv_path)

model, feature_names = load_model_data(MODEL_PATH)
df_cleaned = load_dataset(CLEANED_DATASET_CSV)

# ─────────────────────────────────────────────
# 自訂 CSS 樣式優化 (Aesthetic Enhancement)
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* 全域字體優化 */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Noto+Sans+TC:wght@300;400;500;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Outfit', 'Noto Sans TC', sans-serif;
    }
    
    /* 玻璃擬態與陰影卡片 */
    .metric-card {
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid rgba(226, 232, 240, 1);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.03);
        transition: transform 0.2s ease-in-out;
        margin-bottom: 20px;
    }
    .metric-card:hover {
        transform: translateY(-2px);
    }
    
    /* 標題與視覺重點 */
    .gradient-text {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }
    
    .highlight-card {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border: 1px solid #bbf7d0;
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    
    .highlight-value {
        color: #166534;
        font-size: 3rem;
        font-weight: 800;
        margin: 10px 0;
    }
    
    .secondary-value {
        color: #1e3a8a;
        font-size: 2.2rem;
        font-weight: 700;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 側邊欄資訊
# ─────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/color/144/scales.png", width=70)
    st.markdown("<h2 class='gradient-text'>車禍賠償預測系統</h2>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
    **📊 模型效能指標**
    - **模型演算法**：隨機森林 (Random Forest)
    - **訓練資料量**：7,045 筆實際判決
    - **平均絕對誤差 (MAE)**：約 31.4 萬元
    - **決定係數 ($R^2$)**：0.43
    - **效能提升**：比盲猜平均值提升 **37.1%**
    """)
    st.markdown("---")
    st.caption("ℹ️ 本系統僅供學術研究與初步賠償金額估計參考，實際判決結果仍以法院心證為準。")

# ─────────────────────────────────────────────
# 主頁面結構
# ─────────────────────────────────────────────
st.markdown("<h1 style='margin-bottom: 0px;'>⚖️ 車禍案件：精神慰撫金 AI 預測與分析系統</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #64748b; font-size: 1.1rem; margin-top: 5px;'>基於 112~114 年司法院開放裁判書大數據，結合機器學習技術進行精準回歸分析</p>", unsafe_allow_html=True)

if model is None:
    st.error("❌ 找不到訓練好的模型檔案。請先在專案目錄下執行 `python3 code/04_model_training.py`。")
    st.stop()

# 建立兩個主要功能頁籤
tab1, tab2 = st.tabs(["🔮 AI 慰撫金預測", "📈 歷史裁判資料分析"])

# ==============================================================================
# TAB 1: AI 預測
# ==============================================================================
with tab1:
    st.markdown("### ✍️ 請輸入車禍案件具體特徵進行預估")
    
    # 建立表單輸入區
    col_input1, col_input2 = st.columns(2)
    
    with col_input1:
        st.markdown("##### **📝 案情基本特徵**")
        
        # 傷亡程度
        injury = st.selectbox(
            "1. 被害人傷亡程度 (影響模型最關鍵因子)",
            options=["傷害", "重傷", "死亡"],
            help="根據判決書正本，區分一般傷害、重傷(符合刑法第10條重傷定義，如失明、截肢等)或死亡。"
        )
        
        # 肇事者酒駕
        drunk = st.radio(
            "2. 肇事者是否酒駕 / 飲酒後駕車",
            options=["否", "是"],
            horizontal=True,
            help="判決書中提及被告有酒後駕車行為。"
        )
        
        # 過失責任比例
        fault_ratio = st.slider(
            "3. 原告 (被害人) 與有過失比例 (%)",
            min_value=0,
            max_value=100,
            value=0,
            step=10,
            help="原告自身在車禍事故中亦有過失，法官會依此比例減輕被告賠償責任。例如：原告過失比例 30%，則可獲得 70% 的賠償金。"
        )
        
        # 訴訟法院
        all_courts_list = sorted(list(COURT_CODE_TO_NAME.keys()))
        court_options = [f"{COURT_CODE_TO_NAME[code]} ({code})" for code in all_courts_list]
        selected_court_str = st.selectbox(
            "4. 審理之法院 / 簡易分庭",
            options=court_options,
            index=court_options.index("臺灣臺北地方法院 (TPDV)"),
            help="不同法院與地區簡易庭，在實務判決之精神慰撫金基準可能存在地區差異。"
        )
        
    with col_input2:
        st.markdown("##### **💰 實質財產損害金額 (新臺幣元)**")
        
        medical_fee = st.number_input(
            "1. 醫療費用總計",
            min_value=0,
            max_value=50000000,
            value=50000,
            step=10000,
            format="%d",
            help="包括醫療材料費、門診與住院費用等。"
        )
        
        care_fee = st.number_input(
            "2. 看護費用總計",
            min_value=0,
            max_value=50000000,
            value=0,
            step=10000,
            format="%d",
            help="由親屬或職業看護照顧之合理費用總額。"
        )
        
        work_loss = st.number_input(
            "3. 工作損失與勞動力減損補償",
            min_value=0,
            max_value=50000000,
            value=0,
            step=10000,
            format="%d",
            help="因傷休養期間的工資損失，或經鑑定後之勞動能力喪失金額。"
        )
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 點擊預測按鈕
    if st.button("🚀 進行 AI 慰撫金估算", use_container_width=True):
        # 1. 建立空輸入 DataFrame
        input_data = pd.DataFrame(0, index=[0], columns=feature_names)
        
        # 2. 設定特徵值
        # 傷亡程度對照
        injury_mapping = {'死亡': 3, '重傷': 2, '傷害': 1}
        input_data['Injury_Level'] = injury_mapping[injury]
        input_data['Drunk'] = 1 if drunk == "是" else 0
        input_data['Fault_Ratio'] = fault_ratio
        
        # 金額對數轉換
        input_data['Medical_Fee_log'] = np.log1p(medical_fee)
        input_data['Care_Fee_log'] = np.log1p(care_fee)
        input_data['Work_Loss_log'] = np.log1p(work_loss)
        
        # 法院設定
        selected_code = selected_court_str.split('(')[-1].strip(')')
        court_feature = f"Court_{selected_code}"
        if court_feature in feature_names:
            input_data[court_feature] = 1
            
        # 3. 模型預測
        with st.spinner("🧠 AI 模型深度運算中..."):
            pred_log = model.predict(input_data)[0]
            pred_real = np.expm1(pred_log)
            
        # 4. 計算過失相抵後的金額
        net_pred_real = pred_real * (1 - fault_ratio / 100)
        
        # 5. 呈現預測結果卡片 (Highlight Display)
        st.markdown("<h4 style='margin-bottom:10px;'>🔮 預估分析結果</h4>", unsafe_allow_html=True)
        col_res1, col_res2 = st.columns(2)
        
        with col_res1:
            st.markdown(f"""
            <div class="metric-card" style="text-align: center;">
                <p style="color: #64748b; font-weight: 500; font-size: 1.1rem; margin-bottom: 5px;">🤖 法官心證估算：精神慰撫金金額</p>
                <div class="secondary-value">NT$ {int(pred_real):,} 元</div>
                <p style="color: #94a3b8; font-size: 0.9rem; margin-top: 5px;">(尚未扣除原告過失比例)</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_res2:
            st.markdown(f"""
            <div class="highlight-card">
                <p style="color: #15803d; font-weight: 600; font-size: 1.2rem; margin-bottom: 5px;">💰 過失相抵扣除後：原告實得賠償額</p>
                <div class="highlight-value">NT$ {int(net_pred_real):,} 元</div>
                <p style="color: #166534; font-size: 0.95rem; margin-top: 5px;">原告過失比例：<b>{fault_ratio}%</b>（應負擔自己過失責任）</p>
            </div>
            """, unsafe_allow_html=True)

        st.info(
            "⚠️ 本結果為機器學習模型的**參考估計值**，並非正式法律判斷，也不是統計上的信賴區間或預測區間。"
            "實際判決金額仍會受個案事實、證據、法院見解與法官裁量影響，請勿單獨以此數字作為訴訟或和解依據。"
        )

        # 6. 加入與歷史資料分布的視覺化對比
        if df_cleaned is not None:
            st.markdown("---")
            st.markdown("### 📊 預測值與歷史案件判決分布對比")
            
            # 動態調整直方圖的上限，避免長尾數據導致圖表難以閱讀
            max_limit = max(1000000, pred_real * 1.5)
            df_plot = df_cleaned[df_cleaned['Mental_Damage'] <= max_limit]
            
            hist_chart = alt.Chart(df_plot).mark_bar(
                color='#3b82f6', 
                opacity=0.6,
                cornerRadiusTopLeft=4,
                cornerRadiusTopRight=4
            ).encode(
                alt.X("Mental_Damage:Q", bin=alt.Bin(maxbins=50), title="法院判決精神慰撫金 (元)"),
                alt.Y("count()", title="案件數量 (件)")
            )
            
            # 加入目前預測線
            line_df = pd.DataFrame({'x': [pred_real], 'label': ['AI 預估值']})
            rule_chart = alt.Chart(line_df).mark_rule(
                color='#ef4444', 
                strokeWidth=3, 
                strokeDash=[5, 5]
            ).encode(
                x='x:Q'
            )
            
            text_chart = alt.Chart(line_df).mark_text(
                align='left',
                dx=10,
                dy=-120,
                color='#ef4444',
                fontSize=14,
                fontWeight='bold'
            ).encode(
                x='x:Q',
                text='label:N'
            )
            
            combined_chart = (hist_chart + rule_chart + text_chart).properties(
                width=800,
                height=350
            )
            
            st.markdown(f"##### 歷史案件慰撫金分布圖（限制顯示額度 {int(max_limit):,} 元以內，當前 AI 估計：NT$ {int(pred_real):,}）")
            st.altair_chart(combined_chart, use_container_width=True)
            
        st.markdown("""
        > 💡 **判決趨勢與心證說明**：
        > 1. **傷亡嚴重度** 是決定精神慰撫金最重要的基準，死亡或重大殘疾案件之慰撫金通常為傷害案的數倍甚至十倍以上。
        > 2. **實質損害關聯性**：法官通常會依據醫療費用及看護費用高低，間接佐證被害人之生理受創及身心痛苦程度，進而影響慰撫金金額之裁量。
        > 3. **與有過失 (過失相抵)**：依民法第217條規定，損害之發生或擴大，被害人與有過失者，法院得減免賠償金額。此項減免會套用在整體賠償額上。
        """)

# ==============================================================================
# TAB 2: 歷史資料統計與模型分析
# ==============================================================================
with tab2:
    st.markdown("### 📈 司法院開放資料統計看板 (共 7,045 筆案件)")
    
    if df_cleaned is not None:
        # 1. 頂部 KPI 卡片
        col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
        
        with col_kpi1:
            st.markdown(f"""
            <div class="metric-card" style="text-align: center;">
                <p style="color: #64748b; font-size: 0.9rem; margin-bottom: 2px;">📂 分析總案件數</p>
                <h2 style="color: #1e3a8a; font-weight: 700; margin: 5px 0;">{len(df_cleaned):,} 筆</h2>
                <p style="color: #94a3b8; font-size: 0.8rem;">112-114 年裁判書</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_kpi2:
            avg_mental = df_cleaned['Mental_Damage'].mean()
            st.markdown(f"""
            <div class="metric-card" style="text-align: center;">
                <p style="color: #64748b; font-size: 0.9rem; margin-bottom: 2px;">💵 慰撫金平均值</p>
                <h2 style="color: #0f766e; font-weight: 700; margin: 5px 0;">NT$ {int(avg_mental):,}</h2>
                <p style="color: #94a3b8; font-size: 0.8rem;">包含各類傷亡程度</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_kpi3:
            median_mental = df_cleaned['Mental_Damage'].median()
            st.markdown(f"""
            <div class="metric-card" style="text-align: center;">
                <p style="color: #64748b; font-size: 0.9rem; margin-bottom: 2px;">📊 慰撫金中位數</p>
                <h2 style="color: #d97706; font-weight: 700; margin: 5px 0;">NT$ {int(median_mental):,}</h2>
                <p style="color: #94a3b8; font-size: 0.8rem;">排除極端值干擾</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_kpi4:
            drunk_count = df_cleaned['Drunk'].sum()
            st.markdown(f"""
            <div class="metric-card" style="text-align: center;">
                <p style="color: #64748b; font-size: 0.9rem; margin-bottom: 2px;">🍺 涉及酒駕比例</p>
                <h2 style="color: #be123c; font-weight: 700; margin: 5px 0;">{drunk_count / len(df_cleaned) * 100:.2f} %</h2>
                <p style="color: #94a3b8; font-size: 0.8rem;">共 {drunk_count} 筆涉酒駕案</p>
            </div>
            """, unsafe_allow_html=True)
            
        # 2. 圖表展示：傷亡程度與慰撫金關聯、模型特徵重要性
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.markdown("##### 👥 傷亡嚴重度與平均精神慰撫金")
            # 依傷亡嚴重度分組計算均值
            injury_stats = df_cleaned.groupby('Injury')['Mental_Damage'].agg(['mean', 'median', 'count']).reset_index()
            # 排序
            injury_stats['sort_order'] = injury_stats['Injury'].map({'死亡': 3, '重傷': 2, '傷害': 1})
            injury_stats = injury_stats.sort_values(by='sort_order')
            
            bar_injury = alt.Chart(injury_stats).mark_bar(color='#10b981', cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
                alt.X('Injury:N', sort=['傷害', '重傷', '死亡'], title='傷亡程度'),
                alt.Y('mean:Q', title='平均慰撫金金額 (元)'),
                tooltip=[
                    alt.Tooltip('Injury:N', title='傷亡程度'),
                    alt.Tooltip('mean:Q', title='平均值', format=',.0f'),
                    alt.Tooltip('median:Q', title='中位數', format=',.0f'),
                    alt.Tooltip('count:Q', title='案件量')
                ]
            ).properties(height=300)
            
            st.altair_chart(bar_injury, use_container_width=True)
            
        with col_chart2:
            st.markdown("##### 🔍 預測模型機器學習之特徵重要性")
            # 特徵重要性分析
            importances = model.feature_importances_
            feat_imp = pd.DataFrame({
                'Feature': feature_names,
                'Importance': importances
            }).sort_values(by='Importance', ascending=False).head(10)
            
            # 中文映射
            feature_chi_map = {
                'Drunk': '是否酒駕',
                'Fault_Ratio': '原告過失比例',
                'Injury_Level': '傷亡嚴重度',
                'Medical_Fee_log': '醫療費用 (log)',
                'Care_Fee_log': '看護費用 (log)',
                'Work_Loss_log': '工作損失 (log)'
            }
            
            feat_imp['Feature_Chi'] = feat_imp['Feature'].map(feature_chi_map)
            # 法院特徵對照
            for idx, row in feat_imp.iterrows():
                feat = row['Feature']
                if feat.startswith('Court_'):
                    code = feat.replace('Court_', '')
                    feat_imp.at[idx, 'Feature_Chi'] = f"審理地院: {COURT_CODE_TO_NAME.get(code, code)}"
                    
            feat_imp['Feature_Chi'] = feat_imp['Feature_Chi'].fillna(feat_imp['Feature'])
            
            imp_chart = alt.Chart(feat_imp).mark_bar(color='#4f46e5', cornerRadiusBottomRight=4, cornerRadiusTopRight=4).encode(
                alt.X('Importance:Q', title='相對影響重要性 (Relative Importance)'),
                alt.Y('Feature_Chi:N', sort='-x', title='影響因素 (特徵)'),
                tooltip=[
                    alt.Tooltip('Feature_Chi:N', title='特徵'),
                    alt.Tooltip('Importance:Q', title='重要性比例', format='.4f')
                ]
            ).properties(height=300)
            
            st.altair_chart(imp_chart, use_container_width=True)
            
        # 3. 數據查詢與過濾
        st.markdown("---")
        st.markdown("##### 🔍 歷史判決案例局部探索區")
        
        # 篩選條件
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        with col_filter1:
            sel_inj = st.multiselect("過濾傷亡程度", options=["傷害", "重傷", "死亡"], default=["重傷", "死亡"])
        with col_filter2:
            sel_drunk = st.selectbox("酒駕過濾", options=["不限", "無酒駕", "有酒駕"])
        with col_filter3:
            max_view_val = st.slider("最高慰撫金上限 (萬元)", min_value=10, max_value=1000, value=300, step=50)
            
        # 應用過濾
        df_filtered = df_cleaned[df_cleaned['Injury'].isin(sel_inj)]
        if sel_drunk == "無酒駕":
            df_filtered = df_filtered[df_filtered['Drunk'] == 0]
        elif sel_drunk == "有酒駕":
            df_filtered = df_filtered[df_filtered['Drunk'] == 1]
            
        df_filtered = df_filtered[df_filtered['Mental_Damage'] <= max_view_val * 10000]
        
        # 對顯示的列重命名與呈現
        show_cols = {
            'JID': '裁判編號',
            'Injury': '傷亡程度',
            'Drunk': '是否酒駕',
            'Medical_Fee': '醫療費用',
            'Care_Fee': '看護費用',
            'Work_Loss': '工作損失',
            'Fault_Ratio': '與有過失%',
            'Verdict_Total': '判決總給付額',
            'Mental_Damage': '精神慰撫金'
        }
        
        df_show = df_filtered[list(show_cols.keys())].copy()
        df_show['Drunk'] = df_show['Drunk'].map({0: '否', 1: '是'})
        df_show = df_show.rename(columns=show_cols)
        
        st.dataframe(df_show.head(150), height=300, use_container_width=True)
        st.caption(f"💡 目前篩選條件下符合歷史案件共 {len(df_filtered):,} 筆，上方清單顯示前 150 筆。")
        
    else:
        st.info("⚠️ 找不到清洗後的歷史資料集 `data/processed/dataset_cleaned.csv`，無法載入統計分析面板。")
