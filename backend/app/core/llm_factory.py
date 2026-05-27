"""
============================================
LLM 工厂函数 - 支持讯飞Spark/mock/Dify自动切换
============================================
优先级：Mock(无key) > Dify > Spark
"""

import os
import yaml
from typing import Any, Optional

_DIFY_LLM_CACHE: Any = None


def _load_config() -> dict:
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
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
    优先检查：无API Key → Mock模式
    其次检查：Dify配置
    最后回退到讯飞星火Spark
    """
    from dotenv import load_dotenv
    load_dotenv()

    spark_api_key = os.getenv("SPARK_API_KEY", "").strip()
    spark_api_secret = os.getenv("SPARK_API_SECRET", "").strip()

    # 无任何API Key时，返回MockLLM用于演示
    if not spark_api_key or not spark_api_secret:
        dify_llm = _get_dify_llm_if_configured()
        if dify_llm is not None:
            return dify_llm
        return _create_mock_llm(temperature=temperature)

    # 有Spark key，优先检查Dify
    cfg = _load_config()
    if cfg.get("llm", {}).get("provider") == "dify":
        dify_llm = _get_dify_llm_if_configured()
        if dify_llm is not None:
            return dify_llm

    # 使用讯飞星火Spark
    return _create_spark_llm(temperature)


def _create_spark_llm(temperature: float = 0.7) -> Any:
    """创建讯飞星火LLM（支持真实调用和mock fallback）"""
    try:
        from app.core.llm_spark_mock import SparkChatModel
        from app.core.llm_spark_crewai import CrewAISparkLLM
        from dotenv import load_dotenv
        load_dotenv()

        spark_model = SparkChatModel(
            spark_app_id=os.getenv("SPARK_APP_ID", ""),
            spark_api_key=os.getenv("SPARK_API_KEY", "").strip(),
            spark_api_secret=os.getenv("SPARK_API_SECRET", "").strip(),
            spark_model_version=os.getenv("SPARK_API_VERSION", "generalv3.5"),
            spark_domain=os.getenv("SPARK_API_VERSION", "generalv3.5"),
            temperature=temperature,
            max_tokens=4096,
        )
        return CrewAISparkLLM(spark_chat_model=spark_model)
    except Exception as e:
        print(f"[WARN] Spark LLM init failed, using MockLLM: {e}")
        return _create_mock_llm(temperature=temperature)


def _create_mock_llm(model_name: str = "mock-llm", temperature: float = 0.7):
    """
    工厂函数：创建CrewAI兼容的MockLLM
    用于演示模式，不调用任何外部API
    """
    from crewai.llms.base_llm import BaseLLM

    _MOCK_RESPONSE = (
        "【演示模式】当前未配置真实 LLM API Key，"
        "系统使用 MockLLM 返回占位分析结果。"
        "请配置 SPARK_API_KEY / SPARK_API_SECRET 或 DIFY_API_KEY 后获取真实多智能体辩论结果。"
    )

    class _MockLLMImpl(BaseLLM):
        """CrewAI兼容Mock LLM"""
        model: str = "mock-llm"
        temperature: float = 0.7

        def call(self, messages, **kwargs):
            return _MOCK_RESPONSE

        def __call__(self, messages=None, **kwargs):
            return _MOCK_RESPONSE

        def invoke(self, messages=None, **kwargs):
            return _MOCK_RESPONSE

        def _generate(self, messages=None, **kwargs):
            from langchain_core.outputs import ChatResult, ChatGeneration
            from langchain_core.messages import AIMessage
            return ChatResult(
                generations=[
                    ChatGeneration(message=AIMessage(content=_MOCK_RESPONSE))
                ]
            )

        def _agenerate(self, messages=None, **kwargs):
            return self._generate(messages, **kwargs)

        def _stream(self, messages=None, **kwargs):
            from langchain_core.outputs import ChatGeneration
            from langchain_core.messages import AIMessage
            for char in _MOCK_RESPONSE:
                yield ChatGeneration(message=AIMessage(content=char))
                import time
                time.sleep(0.005)

    return _MockLLMImpl(model=model_name, temperature=temperature)
