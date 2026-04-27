"""
🎯 市场机会分析师
识别营销方案的市场空间、机会窗口、增长潜力
"""

from typing import Any, Dict, List
from app.agents.base_agent import MarketingBaseAgent


class OpportunityAnalyst(MarketingBaseAgent):
    """市场机会分析师"""

    def __init__(self):
        super().__init__("opportunity_analyst")

    def analyze(self, topic: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        分析营销机会

        输出格式：
        {
            "opportunity_score": 0-100,
            "opportunity_points": ["机会点1", "机会点2"],
            "window_period": "6个月",
            "target_segment": "一二线城市25-35岁女性",
            "market_size": "预估规模",
            "growth_potential": "高/中/低"
        }
        """
        agent = self.create_agent()
        prompt = self._build_prompt(topic, context or {})

        raw = agent.agent_executor.invoke({
            "input": prompt
        })["output"]

        return self.parse_output(raw, {"topic": topic, **context})

    def _build_prompt(self, topic: str, context: Dict[str, Any]) -> str:
        frameworks = self._agent_config.get("frameworks", [])
        return f"""你是【{self.role}】，负责分析以下营销方案的市场机会。

## 方案主题
{topic}

## 分析要求
1. 使用 {', '.join(frameworks)} 等框架进行系统分析
2. 给出0-100的机会评分（越高代表机会越大）
3. 识别3-5个核心机会点
4. 评估机会窗口的时间周期
5. 明确目标细分市场
6. 估算市场容量和增长潜力

## 输出格式（严格按此JSON格式返回）
```json
{{
    "opportunity_score": 75,
    "opportunity_points": [
        "市场空白：当前同类产品主要集中在一线城市，下沉市场空白明显",
        "趋势红利：XX赛道年增长率超30%，处于快速增长期",
        "政策利好：XX政策支持相关产业发展"
    ],
    "window_period": "6-12个月",
    "target_segment": "具体描述目标用户画像",
    "market_size": "预估市场容量（XX亿元）",
    "growth_potential": "高/中/低及理由"
}}
```

⚠️ 所有评分和估算必须有逻辑支撑，不能凭空编造数字。"""

    def parse_output(self, raw_output: str, context: Dict[str, Any]) -> Dict[str, Any]:
        import json, re
        # 尝试提取JSON
        match = re.search(r'\{[^{}]*"opportunity_score"[^{}]*\}', raw_output, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return {
            "opportunity_score": 50,
            "opportunity_points": [],
            "window_period": "未知",
            "target_segment": "待分析",
            "market_size": "待估算",
            "growth_potential": "待评估",
            "raw": raw_output,
            "agent": self.role
        }
