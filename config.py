
import os
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class LLMConfig:
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 1.0

@dataclass
class AppConfig:
    api_key: str = os.getenv("OPENAI_API_KEY")
    complexity_iterations: Dict[int, int] = None

    def __post_init__(self):
        if self.api_key is None:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        self.complexity_iterations = {
            1: 1,  # Basic
            2: 2,  # Simple
            3: 3,  # Moderate
            4: 4,  # Complex
            5: 5   # Highly nuanced and complex
        }

    def get_iterations(self, complexity: int) -> int:
        return self.complexity_iterations.get(complexity, 1)

config = AppConfig()
llm_config = LLMConfig()
