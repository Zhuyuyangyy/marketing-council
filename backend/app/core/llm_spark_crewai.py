"""CrewAI BaseLLM wrapper for SparkChatModel."""
from typing import Any, List, Optional
from crewai.llms.base_llm import BaseLLM
from langchain_core.outputs import ChatGeneration, ChatResult


class CrewAISparkLLM(BaseLLM):
    """
    CrewAI BaseLLM wrapper that delegates to SparkChatModel (LangChain BaseChatModel).
    The wrapped SparkChatModel is stored in self._spark and all CrewAI-required
    methods delegate to it.
    Inherits from BaseLLM to satisfy CrewAI Agent's isinstance(llm, BaseLLM) check
    in CrewAI 1.14.3's Pydantic validator.
    """

    model: str = "spark-model"
    temperature: float = 0.7

    def __init__(self, spark_chat_model: Any, **kwargs):
        # Set _spark BEFORE parent init (pydantic validator runs during super().__init__)
        object.__setattr__(self, '_spark', spark_chat_model)
        # Call parent init - must not pass model as kwarg to avoid pydantic conflict
        super().__init__(**kwargs)

    def _generate(
        self,
        messages: List[Any],
        stop: Optional[List[str]] = None,
        **kwargs,
    ) -> ChatResult:
        return self._spark._generate(messages, stop=stop, **kwargs)

    def _agenerate(
        self,
        messages: List[Any],
        stop: Optional[List[str]] = None,
        **kwargs,
    ):
        return self._spark._agenerate(messages, stop=stop, **kwargs)

    def _stream(
        self,
        messages: List[Any],
        stop: Optional[List[str]] = None,
        **kwargs,
    ):
        return self._spark._stream(messages, stop=stop, **kwargs)

    def call(self, messages: Any, **kwargs) -> str:
        result = self._spark._generate(messages, **kwargs)
        return result.generations[0].message.content

    def __call__(self, messages: Any = None, **kwargs) -> str:
        return self.call(messages, **kwargs)

    def invoke(self, messages: Any, **kwargs) -> str:
        return self.call(messages, **kwargs)