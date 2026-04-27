"""
📊 竞品环境分析师
分析竞争格局、竞品动向、市场进入时机
"""

from typing import Any, Dict
import json, re
from app.agents.base_agent import MarketingBaseAgent


class CompetitiveAnalyst(MarketingBaseAgent):
    """竞品环境分析师"""

    def __init__(self):
        super().__init__("competitive_analyst")

    def analyze(self, topic: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        agent = self.create_agent()
        prompt = self._build_prompt(topic, context or {})
        raw = agent.agent_executor.invoke({"input": prompt})["output"]
        return self.parse_output(raw, {"topic": topic})

    def _build_prompt(self, topic: str, context: Dict[str, Any]) -> str:
        frameworks = self._agent_config.get("frameworks", [])
        return f"""你是【{self.role}】，负责分析以下营销方案的竞争环境和市场时机。

## 方案主题
{topic}

## 分析框架
使用 {', '.join(frameworks)} 进行系统分析

## 分析要求
1. 评估当前竞争格局（充分竞争/寡头/垄断/蓝海）
2. 识别主要竞品及其优劣势
3. 评估替代品威胁程度
4. 分析进入壁垒的高低
5. 判断当前是否是最佳进入时机
6. 如果竞品跟进，大概需要多长时间？

## 输出格式（严格按此JSON格式返回）
```json
{{
    "competitive_intensity": "激烈/中等/较低/蓝海",
    "competitive_intensity_score": 75,
    "competitive_threats": [
        {{"competitor": "竞品名称", "threat_level": "高", "key_advantage": "其优势", "our_response": "我们的应对"}}
    ],
    "substitute_threat": "高/中/低及理由",
    "barrier_analysis": {{
        "barrier_level": "高/中/低",
        "key_barriers": ["壁垒1", "壁垒2"],
        "how_to_break": "如何打破壁垒"
    }},
    "timing_assessment": {{
        "is_good_timing": true,
        "window_status": "窗口开放/窗口收窄/窗口关闭",
        "window_closing_time": "预计X个月后窗口关闭",
        "reason": "时机判断理由"
    }},
    "competitive_response_speed": "竞品跟进速度评估"
}}
```

⚠️ 时机判断要具体，不要说"时机不错"这种废话。"""

    def parse_output(self, raw_output: str, context: Dict[str, Any]) -> Dict[str, Any]:
        intensity_match = re.search(r'"competitive_intensity"\s*:\s*"([^"]+)"', raw_output)
        timing_match = re.search(r'"is_good_timing"\s*:\s*(true|false)', raw_output)
        window_match = re.search(r'"window_status"\s*:\s*"([^"]+)"', raw_output)
        return {
            "competitive_intensity": intensity_match.group(1) if intensity_match else "",
            "timing_assessment": {
                "is_good_timing": timing_match.group(1) == "true" if timing_match else None,
                "window_status": window_match.group(1) if window_match else ""
            },
            "competitive_threats": [],
            "barrier_analysis": {},
            "raw": raw_output,
            "agent": self.role
        }
