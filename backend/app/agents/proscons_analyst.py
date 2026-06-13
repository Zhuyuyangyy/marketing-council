"""
 优缺点分析师
量化分析营销方案的正面和负面因素
"""

from typing import Any, Dict
import json, re
from app.agents.base_agent import MarketingBaseAgent


class ProsConsAnalyst(MarketingBaseAgent):
    """优缺点分析师"""

    def __init__(self):
        super().__init__("proscons_analyst")

    def analyze(self, topic: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        agent = self.create_agent()
        from crewai import Task
        task = Task(
            description=self._build_prompt(topic, context or {}),
            expected_output='JSON格式，包含 pros(列表), cons(列表), net_score(正数表示利大于弊), key_insight 字段',
        )
        raw = agent.execute_task(task)
        return self.parse_output(raw, {"topic": topic, **context})

    def _build_prompt(self, topic: str, context: Dict[str, Any]) -> str:
        return f"""你是【{self.role}】，负责结构化分析以下营销方案的利弊。

## 方案主题
{topic}

## 分析要求
1. 列出3-7个核心优点，每个优点说明依据和权重
2. 列出3-7个核心缺点，每个缺点说明严重程度和可补救性
3. 综合计算净得分（优点总分 - 缺点总分）
4. 给出明确的利弊权衡结论

## 输出格式（严格按此JSON格式返回）
```json
{{
    "pros": [
        {{"title": "优点标题", "weight": 8, "reason": "权重理由"}},
        {{"title": "优点标题", "weight": 6, "reason": "权重理由"}}
    ],
    "cons": [
        {{"title": "缺点标题", "severity": 7, "recoverable": true, "reason": "可补救性说明"}},
        {{"title": "缺点标题", "severity": 9, "recoverable": false, "reason": "不可补救"}}
    ],
    "net_score": 15,
    "net_verdict": "净得分为正，优势明显",
    "balanced_view": "客观的利弊总结"
}}
```

⚠️ 客观中立，不要夸大优点或缺点。"""

    def parse_output(self, raw_output: str, context: Dict[str, Any]) -> Dict[str, Any]:
        data = self.extract_json(raw_output)
        if data and ("pros" in data or "net_score" in data):
            data.setdefault("pros", [])
            data.setdefault("cons", [])
            data["raw"] = raw_output
            data["agent"] = self.role
            return data

        # Fallback: regex extraction
        net_match = re.search(r'"net_score"\s*:\s*(-?\d+)', raw_output)
        verdict_match = re.search(r'"net_verdict"\s*:\s*"([^"]+)"', raw_output)
        return {
            "pros": [],
            "cons": [],
            "net_score": int(net_match.group(1)) if net_match else 0,
            "net_verdict": verdict_match.group(1) if verdict_match else "",
            "raw": raw_output,
            "agent": self.role
        }
