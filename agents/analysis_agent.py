from crewai import Agent
from tools.stock_tool import get_technical_indicators

analysis_agent = Agent(
    role="Technical Analyst",
    goal=(
        "Compute and interpret RSI, MACD, Bollinger Bands, SMA20, SMA50 "
        "to identify the current market trend. "
        "ONLY use get_technical_indicators tool. "
        "NEVER use brave_search or any web search tool."
    ),
    backstory=(
        "You are a certified technical analyst with 15 years of experience. "
        "You ONLY use the get_technical_indicators tool. Never web search."
    ),
    tools=[get_technical_indicators],
    llm="groq/llama-3.3-70b-versatile",
    verbose=True,
    allow_delegation=False,
)
