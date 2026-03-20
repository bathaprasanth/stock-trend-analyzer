from crewai import Agent

signal_agent = Agent(
    role="Trading Signal Generator",
    goal=(
        "Generate BUY 💰 / SELL 🔴 / HOLD ⏸️ signal with confidence score. "
        "Use ONLY context from previous agents. "
        "NEVER use brave_search or any web search tool."
    ),
    backstory=(
        "You are an algorithmic trading expert. You use ONLY the context "
        "passed from previous agents. You never use any external tools."
    ),
    tools=[],
    llm="groq/llama-3.3-70b-versatile",
    verbose=True,
    allow_delegation=False,
)
