"""
頁面 1：AI 賠償預測系統
"""
import streamlit as st

from config import MODEL_MAE
from predictor import load_model, predict_amount

st.set_page_config(page_title="AI 賠償預測", page_icon="🔮", layout="wide")

st.title("🔮 AI 賠償預測")
st.caption("輸入案件條件，系統將即時預估精神慰撫金金額")

model, feature_names = load_model()
if model is None:
    st.error("找不到模型檔案，請先執行 `python train_model.py`")
    st.stop()

with st.form("predict_form"):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📝 案件基本特徵")
        injury = st.selectbox(
            "傷亡程度（最關鍵因素）",
            ["傷害", "重傷", "死亡"],
            help="傷害=一般輕傷｜重傷=肢體殘缺、失去機能｜死亡=被害人死亡",
        )
        drunk = st.radio("肇事者是否酒駕", ["否", "是"], horizontal=True)
        fault_ratio = st.slider(
            "原告與有過失比例 (%)",
            min_value=0, max_value=100, value=0, step=10,
            help="例如：被害人自己也有 30% 肇事責任，輸入 30",
        )

    with col2:
        st.subheader("💰 實質損害金額（元）")
        medical_fee = st.number_input("醫療費用", min_value=0, value=50000, step=10000)
        care_fee = st.number_input("看護費用", min_value=0, value=0, step=10000)
        work_loss = st.number_input("工作損失（勞動力減損）", min_value=0, value=0, step=10000)

    submitted = st.form_submit_button("🚀 進行 AI 預測", use_container_width=True, type="primary")

if submitted:
    with st.spinner("AI 模型運算中..."):
        pred = predict_amount(
            model, feature_names,
            injury=injury,
            drunk=(drunk == "是"),
            fault_ratio=fault_ratio,
            medical_fee=medical_fee,
            care_fee=care_fee,
            work_loss=work_loss,
        )

    st.success("✅ 預測完成！")

    st.markdown(
        f"""
        <div style="background-color:#f0f2f6;padding:24px;border-radius:12px;text-align:center;">
            <h3 style="color:#31333F;margin:0;">預估精神慰撫金</h3>
            <h1 style="color:#0068c9;font-size:52px;margin:8px 0;">NT$ {int(pred):,}</h1>
            <p style="color:#888;margin:0;">模型平均誤差 (MAE) 約 {MODEL_MAE:,} 元</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 信賴區間（粗略以 MAE 為範圍）
    low = max(int(pred - MODEL_MAE), 0)
    high = int(pred + MODEL_MAE)
    st.info(f"📊 **參考區間**：NT$ {low:,} ~ NT$ {high:,}（以 ±1 MAE 計算）")

    st.markdown("### 📌 解讀")
    st.markdown(
        f"""
        - 本案件條件為 **{injury}**、肇事者{'有' if drunk == '是' else '無'}酒駕、
          原告與有過失 **{fault_ratio}%**。
        - 模型預估法官可能判賠的精神慰撫金約為 **NT$ {int(pred):,}**。
        - 想了解如何降低此金額？請至 👉 **「2_減少賠償建議」** 頁面。
        """
    )
