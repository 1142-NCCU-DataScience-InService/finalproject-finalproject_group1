"""
頁面 3：資料探索 (EDA)
"""
import pandas as pd
import plotly.express as px
import streamlit as st

from config import DATASET_CSV
from predictor import load_model

st.set_page_config(page_title="資料探索", page_icon="📊", layout="wide")
st.title("📊 資料探索與模型解釋")
st.caption("了解模型如何從 7,050 筆判決中學習")

if not DATASET_CSV.exists():
    st.error("找不到資料集")
    st.stop()


@st.cache_data
def load_dataset():
    return pd.read_csv(DATASET_CSV)


df = load_dataset()
model, feature_names = load_model()

# ====================================================
# 基本統計
# ====================================================
st.header("資料集摘要")
c1, c2, c3, c4 = st.columns(4)
c1.metric("總案件數", f"{len(df):,}")
c2.metric("平均慰撫金", f"NT$ {int(df['Mental_Damage'].mean()):,}")
c3.metric("中位數", f"NT$ {int(df['Mental_Damage'].median()):,}")
c4.metric("最高金額", f"NT$ {int(df['Mental_Damage'].max()):,}")

# ====================================================
# 分布圖
# ====================================================
st.markdown("---")
st.header("慰撫金分布")
col1, col2 = st.columns(2)

with col1:
    fig = px.histogram(
        df[df["Mental_Damage"] <= 3000000], x="Mental_Damage", nbins=50,
        title="精神慰撫金分布 (≤300萬)",
        labels={"Mental_Damage": "精神慰撫金 (元)"},
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    injury_stat = df.groupby("Injury")["Mental_Damage"].agg(["mean", "count"]).reset_index()
    injury_stat.columns = ["傷亡程度", "平均慰撫金", "案件數"]
    fig = px.bar(injury_stat, x="傷亡程度", y="平均慰撫金", text_auto=".2s",
                 color="案件數", title="不同傷亡程度的平均慰撫金")
    st.plotly_chart(fig, use_container_width=True)

# ====================================================
# 特徵重要性
# ====================================================
st.markdown("---")
st.header("模型特徵重要性")

if model is not None:
    imp = pd.DataFrame({
        "特徵": feature_names,
        "重要性": model.feature_importances_,
    }).sort_values("重要性", ascending=False).head(15)

    fig = px.bar(imp, x="重要性", y="特徵", orientation="h",
                 title="Top 15 影響法官判決的因素",
                 text=imp["重要性"].apply(lambda x: f"{x*100:.1f}%"))
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=500)
    st.plotly_chart(fig, use_container_width=True)

    st.info(
        "💡 **解讀**：模型發現「看護費 / 醫療費 / 工作損失」等實質損害金額是法官心證的主要依據。"
        "實質損害越大 → 推定被害人精神痛苦越深 → 慰撫金越高。"
    )

# ====================================================
# 相關性
# ====================================================
st.markdown("---")
st.header("特徵與慰撫金的關聯")

numeric_cols = ["Medical_Fee", "Care_Fee", "Work_Loss", "Fault_Ratio", "Injury_Level", "Drunk"]
corr = df[numeric_cols + ["Mental_Damage"]].corr()["Mental_Damage"].drop("Mental_Damage").sort_values()

fig = px.bar(
    x=corr.values, y=corr.index, orientation="h",
    title="各特徵與慰撫金的 Pearson 相關係數",
    labels={"x": "相關係數", "y": "特徵"},
)
st.plotly_chart(fig, use_container_width=True)
