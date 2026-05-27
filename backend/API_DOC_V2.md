# MarketingCouncil API V2 文档

> **版本**: 2.0.0  
> **基础路径**: `/api/v2`  
> **标签**: MarketingCouncil V2

---

## 概述

V2 API 提供增强的营销分析功能，包括辩论场景生成、情感分析、竞品情报、活动优化和品牌定位。

---

## 端点列表

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v2/debate/scenario` | 创建多Agent辩论场景 |
| POST | `/api/v2/sentiment/analyze` | 高级情感分析（含方面级提取） |
| POST | `/api/v2/competitor/intelligence` | 竞品情报分析 |
| POST | `/api/v2/campaign/optimize` | 营销活动优化 |
| POST | `/api/v2/brand/positioning` | 品牌定位与差异化分析 |

---

## 1. 创建辩论场景

### `POST /api/v2/debate/scenario`

创建一个多Agent辩论场景。

**请求体 (DebateScenarioRequest)**

| 字段 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `topic` | string | *必需* | 辩题/营销主题 |
| `num_agents` | int | 6 | Agent数量 (1-6) |
| `rounds` | int | 3 | 辩论轮数 |
| `debate_mode` | string | "standard" | 辩论模式: `standard` / `adversarial` / `consensus` |

**响应示例**

```json
{
  "topic": "新品上市定价策略",
  "num_agents": 6,
  "agents": [
    "opportunity_analyst",
    "risk_controller",
    "pros_cons_analyst",
    "devil_advocate",
    "competitor_analyst",
    "strategy_synthesist"
  ],
  "debate_mode": "standard",
  "rounds": [
    {
      "round": 1,
      "focus": "机会识别",
      "temperature": 0.72,
      "consensus_reached": null
    }
  ],
  "scenario_id": "debate-202605172055",
  "estimated_duration_minutes": 24
}
```

---

## 2. 情感分析

### `POST /api/v2/sentiment/analyze`

对文本进行情感分析，支持方面级提取。

**请求体 (SentimentAnalysisRequest)**

| 字段 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `texts` | List[string] | *必需* | 待分析文本列表 |
| `include_aspect` | bool | true | 是否包含方面级分析 |

**响应示例**

```json
{
  "document_count": 3,
  "average_sentiment": 0.245,
  "sentiment_distribution": {
    "positive": 2,
    "negative": 0,
    "neutral": 1
  },
  "detailed_results": [
    {
      "text": "产品质量很好，价格也合理...",
      "sentiment": 0.523,
      "emotion": "positive",
      "aspects": [
        {"aspect": "质量", "sentiment": 0.42, "confidence": 0.89},
        {"aspect": "价格", "sentiment": 0.31, "confidence": 0.72}
      ],
      "confidence": 0.85
    }
  ]
}
```

**情感分数说明**

| 范围 | 情感 |
|------|------|
| > 0.2 | positive |
| < -0.2 | negative |
| -0.2 ~ 0.2 | neutral |

---

## 3. 竞品情报

### `POST /api/v2/competitor/intelligence`

分析竞品SWOT和市场表现。

**请求体 (CompetitorAnalysisRequest)**

| 字段 | 类型 | 描述 |
|------|------|------|
| `industry` | string | 行业 |
| `product_category` | string | 产品类别 |
| `competitor_names` | List[string] | 竞品名称列表 |

**响应示例**

```json
{
  "industry": "快消品",
  "product_category": "饮料",
  "competitors": [
    {
      "name": "可口可乐",
      "estimated_market_share_pct": 35.2,
      "brand_sentiment": 0.42,
      "swot": {
        "strengths": ["品牌影响力", "渠道覆盖", "产品创新"],
        "weaknesses": ["成本高"],
        "opportunities": ["快消品增长", "政策支持"],
        "threats": ["新进入者", "替代品"]
      }
    }
  ],
  "market_sentiment": 0.31,
  "recommendation": "差异化竞争"
}
```

**竞争建议说明**

| 市场情感 | 建议 |
|----------|------|
| > 0.2 | 差异化竞争 |
| < -0.1 | 价格竞争 |
| 其他 | 品质竞争 |

---

## 4. 营销活动优化

### `POST /api/v2/campaign/optimize`

优化营销活动的预算分配和渠道策略。

**请求体 (CampaignOptimizerRequest)**

| 字段 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `campaign_type` | string | *必需* | 活动类型: `launch` / `retention` / `reactivation` |
| `target_audience` | string | *必需* | 目标受众描述 |
| `budget_level` | string | *必需* | 预算等级: `low` / `medium` / `high` |
| `channel_mix` | Dict[str, float] | null | 渠道配比（默认自动分配） |

**预算等级对应金额**

| 等级 | 预算 |
|------|------|
| low | ¥50,000 |
| medium | ¥200,000 |
| high | ¥1,000,000 |

**响应示例**

```json
{
  "campaign_type": "launch",
  "target_audience": "25-35岁都市白领",
  "budget_level": "medium",
  "total_budget": 200000,
  "channel_allocation": {
    "social": 60000.0,
    "search": 50000.0,
    "display": 40000.0,
    "affiliate": 30000.0,
    "email": 20000.0
  },
  "expected_roi": 3.85,
  "estimated_reach": 30000,
  "channel_recommendations": ["加大social投放", "加大search投放"]
}
```

---

## 5. 品牌定位

### `POST /api/v2/brand/positioning`

分析品牌定位和差异化策略。

**请求体 (BrandPositioningRequest)**

| 字段 | 类型 | 描述 |
|------|------|------|
| `brand_name` | string | 品牌名称 |
| `product_description` | string | 产品描述 |
| `target_segments` | List[string] | 目标细分市场 |
| `competitor_tags` | List[string] | 竞品标签（用于对比） |

**响应示例**

```json
{
  "brand_name": "元气森林",
  "product_description": "无糖气泡水",
  "differentiation_score": 0.72,
  "brand_strength_score": 0.85,
  "positioning": {
    "core_differentiator": "技术创新",
    "personality": "年轻活力",
    "voice": "轻松活泼"
  },
  "tag_cloud": ["无糖", "健康", "本土品牌", "年轻活力专属"],
  "recommendations": ["强化差异化特征", "深化目标人群连接", "持续品牌传播"]
}
```

**差异化评分说明**

| 评分 | 建议 |
|------|------|
| > 0.6 | 强化差异化特征、深化目标人群连接、持续品牌传播 |
| ≤ 0.6 | 寻找独特卖点、提升品牌认知度 |

---

## 错误处理

所有端点可能返回以下错误：

| 状态码 | 描述 |
|--------|------|
| 422 | 请求体验证失败 |
| 500 | 服务器内部错误 |

---

*文档生成时间: 2026-05-17*