"""
市场机会分析师
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
        from crewai import Task
        task = Task(
            description=self._build_prompt(topic, context or {}),
            expected_output='JSON格式，包含 opportunity_score(0-100), opportunity_points(列表), window_period, target_segment, market_size, growth_potential 字段',
        )
        raw = agent.execute_task(task)

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
        # 尝试从多行JSON中提取完整对象（支持嵌套结构）
        # 策略：找到 opportunity_score 所在行，向前后扩展找配对的大括号
        try:
            # 先尝试直接 parse 整个 raw_output
            try:
                data = json.loads(raw_output)
                if "opportunity_score" in data:
                    data["agent"] = self.role
                    return data
            except json.JSONDecodeError:
                pass

            # 尝试找到 JSON 块（从 { 到最后 }）
            start = raw_output.find('{"')
            if start == -1:
                start = raw_output.find('{')
            if start != -1:
                # 从找到的 { 开始，尝试增长式解析
                for end in range(len(raw_output), start, -1):
                    try:
                        candidate = raw_output[start:end]
                        data = json.loads(candidate)
                        if "opportunity_score" in data:
                            data["agent"] = self.role
                            return data
                    except json.JSONDecodeError:
                        continue
        except Exception:
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
