"""
頁面 2：減少賠償建議
透過 What-if 模擬 + 歷史資料統計，告訴使用者如何降低判賠金額。
"""
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from config import DATASET_CSV, MODEL_MAE
from predictor import load_model, predict_amount

st.set_page_config(page_title="減少賠償建議", page_icon="💡", layout="wide")
st.title("💡 如何降低賠償金額？")
st.caption("基於 7,050 筆真實判決的策略建議與 What-if 模擬")

model, feature_names = load_model()
if model is None or not DATASET_CSV.exists():
    st.error("缺少模型或資料集，請先執行 `python train_model.py`")
    st.stop()


@st.cache_data
def load_dataset():
    return pd.read_csv(DATASET_CSV)


df = load_dataset()

# ====================================================
# 第一區：輸入基準情境
# ====================================================
st.header("Step 1 ── 輸入你的案件條件")

with st.form("baseline"):
    c1, c2, c3 = st.columns(3)
    with c1:
        injury = st.selectbox("傷亡程度", ["傷害", "重傷", "死亡"])
        drunk = st.radio("肇事者是否酒駕", ["否", "是"], horizontal=True)
    with c2:
        fault_ratio = st.slider("原告與有過失比例 (%)", 0, 100, 0, 10)
        medical_fee = st.number_input("醫療費用 (元)", 0, value=100000, step=10000)
    with c3:
        care_fee = st.number_input("看護費用 (元)", 0, value=200000, step=10000)
        work_loss = st.number_input("工作損失 (元)", 0, value=100000, step=10000)

    go = st.form_submit_button("🔍 開始分析", type="primary", use_container_width=True)

if not go:
    st.info("👆 請輸入案件條件並按下「開始分析」")
    st.stop()

baseline_kwargs = dict(
    injury=injury,
    drunk=(drunk == "是"),
    fault_ratio=fault_ratio,
    medical_fee=medical_fee,
    care_fee=care_fee,
    work_loss=work_loss,
)
baseline = predict_amount(model, feature_names, **baseline_kwargs)

st.markdown("---")
st.header("Step 2 ── 基準預測")
st.metric("目前條件下預估慰撫金", f"NT$ {int(baseline):,}", help=f"MAE ±{MODEL_MAE:,} 元")

# ====================================================
# 第二區：What-if 策略模擬
# ====================================================
st.markdown("---")
st.header("Step 3 ── 各項策略可減少多少？")
st.caption("固定其他條件，只改變一個變數，看模型預測金額如何變化。")

strategies = []

# 策略 A：提高與有過失比例
if fault_ratio < 100:
    for delta in [10, 20, 30]:
        new_fr = min(fault_ratio + delta, 100)
        kw = {**baseline_kwargs, "fault_ratio": new_fr}
        pred = predict_amount(model, feature_names, **kw)
        strategies.append({
            "策略": f"主張對方與有過失 +{delta}% (從 {fault_ratio}% → {new_fr}%)",
            "類別": "舉證對方過失",
            "預估金額": pred,
            "減少金額": baseline - pred,
            "減少比例": (baseline - pred) / baseline * 100 if baseline > 0 else 0,
        })

# 策略 B：質疑看護費合理性（看護費是 39% 最重要特徵）
if care_fee > 0:
    for pct in [0.25, 0.5, 0.75]:
        new_care = int(care_fee * (1 - pct))
        kw = {**baseline_kwargs, "care_fee": new_care}
        pred = predict_amount(model, feature_names, **kw)
        strategies.append({
            "策略": f"質疑看護費（成功減 {int(pct*100)}%：{care_fee:,} → {new_care:,}）",
            "類別": "質疑看護費",
            "預估金額": pred,
            "減少金額": baseline - pred,
            "減少比例": (baseline - pred) / baseline * 100 if baseline > 0 else 0,
        })

