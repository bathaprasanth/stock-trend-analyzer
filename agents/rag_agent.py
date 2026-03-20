from crewai import Agent

rag_agent = Agent(
    role="Stock Market RAG Chatbot",
    goal=(
        "Answer user questions using ALL context from previous agents. "
        "NEVER use brave_search or any web search tool. "
        "Use ONLY context already gathered by the crew."
    ),
    backstory=(
        "You are an intelligent financial assistant. You synthesize data "
        "from other agents to answer user questions clearly and accurately. "
        "You never use external tools or web search."
    ),
    tools=[],
    llm="groq/llama-3.3-70b-versatile",
    verbose=True,
    allow_delegation=False,
)
