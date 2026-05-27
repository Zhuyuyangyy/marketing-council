"""
讯飞星火大模型 LLM 封装 - 支持 Mock 模式
支持真实的 Spark API 调用和完全 Mock 响应（无需 API Key）
"""

import os
import uuid
import httpx
import json
import time
import hashlib
import base64
import hmac
from typing import Any, Dict, List, Optional, Iterator, AsyncIterator
from urllib.parse import urlparse
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult


def _generate_auth_header(api_key: str, api_secret: str, url: str) -> tuple[str, str]:
    """Generate讯飞星火 HMAC-SHA256 认证头"""
    parsed = urlparse(url)
    host = parsed.netloc
    date = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())
    origin = f'host: {host}\ndate: {date}\nGET {parsed.path} HTTP/1.1'
    sig = hmac.new(api_secret.encode(), origin.encode(), digestmod=hashlib.sha256).digest()
    auth = base64.b64encode(
        f'api_key="{api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{base64.b64encode(sig).decode()}"'.encode()
    ).decode()
    return auth, host, date


class SparkChatModel(BaseChatModel):
    """
    讯飞星火大模型 LangChain 封装
    - 有 API Key 时调用真实讯飞星火 API
    - 无 API Key 时自动切换到 Mock 模式，返回预设响应
    """

    spark_app_id: str = ""
    spark_api_key: str = ""
    spark_api_secret: str = ""
    spark_model_version: str = "generalv3.5"
    spark_domain: str = "generalv3.5"
    temperature: float = 0.7
    max_tokens: int = 4096

    # 讯飞 API 地址
    spark_http_url: str = "https://spark-api-open.xf-yun.com/v1/chat/completions"

    class Config:
        arbitrary_types_allowed = True

    @property
    def _llm_type(self) -> str:
        return "spark-chat-model"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {"model": self.spark_domain, "temperature": self.temperature}

    @property
    def _is_mock(self) -> bool:
        """Check if we should use mock mode"""
        return not (self.spark_api_key and self.spark_api_secret)

    # ============================================================
    # Mock responses per agent role
    # ============================================================

    def _mock_response(self, messages: List[BaseMessage]) -> str:
        """Generate contextual mock response based on last user message"""
        last_content = ""
        for msg in reversed(messages):
            content = getattr(msg, "content", "") or str(msg)
            if content:
                last_content = content
                break

        # Default demo response
        return (
            "【演示模式】当前运行在 Mock LLM 模式。"
            "要获取真实 AI 分析结果，请配置 SPARK_API_KEY 和 SPARK_API_SECRET 环境变量。"
            f"\n\n您的输入: {last_content[:100]}..."
        )

    def _mock_stream(self, messages: List[BaseMessage]) -> Iterator[ChatGeneration]:
        """Mock streaming response"""
        response = self._mock_response(messages)
        for char in response:
            yield ChatGeneration(message=AIMessage(content=char))
            time.sleep(0.01)

    # ============================================================
    # Real API call
    # ============================================================

    def _call_spark_api(self, messages: List[BaseMessage]) -> ChatResult:
        """Call real 讯飞星火 API"""
        spark_messages = self._to_spark_format(messages)

        auth, host, date = _generate_auth_header(
            self.spark_api_key, self.spark_api_secret, self.spark_http_url
        )

        headers = {
            "Content-Type": "application/json",
            "Authorization": auth,
            "Host": host,
            "Date": date,
        }

        request_body = {
            "header": {"app_id": self.spark_app_id or "default", "uid": str(uuid.uuid4())[:8]},
            "parameter": {
                "chat": {
                    "domain": self.spark_domain,
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                }
            },
            "payload": {"message": {"text": spark_messages}},
        }

        with httpx.Client(timeout=60.0) as client:
            response = client.post(self.spark_http_url, json=request_body, headers=headers)
            response.raise_for_status()
            result = response.json()

            # Parse 讯飞 response format
            choices = result.get("payload", {}).get("choices", {}).get("text", [])
            if not choices:
                # Try alternate format
                choices = result.get("choices", [])
            content = choices[0]["content"] if choices else "No response"
            return ChatResult(generations=[ChatGeneration(message=AIMessage(content=content))])

    # ============================================================
    # LangChain required methods
    # ============================================================

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        if self._is_mock:
            return ChatResult(
                generations=[ChatGeneration(message=AIMessage(content=self._mock_response(messages)))]
            )
        try:
            return self._call_spark_api(messages)
        except Exception as e:
            # Fallback to mock on error
            return ChatResult(
                generations=[ChatGeneration(message=AIMessage(content=f"API Error: {e}"))]
            )

    async def _agenerate(self, messages, **kwargs):
        return self._generate(messages, **kwargs)

    def _stream(self, messages: List[BaseMessage], **kwargs) -> Iterator[ChatGeneration]:
        if self._is_mock:
            yield from self._mock_stream(messages)
            return

        # Real streaming (讯飞 has streaming support)
        try:
            for chunk in self._stream_spark(messages):
                yield chunk
        except Exception as e:
            yield ChatGeneration(message=AIMessage(content=f"Stream error: {e}"))

    def _stream_spark(self, messages: List[BaseMessage]) -> Iterator[ChatGeneration]:
        """Real streaming from 讯飞 API"""
        spark_messages = self._to_spark_format(messages)
        auth, host, date = _generate_auth_header(
            self.spark_api_key, self.spark_api_secret, self.spark_http_url
        )

        headers = {
            "Content-Type": "application/json",
            "Authorization": auth,
            "Host": host,
            "Date": date,
        }

        request_body = {
            "header": {"app_id": self.spark_app_id or "default", "uid": str(uuid.uuid4())[:8]},
            "parameter": {
                "chat": {
                    "domain": self.spark_domain,
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                    "stream": True,
                }
            },
            "payload": {"message": {"text": spark_messages}},
        }

        with httpx.Client(timeout=120.0) as client:
            with client.stream("POST", self.spark_http_url, json=request_body, headers=headers) as resp:
                for line in resp.iter_lines():
                    if not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        content = (
                            chunk.get("payload", {})
                            .get("choices", {})
                            .get("text", [{}])[0]
                            .get("content", "")
                        )
                        if content:
                            yield ChatGeneration(message=AIMessage(content=content))
                    except json.JSONDecodeError:
                        continue

    def _to_spark_format(self, messages: List[BaseMessage]) -> List[Dict[str, str]]:
        result = []
        for msg in messages:
            if hasattr(msg, "type"):
                role_map = {"system": "system", "human": "user", "ai": "assistant"}
                role = role_map.get(msg.type, "user")
            else:
                role = "user"
            content = getattr(msg, "content", "") or str(msg)
            result.append({"role": role, "content": content})
        return result


class MockSparkChatModel(SparkChatModel):
    """
    强制 Mock 模式的 Spark 模型
    明确用于演示/测试，不调用任何真实 API
    """

    def __init__(self, **kwargs):
        kwargs["spark_api_key"] = ""
        kwargs["spark_api_secret"] = ""
        super().__init__(**kwargs)

    @property
    def _is_mock(self) -> bool:
        return True
