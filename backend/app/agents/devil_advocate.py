"""
 反向思考师
故意唱反调，质疑假设，找出方案中的漏洞和盲区
"""

from typing import Any, Dict
import json, re
from app.agents.base_agent import MarketingBaseAgent


class DevilAdvocate(MarketingBaseAgent):
    """反向思考师"""

    def __init__(self):
        super().__init__("devil_advocate")

    def analyze(self, topic: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        agent = self.create_agent()
        # 如果有其他Agent的结论，作为质疑素材
        other_outputs = context.get("other_agent_outputs", {}) if context else {}
        from crewai import Task
        task = Task(
            description=self._build_prompt(topic, other_outputs),
            expected_output='JSON格式，包含 challenges(列表), assumptions(列表), blind_spots(列表) 字段',
        )
        raw = agent.execute_task(task)
        return self.parse_output(raw, {"topic": topic})

    def _build_prompt(self, topic: str, other_outputs: Dict[str, Any]) -> str:
        angles = self._agent_config.get("questioning_angles", [])
        others_text = ""
        if other_outputs:
            others_text = "\n\n## 其他专家的分析结论（供你质疑）\n"
            for name, output in other_outputs.items():
                others_text += f"- 【{name}】：{str(output)[:300]}...\n"

        return f"""你是【{self.role}】，你专门负责唱反调，质疑显而易见结论中的漏洞。

## 方案主题
{topic}

## 质疑角度
从以下角度系统性质疑：
{', '.join(angles)}

{others_text}

## 分析要求
1. 找出方案中最脆弱的假设
2. 提出3-5个最难回答的反向质疑
3. 识别潜在的盲区（所有人都没注意到的风险）
4. 列出如果失败，最可能的原因
5. 有哪些问题是方案支持者无法回答的？

## 输出格式（严格按此JSON格式返回）
```json
{{
    "challenges": [
        {{"question": "质疑问题", "difficulty": "高", "implication": "如果成立会导致什么"}},
        {{"question": "质疑问题", "difficulty": "中", "implication": "影响程度"}}
    ],
    "weakest_assumption": "最脆弱的假设是什么",
    "blind_spots": ["盲区1", "盲区2"],
    "probable_failure_reason": "最可能的失败原因",
    "unanswerable_questions": ["无法回答的问题1", "无法回答的问题2"]
}}
```

⚠️ 你是"魔鬼代言人"，不要留情面，把最难听的问题问出来！"""

    def parse_output(self, raw_output: str, context: Dict[str, Any]) -> Dict[str, Any]:
        weakest_match = re.search(r'"weakest_assumption"\s*:\s*"([^"]+)"', raw_output)
        failure_match = re.search(r'"probable_failure_reason"\s*:\s*"([^"]+)"', raw_output)
        return {
            "challenges": [],
            "weakest_assumption": weakest_match.group(1) if weakest_match else "",
            "blind_spots": [],
            "probable_failure_reason": failure_match.group(1) if failure_match else "",
            "unanswerable_questions": [],
            "raw": raw_output,
            "agent": self.role
        }
