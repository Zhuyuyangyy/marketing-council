"""
 风险控制官
评估营销方案的风险等级、威胁因素、潜在损失
"""

from typing import Any, Dict, List
import json, re
from app.agents.base_agent import MarketingBaseAgent


class RiskController(MarketingBaseAgent):
    """风险控制官"""

    def __init__(self):
        super().__init__("risk_controller")

    def analyze(self, topic: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        agent = self.create_agent()
        from crewai import Task
        task = Task(
            description=self._build_prompt(topic, context or {}),
            expected_output='JSON格式，包含 risk_score(0-100), risk_items(列表), risk_categories, potential_loss, mitigation_measures 字段',
        )
        raw = agent.execute_task(task)
        return self.parse_output(raw, {"topic": topic, **context})

    def _build_prompt(self, topic: str, context: Dict[str, Any]) -> str:
        risk_categories = self._agent_config.get("risk_categories", [])
        return f"""你是【{self.role}】，负责识别和评估以下营销方案的风险。

## 方案主题
{topic}

## 风险评估维度
从以下维度逐一分析：
{', '.join(risk_categories)}

## 分析要求
1. 识别每个维度的具体风险项
2. 评估每个风险的发生概率（高/中/低）
3. 评估一旦发生的impact（影响程度）
4. 综合给出0-100的风险评分（越高代表风险越大）
5. 识别最需要关注的高危风险项

## 输出格式（严格按此JSON格式返回）
```json
{{
    "risk_level": "高/中/低",
    "risk_score": 65,
    "risk_items": [
        {{
            "category": "政策合规",
            "severity": "高",
            "probability": "高",
            "impact": "可能导致推广计划被迫暂停",
            "mitigation": "建议提前进行合规审查"
        }}
    ],
    "top_risks": ["最需要关注的风险1", "风险2"],
    "recommendation": "如何在控制风险的同时推进方案"
}}
```

⚠️ 你是团队中的"乌鸦嘴"，不要回避坏消息，要把风险说透。"""

    def parse_output(self, raw_output: str, context: Dict[str, Any]) -> Dict[str, Any]:
        match = re.search(r'\[[\s\S]*?"category"[\s\S]*?\]', raw_output)
        risk_items = []
        if match:
            try:
                risk_items = json.loads(match.group())
            except json.JSONDecodeError:
                pass
        score_match = re.search(r'"risk_score"\s*:\s*(\d+)', raw_output)
        level_match = re.search(r'"risk_level"\s*:\s*"([^"]+)"', raw_output)
        return {
            "risk_level": level_match.group(1) if level_match else "中",
            "risk_score": int(score_match.group(1)) if score_match else 50,
            "risk_items": risk_items,
            "raw": raw_output,
            "agent": self.role
        }
