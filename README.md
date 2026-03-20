# 📈 Stock Trend Analyzer v2 — Multi-Agent RAG Chatbot

## 🚀 Quick Setup (5 steps)

### 1. Create & activate virtual environment
```bash
py -3.11 -m venv venv
venv\Scripts\activate        # Windows
```

### 2. Install dependencies
```bash
python -m pip install -r requirements.txt
```

### 3. Get FREE Groq API Key
- Go to https://console.groq.com/keys
- Sign up → Create API Key → Copy it

### 4. Create .env file
```bash
copy .env.example .env
```
Open `.env` and replace with your real key:
```
GROQ_API_KEY=gsk_your_real_key_here
```

### 5. Run the chatbot
```bash
python main.py
```

---

## 💬 How to Use

```
🤖 You: AAPL          ← Run full analysis
🤖 You: TSLA          ← Switch stock
🤖 You: Should I buy? ← Follow-up question
🤖 You: history       ← See past chats
🤖 You: clear         ← Reset memory
🤖 You: exit          ← Quit
```

---

## 🏗️ Project Structure

```
stock_analyzer_v2/
├── .env                  ← Your API key (create this!)
├── .env.example          ← Template
├── main.py               ← Run this
├── requirements.txt
├── agents/
│   ├── data_agent.py     ← Fetches price + news
│   ├── analysis_agent.py ← RSI, MACD, Bollinger, SMA
│   ├── signal_agent.py   ← BUY/SELL/HOLD signal
│   └── rag_agent.py      ← Chatbot synthesizer
├── tasks/
│   └── tasks.py          ← All 4 agent tasks
├── tools/
│   └── stock_tool.py     ← yfinance tools
└── rag/
    └── memory.py         ← Conversation memory
```

---

## 🤖 4-Agent Pipeline

```
[1] Data Agent     → price, history, news
        ↓
[2] Analysis Agent → RSI, MACD, Bollinger → BULLISH/BEARISH
        ↓
[3] Signal Agent   → BUY 💰 / SELL 🔴 / HOLD ⏸️
        ↓
[4] RAG Chatbot    → answers YOUR question with all context
```

---

## ⚠️ Rate Limit Note
Free Groq plan = 12,000 tokens/minute.
The app auto-retries if rate limit is hit (waits 40-80 seconds).
Wait 60 seconds between analyses to avoid rate limits.

---

## ⚠️ Disclaimer
For educational purposes only. Not financial advice.
