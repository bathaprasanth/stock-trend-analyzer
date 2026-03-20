"""
Stock Trend Analyzer v2 — Streamlit Dashboard (Optimized)
===========================================================
- Full analysis runs 4 agents ONCE per ticker
- Follow-up questions use cached context (instant!)
- Run with: streamlit run dashboard.py
"""
import pkg_resources
import setuptools
import time
import os
import streamlit as st
import plotly.graph_objects as go
from dotenv import load_dotenv
load_dotenv()

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Stock Trend Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;700&display=swap');
    :root {
        --bg: #0a0e1a; --surface: #111827; --border: #1f2937;
        --accent: #00d4aa; --red: #ff4757; --yellow: #ffd32a;
        --text: #e5e7eb; --muted: #6b7280;
    }
    html, body, .stApp { background-color: var(--bg) !important; color: var(--text) !important; font-family: 'DM Sans', sans-serif; }
    section[data-testid="stSidebar"] { background-color: var(--surface) !important; border-right: 1px solid var(--border); }
    h1, h2, h3 { font-family: 'Space Mono', monospace !important; }
    h1 { color: var(--accent) !important; font-size: 1.6rem !important; }
    h2 { color: var(--text) !important; font-size: 1.1rem !important; }
    [data-testid="metric-container"] { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 16px !important; }
    [data-testid="metric-container"] label { color: var(--muted) !important; font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 0.1em; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] { color: var(--accent) !important; font-family: 'Space Mono', monospace !important; font-size: 1.4rem !important; }
    .stTextInput input { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 8px !important; color: var(--text) !important; font-family: 'Space Mono', monospace !important; }
    .stTextInput input:focus { border-color: var(--accent) !important; box-shadow: 0 0 0 2px rgba(0,212,170,0.2) !important; }
    .stButton button { background: var(--accent) !important; color: #0a0e1a !important; border: none !important; border-radius: 8px !important; font-family: 'Space Mono', monospace !important; font-weight: 700 !important; }
    .stButton button:hover { background: #00f0c0 !important; }
    .user-bubble { background: var(--border); border-radius: 12px 12px 2px 12px; padding: 10px 16px; margin: 8px 0; max-width: 80%; margin-left: auto; color: var(--text); font-size: 0.9rem; }
    .bot-bubble { background: var(--surface); border: 1px solid var(--border); border-left: 3px solid var(--accent); border-radius: 2px 12px 12px 12px; padding: 12px 16px; margin: 8px 0; max-width: 90%; color: var(--text); font-size: 0.9rem; line-height: 1.6; white-space: pre-wrap; }
    hr { border-color: var(--border) !important; }
    .stTabs [data-baseweb="tab-list"] { background: var(--surface); border-radius: 8px; gap: 4px; }
    .stTabs [data-baseweb="tab"] { color: var(--muted) !important; font-family: 'Space Mono', monospace !important; font-size: 0.8rem !important; }
    .stTabs [aria-selected="true"] { color: var(--accent) !important; background: var(--border) !important; border-radius: 6px; }
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg); }
    ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ── Helper Functions ──────────────────────────────────────────────────────────
def check_api_key():
    key = os.getenv("GROQ_API_KEY", "")
    return key and key != "gsk_your_new_key_here"


def run_full_crew(ticker: str, question: str) -> str:
    """Run all 4 agents - use only for full analysis."""
    from crewai import Crew, Process
    from agents.data_agent import data_agent
    from agents.analysis_agent import analysis_agent
    from agents.signal_agent import signal_agent
    from agents.rag_agent import rag_agent
    from tasks.tasks import fetch_data_task, analysis_task, signal_task, chatbot_task

    crew = Crew(
        agents=[data_agent, analysis_agent, signal_agent, rag_agent],
        tasks=[fetch_data_task, analysis_task, signal_task, chatbot_task],
        process=Process.sequential,
        verbose=False,
    )
    for attempt in range(3):
        try:
            result = crew.kickoff(inputs={
                "ticker": ticker.upper(),
                "user_question": question,
            })
            return str(result)
        except Exception as e:
            err = str(e).lower()
            if "rate_limit" in err:
                wait = 45 + attempt * 20
                st.warning(f"⏳ Rate limit hit. Waiting {wait}s... (attempt {attempt+1}/3)")
                time.sleep(wait)
            else:
                return f"❌ Error: {str(e)}"
    return "❌ Failed after 3 retries. Please wait 60s and try again."


