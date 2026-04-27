"""
============================================
营销辩论团 Agent 基类
============================================
所有专业Agent继承此类，统一LLM注入和输出格式
============================================
"""

import yaml
from typing import Any, Dict, List, Optional
from crewai import Agent
from loguru import logger

from app.core.llm_factory import get_crewai_llm


class MarketingBaseAgent:
    """营销辩论团Agent基类"""

    def __init__(self, agent_key: str):
        self.agent_key = agent_key
        self.config = self._load_config()
        self._agent_config = self.config.get("agents", {}).get(agent_key, {})
        self._llm = get_crewai_llm(temperature=0.7)

    def _load_config(self) -> Dict[str, Any]:
        import os
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "config.yaml"
        )
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    @property
    def role(self) -> str:
        return self._agent_config.get("role", self.agent_key)

    @property
    def goal(self) -> str:
        return self._agent_config.get("goal", "")

    @property
    def backstory(self) -> str:
        return self._agent_config.get("backstory", "")

    def create_agent(self, tools: Optional[List[Any]] = None) -> Agent:
        """创建CrewAI Agent"""
        return Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            llm=self._llm,
            tools=tools or [],
            verbose=True,
            allow_delegation=False,
        )

    def build_prompt(self, context: Dict[str, Any]) -> str:
        """子类实现：构建分析提示词"""
        raise NotImplementedError

    def parse_output(self, raw_output: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """子类实现：解析结构化输出"""
        return {"raw": raw_output, "agent": self.role}
