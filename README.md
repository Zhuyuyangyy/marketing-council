# 🏛️ MarketingCouncil - 营销决策辩论团

**多Agent营销方案风险评估与可能性分析系统**

> 6个专业AI Agent · 3轮结构化辩论 · 实时流式输出

---

## 核心特性

- **🎯 6专业Agent团队**：机会分析师、风险控制官、优缺点分析师、反向思考师、竞品环境分析师、策略综合官
- **🔄 3轮辩论机制**：独立分析 → 交叉质疑 → 策略收敛
- **📊 量化评分**：机会/风险数值化 (0-100)，置信度评估
- **⚡ 流式SSE输出**：实时看到每个Agent的思考过程
- **🔀 框架无关**：支持讯飞星火Spark / Dify工作流 / OpenAI

---

## 项目结构

```
marketing-council/
├── config.yaml              # 全局配置（Agent定义、LLM、决策参数）
├── requirements.txt
├── start.bat / start.sh    # 一键启动
├── backend/
│   ├── app/
│   │   ├── main.py         # FastAPI 入口（端口8009）
│   │   ├── agents/         # 6个专业Agent
│   │   │   ├── opportunity_analyst.py   # 🎯 市场机会分析师
│   │   │   ├── risk_controller.py       # ⚠️ 风险控制官
│   │   │   ├── proscons_analyst.py       # ⚖️ 优缺点分析师
│   │   │   ├── devil_advocate.py         # 😈 反向思考师
│   │   │   ├── competitive_analyst.py    # 📊 竞品环境分析师
│   │   │   └── strategy_synthesizer.py  # 🏛️ 策略综合官
│   │   ├── core/
│   │   │   ├── debate_orchestrator.py    # 多轮辩论编排器
│   │   │   ├── llm_factory.py            # LLM工厂（Spark/Dify自动切换）
│   │   │   └── llm_spark.py              # 讯飞星火封装
│   │   └── routers/
│   │       └── debate.py                 # API路由
│   └── app.py                            # uvicorn入口
└── frontend/
    └── index.html                        # Vue3 单页前端
```

---

## 快速启动

### 1. 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置API Key（可选）
```bash
# 讯飞星火（默认）
cp .env.example .env
# 填入 SPARK_APP_ID / SPARK_API_KEY / SPARK_API_SECRET

# 或 Dify 工作流
# 在 config.yaml 中设置 llm.provider: "dify"
```

### 3. 启动
```bash
# 后端（端口8009）
python -m uvicorn app.main:app --host 0.0.0.0 --port 8009

# 前端（直接打开）
# 浏览器打开 frontend/index.html
```

---

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 服务信息 |
| GET | `/health` | 健康检查 |
| POST | `/api/v1/debate` | 发起辩论（同步，返回完整结果）|
| POST | `/api/v1/debate/stream` | 发起辩论（流式SSE）|
| GET | `/api/v1/debate/demo` | 演示模式（不调用真实LLM）|
| GET | `/api/v1/debate/agents` | Agent角色说明 |

---

## 辩论流程

```
用户输入营销方案
      ↓
━━━━━━━━━━━━━━━━━━━━━━━━━
  Round 1：并行5Agent独立分析
━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 机会分析师   → 市场空间/机会窗口/增长潜力
⚠️ 风险控制官   → 风险等级/威胁因素/潜在损失
⚖️ 优缺点分析师 → 量化利弊/净得分/权衡结论
📊 竞品环境分析师 → 竞争格局/进入时机/壁垒分析
      ↓
━━━━━━━━━━━━━━━━━━━━━━━━━
  Round 2：交叉辩论
━━━━━━━━━━━━━━━━━━━━━━━━━
😈 反向思考师   → 质疑假设/挑战结论/找出盲区
      ↓
━━━━━━━━━━━━━━━━━━━━━━━━━
  Round 3：策略综合
━━━━━━━━━━━━━━━━━━━━━━━━━
🏛️ 策略综合官   → STRONG-GO / CONDITIONAL-GO / HOLD / STOP
                 + 置信度 + 条件 + 下一步行动
```

---

## 决策标签

| 决策 | 条件 | 颜色 |
|------|------|------|
| **STRONG-GO** | 机会>70 且 风险<40 | 🟢 绿 |
| **CONDITIONAL-GO** | 满足特定条件才推进 | 🟡 黄 |
| **HOLD** | 需要更多信息再决定 | 🔵 蓝 |
| **STOP** | 风险过高或机会不足 | 🔴 红 |

---

## 前端界面

打开 `frontend/index.html` 即可使用，支持：
- 📋 演示模式（快速预览，无需API Key）
- 🚀 实时辩论（调用后端API）
- 🎨 深色专业主题
- 📊 6 Agent卡片实时状态

---

## 技术栈

- **后端**：FastAPI + CrewAI + LangChain
- **LLM**：讯飞星火 / Dify / OpenAI（可配置）
- **前端**：Vue3 + Axios（单HTML文件，无构建）
- **协议**：REST + SSE流式

---

## 配置说明

### config.yaml 关键配置

```yaml
llm:
  provider: "spark"  # spark | dify

  # Dify配置（provider=dify时生效）
  dify:
    enabled: true
    api_url: "http://localhost/v1"
    api_key: "your-dify-api-key"

decision:
  opportunity_threshold: 60   # 机会评分阈值
  risk_tolerance: 60          # 风险可接受上限
  confidence_threshold: 50     # 置信度阈值
```

---

⚠️ **免责声明**：本系统由AI多Agent驱动，输出仅供参考，不构成专业投资或运营建议。
