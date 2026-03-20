from collections import deque
from typing import Dict


class ConversationMemory:
    def __init__(self, max_history: int = 10):
        self.history: deque = deque(maxlen=max_history)
        self.stock_context: Dict = {}

    def add_exchange(self, ticker: str, question: str, answer: str):
        self.history.append({
            "ticker":   ticker,
            "question": question,
            "answer":   answer,
        })

    def get_history_text(self) -> str:
        if not self.history:
            return "No previous conversation."
        lines = []
        for i, ex in enumerate(self.history, 1):
            lines.append(f"[{i}] [{ex['ticker']}] You: {ex['question']}")
            lines.append(f"      Bot: {ex['answer'][:150]}...")
        return "\n".join(lines)

    def clear(self):
        self.history.clear()
        self.stock_context.clear()


memory = ConversationMemory(max_history=10)
