from crewai import Task
from agents.data_agent    import data_agent
from agents.analysis_agent import analysis_agent
from agents.signal_agent  import signal_agent
from agents.rag_agent     import rag_agent


# ── Task 1: Fetch Data ────────────────────────────────────────────────────────
fetch_data_task = Task(
    description=(
        "Fetch the latest stock data for ticker: {ticker}.\n"
        "1. Call get_stock_data to get price, change, 30-day history.\n"
        "2. Call get_stock_news to get latest 5 headlines.\n"
        "Return structured JSON with all data.\n"
        "STRICT RULE: Use ONLY get_stock_data and get_stock_news. "
        "DO NOT use brave_search or any web search. No exceptions."
    ),
    expected_output=(
        "JSON with: ticker, latest_price, prev_price, change_pct, "
        "prices_30d, dates, headlines."
    ),
    agent=data_agent,
)


# ── Task 2: Technical Analysis ────────────────────────────────────────────────
analysis_task = Task(
    description=(
        "Calculate technical indicators for {ticker}:\n"
        "- RSI (oversold <30, overbought >70)\n"
        "- MACD vs signal line\n"
        "- Bollinger Bands position\n"
        "- SMA20 vs SMA50 (golden/death cross)\n"
        "Give verdict: BULLISH 📈 / BEARISH 📉 / NEUTRAL ➡️\n"
        "STRICT RULE: Use ONLY get_technical_indicators tool. "
        "DO NOT use brave_search or any web search. No exceptions."
    ),
    expected_output=(
        "Analysis report with all indicator readings and overall trend verdict."
    ),
    agent=analysis_agent,
    context=[fetch_data_task],
)


# ── Task 3: Trading Signal ────────────────────────────────────────────────────
signal_task = Task(
    description=(
        "Generate trading signal for {ticker}:\n"
        "1. Signal: BUY 💰 / SELL 🔴 / HOLD ⏸️\n"
        "2. Confidence: 0-100%\n"
        "3. Top 3 reasons\n"
        "4. Risk: LOW / MEDIUM / HIGH\n"
        "5. Price target (1-2 weeks)\n"
        "6. Stop-loss price\n"
        "STRICT RULE: Use ONLY context from previous agents. "
        "DO NOT use brave_search or any web search. No exceptions."
    ),
    expected_output=(
        "Signal report: BUY/SELL/HOLD, confidence %, 3 reasons, "
        "risk level, price target, stop-loss."
    ),
    agent=signal_agent,
    context=[fetch_data_task, analysis_task],
)


# ── Task 4: RAG Chatbot ───────────────────────────────────────────────────────
chatbot_task = Task(
    description=(
        "Answer this user question: '{user_question}' about {ticker}.\n"
        "Use ALL context from previous agents (price, indicators, signal, news).\n\n"
        "Format response as:\n"
        "📊 **Quick Summary** - 2 sentences\n"
        "🔍 **Detailed Answer** - full explanation with numbers\n"
        "💰 **Signal** - BUY/SELL/HOLD with confidence\n"
        "💡 **Key Takeaway** - one actionable insight\n"
        "⚠️ **Disclaimer** - investment disclaimer\n\n"
        "STRICT RULE: Use ONLY context from previous agents. "
        "DO NOT use brave_search or any web search. No exceptions."
    ),
    expected_output=(
        "Structured chatbot response with all 5 sections."
    ),
    agent=rag_agent,
    context=[fetch_data_task, analysis_task, signal_task],
)
