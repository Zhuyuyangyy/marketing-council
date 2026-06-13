"""
============================================
营销辩论团 Agent 基类
============================================
所有专业Agent继承此类，统一LLM注入和输出格式
============================================
"""

import json
import re
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
        # config.yaml is at project root (two levels up from app/)
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
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

    @staticmethod
    def extract_json(raw: str) -> Optional[Dict[str, Any]]:
        """
        Robust JSON extractor: tries multiple strategies to parse a JSON object
        from LLM-generated text that may contain markdown fences, prose, etc.

        Strategy 1: Try the entire string as JSON.
        Strategy 2: Find ```json ... ``` fenced blocks and parse contents.
        Strategy 3: Greedy brace-matching from the first '{' to find a valid object.
        """
        if not raw or not raw.strip():
            return None

        text = raw.strip()

        # Strategy 1: direct parse
        try:
            data = json.loads(text)
            if isinstance(data, dict):
                return data
        except (json.JSONDecodeError, ValueError):
            pass

        # Strategy 2: extract from markdown code fences
        fence_pattern = r'```(?:json)?\s*\n?([\s\S]*?)\n?\s*```'
        for match in re.finditer(fence_pattern, text):
            try:
                data = json.loads(match.group(1).strip())
                if isinstance(data, dict):
                    return data
            except (json.JSONDecodeError, ValueError):
                continue

        # Strategy 3: greedy brace matching from first '{'
        first_brace = text.find('{')
        if first_brace != -1:
            depth = 0
            in_string = False
            escape_next = False
            for i in range(first_brace, len(text)):
                ch = text[i]
                if escape_next:
                    escape_next = False
                    continue
                if ch == '\\' and in_string:
                    escape_next = True
                    continue
                if ch == '"' and not escape_next:
                    in_string = not in_string
                    continue
                if in_string:
                    continue
                if ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        candidate = text[first_brace:i + 1]
                        try:
                            data = json.loads(candidate)
                            if isinstance(data, dict):
                                return data
                        except (json.JSONDecodeError, ValueError):
                            # Move past this candidate and try next '{'
                            next_brace = text.find('{', first_brace + 1)
                            if next_brace != -1 and next_brace <= i:
                                first_brace = next_brace
                                depth = 0
                                in_string = False
                                escape_next = False
                            break

        return None