# 策略 C：質疑醫療費必要性（占 18%）
if medical_fee > 0:
    for pct in [0.25, 0.5]:
        new_med = int(medical_fee * (1 - pct))
        kw = {**baseline_kwargs, "medical_fee": new_med}
        pred = predict_amount(model, feature_names, **kw)
        strategies.append({
            "策略": f"質疑醫療費必要性（成功減 {int(pct*100)}%：{medical_fee:,} → {new_med:,}）",
            "類別": "質疑醫療費",
            "預估金額": pred,
            "減少金額": baseline - pred,
            "減少比例": (baseline - pred) / baseline * 100 if baseline > 0 else 0,
        })

# 策略 D：質疑工作損失
if work_loss > 0:
    kw = {**baseline_kwargs, "work_loss": int(work_loss * 0.5)}
    pred = predict_amount(model, feature_names, **kw)
    strategies.append({
        "策略": f"質疑工作損失（成功減 50%：{work_loss:,} → {int(work_loss*0.5):,}）",
        "類別": "質疑工作損失",
        "預估金額": pred,
        "減少金額": baseline - pred,
        "減少比例": (baseline - pred) / baseline * 100 if baseline > 0 else 0,
    })

if strategies:
    strat_df = pd.DataFrame(strategies).sort_values("減少金額", ascending=False).reset_index(drop=True)

    # 顯示前三大策略
    st.subheader("🏆 最有效的三個策略")
    top3 = strat_df.head(3)
    cols = st.columns(3)
    for i, (_, row) in enumerate(top3.iterrows()):
        with cols[i]:
            st.metric(
                row["類別"],
                f"-NT$ {int(row['減少金額']):,}",
                delta=f"-{row['減少比例']:.1f}%",
                delta_color="inverse",
            )
            st.caption(row["策略"])

    # 完整表格
    with st.expander("📋 查看所有策略模擬結果"):
        show_df = strat_df.copy()
        show_df["預估金額"] = show_df["預估金額"].apply(lambda x: f"NT$ {int(x):,}")
        show_df["減少金額"] = show_df["減少金額"].apply(lambda x: f"NT$ {int(x):,}")
        show_df["減少比例"] = show_df["減少比例"].apply(lambda x: f"{x:.1f}%")
        st.dataframe(show_df, use_container_width=True, hide_index=True)

    # 視覺化
    fig = px.bar(
        strat_df, x="減少金額", y="策略", color="類別", orientation="h",
        title="各策略可降低的賠償金額（元）",
        text=strat_df["減少金額"].apply(lambda x: f"-{int(x):,}"),
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=400)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("目前案件條件下，無可模擬的減少策略。")

# ====================================================
# 第三區：基於歷史資料的統計建議
# ====================================================
st.markdown("---")
st.header("Step 4 ── 來自 7,050 筆判決的統計洞察")

tab1, tab2, tab3 = st.tabs(["📉 與有過失的影響", "🍺 酒駕加重幅度", "🏥 醫療費級距"])