def answer_from_context(question: str, context: str, ticker: str) -> str:
    """
    Answer follow-up questions using cached context — NO agent re-run!
    Uses Groq directly for instant response.
    """
    import groq
    client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = f"""You are a stock market RAG chatbot assistant.

Here is the full analysis context for {ticker}:
{context}

User question: {question}

Answer the question using ONLY the context above.
Be clear, concise and helpful. Include specific numbers from the context.
Format your response with:
📊 **Answer:** (direct answer)
📈 **Supporting Data:** (specific numbers/indicators)
💡 **Key Takeaway:** (one actionable insight)
⚠️ **Disclaimer:** Not financial advice."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {str(e)}"


def get_stock_data_direct(ticker: str):
    import yfinance as yf
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1mo")
    hist3 = stock.history(period="3mo")
    return hist, hist3


def compute_indicators(hist3):
    close = hist3["Close"]
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(14).mean()
    rsi = 100 - (100 / (1 + gain / loss))
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    rm = close.rolling(20).mean()
    rs = close.rolling(20).std()
    bb_upper = rm + 2 * rs
    bb_lower = rm - 2 * rs
    return rsi, macd, signal, bb_upper, bb_lower, rm


# ── Session State ─────────────────────────────────────────────────────────────
defaults = {
    "messages": [],
    "current_ticker": None,
    "analysis_done": False,
    "hist": None,
    "hist3": None,
    "analysis_context": "",   # ← stores full analysis for fast follow-ups
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("# 📈 Stock Analyzer")
    st.markdown("---")

    if not check_api_key():
        st.error("❌ GROQ_API_KEY not set!")
        st.markdown("""
        1. Go to [console.groq.com/keys](https://console.groq.com/keys)
        2. Create API Key
        3. Add to `.env`: `GROQ_API_KEY=gsk_...`
        4. Restart the app
        """)
        st.stop()
    else:
        st.success("✅ API Key Connected")

    st.markdown("---")

    ticker_input = st.text_input(
        "🔍 Enter Stock Ticker",
        placeholder="AAPL, TSLA, MSFT...",
        value=st.session_state.current_ticker or "",
    ).upper().strip()

    analyze_btn = st.button("🚀 Run Full Analysis", use_container_width=True)

    st.markdown("---")
    st.markdown("**Quick Select:**")
    cols = st.columns(3)
    quick = ["AAPL", "TSLA", "MSFT", "NVDA", "GOOGL", "AMZN"]
    for i, q in enumerate(quick):
        if cols[i % 3].button(q, key=f"q_{q}"):
            st.session_state.current_ticker = q
            st.rerun()

    st.markdown("---")
    if st.button("🧹 Clear History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.analysis_done = False
        st.session_state.analysis_context = ""
        st.rerun()

    # Show status
    if st.session_state.analysis_done:
        st.markdown("---")
        st.success(f"✅ {st.session_state.current_ticker} analyzed!")
        st.info("💬 Follow-up questions are **instant** — no waiting!")

    st.markdown("---")
    st.markdown("""
    <div style='color: #6b7280; font-size: 0.75rem;'>
    ⚠️ Educational use only.<br>Not financial advice.<br><br>
    Model: llama-3.3-70b-versatile<br>Data: Yahoo Finance
    </div>
    """, unsafe_allow_html=True)


# ── Main Area ─────────────────────────────────────────────────────────────────
st.markdown("# 📈 Stock Trend Analyzer")
st.markdown("*Multi-Agent AI — Trend Prediction | Buy/Sell Signal | RAG Chatbot*")
st.markdown("---")

# ── Handle Full Analysis ──────────────────────────────────────────────────────
if analyze_btn and ticker_input:
    st.session_state.current_ticker = ticker_input
    st.session_state.analysis_done = False
    st.session_state.analysis_context = ""

    with st.spinner(f"📡 Loading {ticker_input} market data..."):
        try:
            hist, hist3 = get_stock_data_direct(ticker_input)
            st.session_state.hist = hist
            st.session_state.hist3 = hist3
        except Exception as e:
            st.error(f"❌ Could not load data: {e}")
            st.stop()

    with st.spinner("🤖 Running 4 AI agents... (60 seconds, please wait ☕)"):
        question = f"Give me a full analysis of {ticker_input} including trend, signal, and news."
        answer = run_full_crew(ticker_input, question)

        # Cache the full analysis context for instant follow-ups
        st.session_state.analysis_context = answer
        st.session_state.messages.append({"role": "user", "content": f"📊 Analyze {ticker_input}"})
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.session_state.analysis_done = True
        st.rerun()

# ── Charts ────────────────────────────────────────────────────────────────────
if st.session_state.hist is not None:
    ticker = st.session_state.current_ticker
    hist = st.session_state.hist
    hist3 = st.session_state.hist3

    latest = round(float(hist["Close"].iloc[-1]), 2)
    prev = round(float(hist["Close"].iloc[-2]), 2)
    chg = round(((latest - prev) / prev) * 100, 2)

    rsi_s, macd_s, sig_s, bb_up, bb_lo, bb_mid = compute_indicators(hist3)
    rsi_val = round(float(rsi_s.iloc[-1]), 1)
    macd_val = round(float(macd_s.iloc[-1]), 3)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("💵 Price", f"${latest}", f"{chg:+.2f}%")
    c2.metric("📊 RSI", f"{rsi_val}",
              "Oversold 🟢" if rsi_val < 30 else "Overbought 🔴" if rsi_val > 70 else "Normal ⚪")
    c3.metric("📉 MACD", f"{macd_val}", "Bullish 📈" if macd_val > 0 else "Bearish 📉")
    c4.metric("🔼 BB Upper", f"${round(float(bb_up.iloc[-1]), 2)}")
    c5.metric("🔽 BB Lower", f"${round(float(bb_lo.iloc[-1]), 2)}")

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📈 Price Chart", "📊 RSI", "📉 MACD"])

    with tab1:
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=hist3.index, open=hist3["Open"], high=hist3["High"],
            low=hist3["Low"], close=hist3["Close"], name=ticker,
            increasing_line_color="#00d4aa", decreasing_line_color="#ff4757",
        ))
        fig.add_trace(go.Scatter(x=hist3.index, y=bb_up, name="BB Upper",
                                  line=dict(color="#ffd32a", width=1, dash="dot")))
        fig.add_trace(go.Scatter(x=hist3.index, y=bb_lo, name="BB Lower",
                                  line=dict(color="#ffd32a", width=1, dash="dot"),
                                  fill="tonexty", fillcolor="rgba(255,211,42,0.05)"))
        fig.add_trace(go.Scatter(x=hist3.index, y=bb_mid, name="SMA20",
                                  line=dict(color="#6b7280", width=1)))
        fig.update_layout(
            template="plotly_dark", paper_bgcolor="#0a0e1a", plot_bgcolor="#0a0e1a",
            height=400, margin=dict(l=0, r=0, t=30, b=0),
            legend=dict(orientation="h", y=1.05),
            xaxis_rangeslider_visible=False,
            title=f"{ticker} — Price + Bollinger Bands",
            title_font=dict(color="#00d4aa"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        rsi_clean = rsi_s.dropna()
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=hist3.index[-len(rsi_clean):], y=rsi_clean,
            marker_color=["#00d4aa" if v >= 50 else "#ff4757" for v in rsi_clean],
            name="RSI"
        ))
        fig2.add_hline(y=70, line_dash="dash", line_color="#ff4757", annotation_text="Overbought (70)")
        fig2.add_hline(y=30, line_dash="dash", line_color="#00d4aa", annotation_text="Oversold (30)")
        fig2.update_layout(
            template="plotly_dark", paper_bgcolor="#0a0e1a", plot_bgcolor="#0a0e1a",
            height=300, margin=dict(l=0, r=0, t=30, b=0),
            title=f"{ticker} — RSI (14)", title_font=dict(color="#00d4aa"),
        )
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        macd_clean = (macd_s - sig_s).dropna()
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            x=hist3.index[-len(macd_clean):], y=macd_clean,
            marker_color=["#00d4aa" if v >= 0 else "#ff4757" for v in macd_clean],
            name="Histogram"
        ))
        fig3.add_trace(go.Scatter(x=hist3.index, y=macd_s, name="MACD",
                                   line=dict(color="#00d4aa", width=2)))
        fig3.add_trace(go.Scatter(x=hist3.index, y=sig_s, name="Signal",
                                   line=dict(color="#ff4757", width=1, dash="dot")))
        fig3.update_layout(
            template="plotly_dark", paper_bgcolor="#0a0e1a", plot_bgcolor="#0a0e1a",
            height=300, margin=dict(l=0, r=0, t=30, b=0),
            title=f"{ticker} — MACD", title_font=dict(color="#00d4aa"),
        )
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")


# ── Chat Section ──────────────────────────────────────────────────────────────
st.markdown("## 🤖 RAG Chatbot")

if st.session_state.analysis_done:
    st.success("⚡ Follow-up questions are instant — answers use cached analysis context!")

# Display messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-bubble">👤 {msg["content"]}</div>',
                    unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-bubble">🤖 {msg["content"]}</div>',
                    unsafe_allow_html=True)

# Chat input
if st.session_state.current_ticker:
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        user_q = col1.text_input(
            "Ask anything:",
            placeholder=f"e.g. Should I buy {st.session_state.current_ticker}?",
            label_visibility="collapsed"
        )
        submitted = col2.form_submit_button("Send 💬")

    if submitted and user_q:
        st.session_state.messages.append({"role": "user", "content": user_q})

        if st.session_state.analysis_context:
            # ⚡ FAST PATH — use cached context, no agents needed!
            with st.spinner("⚡ Answering instantly from cached analysis..."):
                answer = answer_from_context(
                    user_q,
                    st.session_state.analysis_context,
                    st.session_state.current_ticker
                )
        else:
            # Fallback — run full agents if no cache
            with st.spinner("🤖 Running agents... (60 seconds)"):
                time.sleep(45)
                answer = run_full_crew(st.session_state.current_ticker, user_q)

        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()
else:
    st.info("👈 Enter a stock ticker in the sidebar and click **Run Full Analysis** to start!")
