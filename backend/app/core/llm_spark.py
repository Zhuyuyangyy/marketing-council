"""
讯飞星火大模型 LLM 封装（简化版，用于MarketingCouncil）
"""

import os
import uuid
import httpx
from typing import Any, Dict, List, Optional, Iterator
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult


class SparkChatModel(BaseChatModel):
    """讯飞星火大模型 LangChain 封装"""

    spark_app_id: str = ""
    spark_api_key: str = ""
    spark_api_secret: str = ""
    spark_model_version: str = "generalv3.5"
    temperature: float = 0.7
    max_tokens: int = 4096

    spark_http_url: str = "https://spark-api-open.xf-yun.com/v1/chat/completions"

    class Config:
        arbitrary_types_allowed = True

    @property
    def _llm_type(self) -> str:
        return "spark-chat-model"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {"model": self.spark_model_version, "temperature": self.temperature}

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        request_id = f"sync-{uuid.uuid4().hex[:8]}"
        spark_messages = self._to_spark_format(messages)

        # 检查是否已配置API
        if not self.spark_api_key or not self.spark_api_secret:
            return self._mock_generate(f"【演示模式】请配置 SPARK_API_KEY 和 SPARK_API_SECRET 环境变量。请求ID: {request_id}")

        auth_token = f"Bearer {self.spark_api_key}:{self.spark_api_secret}"
        headers = {"Content-Type": "application/json", "Authorization": auth_token}
        request_body = {
            "model": kwargs.get("model", self.spark_model_version),
            "messages": spark_messages,
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
        }

        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(self.spark_http_url, json=request_body, headers=headers)
                response.raise_for_status()
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                return ChatResult(generations=[ChatGeneration(message=AIMessage(content=content))])
        except Exception as e:
            return self._mock_generate(f"API调用失败: {str(e)}，请求ID: {request_id}")

    def _mock_generate(self, content: str) -> ChatResult:
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=content))])

    def _to_spark_format(self, messages: List[BaseMessage]) -> List[Dict[str, str]]:
        result = []
        for msg in messages:
            if hasattr(msg, "type"):
                role = {"system": "system", "human": "user", "ai": "assistant"}.get(msg.type, "user")
            else:
                role = "user"
            result.append({"role": role, "content": str(msg.content)})
        return result

    async def _agenerate(self, messages, **kwargs):
        return self._generate(messages, **kwargs)

    def _stream(self, messages, **kwargs):
        content = "【流式演示】流式输出需要配置真实的讯飞星火API。"
        for char in content:
            yield ChatGeneration(message=AIMessage(content=char))