with tab1:
    st.markdown("**與有過失比例越高，法官判賠金額越低**")
    df_fault = df[df["Fault_Ratio"] >= 0].copy()
    df_fault["過失區間"] = pd.cut(
        df_fault["Fault_Ratio"],
        bins=[-1, 0, 20, 40, 60, 100],
        labels=["0%", "1-20%", "21-40%", "41-60%", "61-100%"],
    )
    stat = df_fault.groupby("過失區間", observed=True)["Mental_Damage"].agg(["mean", "median", "count"]).reset_index()
    stat.columns = ["原告過失區間", "平均慰撫金", "中位數", "案件數"]
    stat["平均慰撫金"] = stat["平均慰撫金"].astype(int)
    stat["中位數"] = stat["中位數"].astype(int)
    st.dataframe(stat, use_container_width=True, hide_index=True)

    fig = px.bar(stat, x="原告過失區間", y="平均慰撫金", text_auto=True,
                 title="原告與有過失比例 vs 平均慰撫金")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("**酒駕案件慰撫金通常較高**")
    stat = df.groupby("Drunk")["Mental_Damage"].agg(["mean", "median", "count"]).reset_index()
    stat["Drunk"] = stat["Drunk"].map({0: "未酒駕", 1: "有酒駕"})
    stat.columns = ["是否酒駕", "平均慰撫金", "中位數", "案件數"]
    stat["平均慰撫金"] = stat["平均慰撫金"].astype(int)
    stat["中位數"] = stat["中位數"].astype(int)
    st.dataframe(stat, use_container_width=True, hide_index=True)

    if len(stat) == 2:
        diff = stat.loc[stat["是否酒駕"] == "有酒駕", "平均慰撫金"].iloc[0] - \
               stat.loc[stat["是否酒駕"] == "未酒駕", "平均慰撫金"].iloc[0]
        st.info(f"💡 酒駕案件平均比未酒駕案件多賠 **NT$ {int(diff):,}**")

with tab3:
    st.markdown("**醫療費級距與慰撫金的關係**")
    df_med = df.copy()
    df_med["醫療費區間"] = pd.cut(
        df_med["Medical_Fee"],
        bins=[-1, 0, 50000, 200000, 500000, 1e9],
        labels=["0", "1-5萬", "5-20萬", "20-50萬", "50萬以上"],
    )
    stat = df_med.groupby("醫療費區間", observed=True)["Mental_Damage"].agg(["mean", "count"]).reset_index()
    stat.columns = ["醫療費區間", "平均慰撫金", "案件數"]
    stat["平均慰撫金"] = stat["平均慰撫金"].astype(int)
    st.dataframe(stat, use_container_width=True, hide_index=True)

    fig = px.bar(stat, x="醫療費區間", y="平均慰撫金", text_auto=True,
                 title="醫療費規模 vs 平均慰撫金")
    st.plotly_chart(fig, use_container_width=True)

# ====================================================
# 第四區：行動建議清單
# ====================================================
st.markdown("---")
st.header("Step 5 ── 給你的具體行動建議")

advice = []

if fault_ratio < 50:
    advice.append("✅ **積極舉證對方與有過失**：調閱行車紀錄器、現場照片、目擊證人；申請車禍鑑定報告。"
                  "模型顯示過失比例每提高 10%，慰撫金約下降 3–8%。")

if care_fee > 0:
    advice.append("✅ **質疑看護費合理性**（影響力 **39%**，最關鍵）：要求對方提出看護費收據、"
                  "醫師證明書、實際看護天數；若是親屬看護，主張以較低標準計算。")

if medical_fee > 0:
    advice.append("✅ **質疑醫療費必要性**（影響力 **18%**）：區分必要醫療 vs. 自費療程；"
                  "對自費項目（如雙人房、特殊治療）主張不予賠償。")

if work_loss > 0:
    advice.append("✅ **質疑工作損失證明**：要求對方提出薪資證明、扣繳憑單；"
                  "對「永久勞動能力減損」主張嚴格鑑定。")

if drunk == "是":
    advice.append("⚠️ **酒駕為加重事由**：模型顯示酒駕案件平均慰撫金顯著高於未酒駕案件，難以透過訴訟降低。"
                  "建議優先考慮和解，避免進入判決程序。")

advice.append("💼 **積極和解**：在訴訟前或一審辯論終結前和解，可避免法官將「態度不佳」列入心證因素。")
advice.append("📄 **提出對自己有利的判決前例**：找出傷亡程度、損害金額相近但判賠較低的案件作為比照。")

for item in advice:
    st.markdown(f"- {item}")

st.markdown("---")
st.warning(
    "⚠️ **法律免責聲明**：以上建議基於統計模型分析，僅供參考。"
    "實際訴訟策略應諮詢律師，並依個案具體情況調整。"
)
