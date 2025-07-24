import streamlit as st, asyncio, nest_asyncio
from agent import StockSentimentAgent

nest_asyncio.apply()   # Streamlit + asyncio

st.set_page_config(page_title="Stock Sentiment", layout="wide")
st.title("📈 Stock Sentiment Agent")

symbol = st.text_input("Symbol", "AAPL").upper()
run_btn = st.button("Analyze")

if "agent" not in st.session_state:
    st.session_state.agent = StockSentimentAgent()
    asyncio.run(st.session_state.agent.start())

if run_btn:
    with st.spinner("Collecting & analyzing…"):
        asyncio.run(st.session_state.agent.collect(symbol))
    st.success("Done!")

score_data = asyncio.run(st.session_state.agent.db.get_latest(symbol))
if score_data:
    s, lbl, conf = score_data
    st.metric("Sentiment Score", f"{s:.2f}")
    st.write("Label:", lbl, "Confidence:", conf)