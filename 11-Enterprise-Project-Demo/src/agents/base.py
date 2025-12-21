"""Base agent class."""
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import structlog

from src.config import settings

logger = structlog.get_logger()


class BaseAgent:
    """Base agent with common functionality."""
    
    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt
        self.llm = ChatOpenAI(
            model=settings.default_model,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            openai_api_key=settings.openai_api_key,
        )
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])
    
    def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke agent with input."""
        try:
            messages = self.prompt_template.format_messages(**input_data)
            response = self.llm.invoke(messages)
            return {
                "agent": self.name,
                "output": response.content,
                "success": True,
            }
        except Exception as e:
            logger.error(f"Agent {self.name} failed", error=str(e))
            return {
                "agent": self.name,
                "output": f"Error: {str(e)}",
                "success": False,
            }

