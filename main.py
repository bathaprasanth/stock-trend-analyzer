"""
Stock Trend Analyzer v2 — Multi-Agent RAG Chatbot
===================================================
✅ 4 Agents: Data → Analysis → Signal → RAG Chatbot
✅ Auto-retry on rate limit (waits & retries 3x)
✅ Conversation memory
✅ Model: groq/llama-3.3-70b-versatile
"""

import time
import os
from dotenv import load_dotenv
load_dotenv()

from crewai import Crew, Process
from agents.data_agent     import data_agent
from agents.analysis_agent import analysis_agent
from agents.signal_agent   import signal_agent
from agents.rag_agent      import rag_agent
from tasks.tasks import (
    fetch_data_task,
    analysis_task,
    signal_task,
    chatbot_task,
)
from rag.memory import memory

BANNER = """
╔══════════════════════════════════════════════════════════╗
║     📈  Stock Trend Analyzer v2  —  Multi-Agent AI      ║
║   Trend Prediction | Buy/Sell Signal | RAG Chatbot      ║
╚══════════════════════════════════════════════════════════╝
Commands:
  • Type a ticker  (e.g. AAPL, TSLA, MSFT) → full analysis
  • Ask a question (e.g. "Should I buy?")  → chatbot answer
  • history  → show conversation history
  • clear    → clear memory
  • exit     → quit
"""


def run_full_analysis(ticker: str, user_question: str) -> str:
    """Run all 4 agents with auto-retry on rate limit."""

    crew = Crew(
        agents=[data_agent, analysis_agent, signal_agent, rag_agent],
        tasks=[fetch_data_task, analysis_task, signal_task, chatbot_task],
        process=Process.sequential,
        verbose=True,
    )

    for attempt in range(3):
        try:
            result = crew.kickoff(inputs={
                "ticker":        ticker.upper(),
                "user_question": user_question,
            })
            return str(result)

        except Exception as e:
            err = str(e).lower()
            if "rate_limit" in err:
                wait = 40 + (attempt * 20)   # 40s → 60s → 80s
                print(f"\n⏳ Rate limit hit. Auto-retrying in {wait}s "
                      f"(attempt {attempt + 1}/3)...")
                time.sleep(wait)
            else:
                raise e

    return (
        "❌ Failed after 3 retries due to rate limits.\n"
        "💡 Wait 60 seconds then try again."
    )


def main():
    # Verify API key on startup
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "gsk_your_new_key_here":
        print("❌ ERROR: GROQ_API_KEY not set in .env file!")
        print("👉 Get your free key at: https://console.groq.com/keys")
        print("👉 Then add to .env: GROQ_API_KEY=gsk_your_key_here")
        return

    print(BANNER)
    current_ticker = None

    while True:
        try:
            user_input = input("\n🤖 You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Goodbye!")
            break

        if not user_input:
            continue

        # ── Commands ──────────────────────────────────────
        if user_input.lower() == "exit":
            print("👋 Goodbye!")
            break

        if user_input.lower() == "clear":
            memory.clear()
            current_ticker = None
            print("🧹 Memory cleared.")
            continue

        if user_input.lower() == "history":
            print("\n📜 Conversation History:")
            print(memory.get_history_text())
            continue

        # ── Detect ticker (all caps, ≤5 letters) ──────────
        stripped = user_input.strip().upper()
        is_ticker = (
            stripped == stripped and
            len(stripped) <= 5 and
            stripped.isalpha()
        )

        if is_ticker:
            current_ticker = stripped
            question = f"Give me a full analysis of {current_ticker} including trend, signal, and news."
            print(f"\n🔍 Running full analysis for {current_ticker}...")
        else:
            if not current_ticker:
                print("⚠️  Please enter a stock ticker first (e.g. AAPL, TSLA, MSFT)")
                continue
            question = user_input
            print(f"\n💬 Answering your question about {current_ticker}...")

        print("⏳ Agents working...\n")

        try:
            answer = run_full_analysis(current_ticker, question)
            memory.add_exchange(current_ticker, question, answer)

            print(f"\n{'═' * 62}")
            print(f"📊 Assistant ({current_ticker}):")
            print(f"{'═' * 62}")
            print(answer)
            print(f"{'═' * 62}\n")

        except Exception as e:
            print(f"❌ Error: {e}")
            print("💡 Check your .env file — GROQ_API_KEY must be set correctly.")


if __name__ == "__main__":
    main()
