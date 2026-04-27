"""
============================================
LLM 工厂函数
支持讯飞星火Spark和Dify工作流自动切换
============================================
"""

import os
import yaml
from typing import Any, Optional

_DIFY_LLM_CACHE: Any = None


def _load_config() -> dict:
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "config.yaml"
    )
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _get_dify_llm_if_configured() -> Optional[Any]:
    """检测Dify配置，有则返回DifyWorkflowLLM"""
    global _DIFY_LLM_CACHE
    if _DIFY_LLM_CACHE is False:
        return None

    from dotenv import load_dotenv
    load_dotenv()

    cfg = _load_config()
    dify_cfg = cfg.get("llm", {}).get("dify", {})

    api_url = os.getenv("DIFY_API_URL") or dify_cfg.get("api_url", "")
    api_key = os.getenv("DIFY_API_KEY") or dify_cfg.get("api_key", "")

    if not (api_url and api_key):
        _DIFY_LLM_CACHE = False
        return None

    try:
        from app.core.llm_dify import DifyWorkflowLLM
        _DIFY_LLM_CACHE = DifyWorkflowLLM(
            api_url=api_url,
            api_key=api_key,
            workflow_id=dify_cfg.get("workflow_id", ""),
            expert_type="营销策略专家",
        )
        return _DIFY_LLM_CACHE
    except Exception as e:
        print(f"[WARN] Dify LLM init failed, fallback to Spark: {e}")
        _DIFY_LLM_CACHE = False
        return None


def get_crewai_llm(temperature: float = 0.7) -> Any:
    """
    获取CrewAI兼容LLM
    优先Dify，其次讯飞星火
    """
    # 1. 检查env中的Dify配置
    dify_llm = _get_dify_llm_if_configured()
    if dify_llm is not None:
        return dify_llm

    # 2. 检查config.yaml中的provider设置
    cfg = _load_config()
    if cfg.get("llm", {}).get("provider") == "dify":
        dify_llm = _get_dify_llm_if_configured()
        if dify_llm is not None:
            return dify_llm

    # 3. 默认使用讯飞星火Spark
    return _create_spark_llm(temperature)


def _create_spark_llm(temperature: float = 0.7) -> Any:
    """创建讯飞星火LLM"""
    from dotenv import load_dotenv
    load_dotenv()

    try:
        from app.core.llm_spark import SparkChatModel
        return SparkChatModel(
            spark_app_id=os.getenv("SPARK_APP_ID", ""),
            spark_api_key=os.getenv("SPARK_API_KEY", ""),
            spark_api_secret=os.getenv("SPARK_API_SECRET", ""),
            spark_model_version=os.getenv("SPARK_API_VERSION", "generalv3.5"),
            temperature=temperature,
            max_tokens=4096,
        )
    except Exception:
        # 如果Spark不可用，返回Mock LLM用于演示
        return _MockLLM(temperature=temperature)


class _MockLLM:
    """Mock LLM - 当没有真实API时提供演示"""
    def __init__(self, temperature: float = 0.7):
        self.temperature = temperature

    def _generate(self, messages, **kwargs):
        from langchain_core.outputs import ChatResult, ChatGeneration
        from langchain_core.messages import AIMessage
        content = "【演示模式】请配置真实的讯飞星火API Key或Dify服务以获取真实分析结果。"
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=content))])

    def _agenerate(self, messages, **kwargs):
        return self._generate(messages, **kwargs)

    def _stream(self, messages, **kwargs):
        from langchain_core.outputs import ChatGeneration
        from langchain_core.messages import AIMessage
        text = "【演示模式】请配置真实API..."
        for char in text:
            yield ChatGeneration(message=AIMessage(content=char))
