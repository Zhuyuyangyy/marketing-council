"""
 策略综合官（决策主席）
汇总所有Agent观点，输出最终决策建议
"""

from typing import Any, Dict, List
import json, re
from app.agents.base_agent import MarketingBaseAgent


class StrategySynthesizer(MarketingBaseAgent):
    """策略综合官"""

    def __init__(self):
        super().__init__("strategy_synthesizer")

    def synthesize(self, topic: str, round1_outputs: Dict[str, Any], round2_outputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        综合所有Agent的分析结果，输出最终决策
        """
        agent = self.create_agent()
        from crewai import Task
        prompt = self._build_synthesis_prompt(topic, round1_outputs, round2_outputs or {})
        task = Task(
            description=prompt,
            expected_output='JSON格式，包含 decision(STRONG-GO/CONDITIONAL-GO/HOLD/STOP), confidence(0-100), decision_reason, conditions(列表), key_concerns(列表), next_steps(列表), summary 字段',
        )
        raw = agent.execute_task(task)
        return self.parse_output(raw, {"topic": topic})

    def _build_synthesis_prompt(self, topic: str, round1: Dict[str, Any], round2: Dict[str, Any]) -> str:
        # 汇总各Agent输出
        summaries = {}
        for key, output in round1.items():
            if isinstance(output, dict) and "raw" in output:
                summaries[key] = output.get("raw", str(output))[:500]
            elif isinstance(output, dict):
                summaries[key] = str(output)[:500]
            else:
                summaries[key] = str(output)[:500]

        summaries_text = "\n".join([f"## 【{k}】\n{summaries[k]}" for k in summaries])

        return f"""你是【{self.role}】，你是决策委员会主席，负责综合所有专家意见给出最终决策。

## 方案主题
{topic}

## 第一轮分析汇总
{summaries_text}

## 第二轮辩论结论（如果有）
{str(round2)[:800] if round2 else "（第二轮辩论尚未进行）"}

## 决策框架
| 决策 | 条件 |
|------|------|
| STRONG-GO | 机会>70 且 风险<40 |
| CONDITIONAL-GO | 机会>50 或 风险<60，需满足特定条件 |
| HOLD | 机会50左右，风险中等，需要更多信息 |
| STOP | 机会<40 或 风险>70 |

## 你的职责
1. 权衡所有专家的意见
2. 特别注意：风险控制官和反向思考师的质疑是否有道理
3. 给出明确的决策（STRONG-GO / CONDITIONAL-GO / HOLD / STOP）
4. 如果是 CONDITIONAL-GO，列出必须满足的条件
5. 给出0-100的置信度评分
6. 列出最多3个最关键的风险点
7. 给出具体的下一步行动建议

## 输出格式（严格按此JSON格式返回）
```json
{{
    "decision": "STRONG-GO / CONDITIONAL-GO / HOLD / STOP",
    "confidence": 78,
    "decision_reason": "决策理由（3-5句话）",
    "conditions": ["条件1（如果是CONDITIONAL-GO）", "条件2"],
    "key_concerns": ["最关键风险1", "最关键风险2", "最关键风险3"],
    "next_steps": ["具体行动1", "具体行动2", "具体行动3"],
    "summary": "2-3句话的决策总结"
}}
```

⚠️ 作为主席，你的决策必须清晰、可执行。不要说"见仁见智"这种废话。"""

    def parse_output(self, raw_output: str, context: Dict[str, Any]) -> Dict[str, Any]:
        decision_match = re.search(r'"decision"\s*:\s*"([^"]+)"', raw_output)
        confidence_match = re.search(r'"confidence"\s*:\s*(\d+)', raw_output)
        conditions_match = re.findall(r'"conditions"\s*:\s*\[([^\]]+)\]', raw_output)
        concerns_match = re.findall(r'"key_concerns"\s*:\s*\[([^\]]+)\]', raw_output)
        steps_match = re.findall(r'"next_steps"\s*:\s*\[([^\]]+)\]', raw_output)

        conditions = []
        if conditions_match:
            conditions = [c.strip().strip('"') for c in conditions_match[0].split(',') if c.strip()]

        return {
            "decision": decision_match.group(1) if decision_match else "HOLD",
            "confidence": int(confidence_match.group(1)) if confidence_match else 50,
            "conditions": conditions,
            "key_concerns": [],
            "next_steps": [],
            "summary": "",
            "raw": raw_output,
            "agent": self.role
        }
