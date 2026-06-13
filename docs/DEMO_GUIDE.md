# MarketingCouncil Demo Guide

> 营销决策辩论团 -- 演示指南

---

## 快速启动（30秒体验）

```bash
# 进入项目目录
cd marketing-council

# 直接运行 Mock 演示（零依赖，无需API Key）
python run_demo.py --mock

# Windows用户如果遇到编码问题，使用:
python -X utf8 run_demo.py --mock
```

---

## 演示模式一览

| 模式 | 命令 | 是否需要API | 说明 |
|------|------|------------|------|
| Mock演示 | `python run_demo.py --mock` | 否 | 纯本地模拟，5秒完成 |
| Agent列表 | `python run_demo.py --list-agents` | 否 | 查看6个Agent角色说明 |
| API测试 | `python run_demo.py --test-api` | 是 | 测试讯飞星火连接 |
| 交互式 | `python run_demo.py` | 否 | 自动进入Mock演示 |
| 自定义主题 | `python run_demo.py --mock --topic "..."` | 否 | 指定营销方案主题 |
| Web前端 | 启动后端后打开 `frontend/index.html` | 可选 | 完整可视化界面 |

---

## 演示场景详解

### 场景1：Mock模式快速演示（推荐首次体验）

**目的**：展示3轮辩论机制和最终决策输出，零配置零依赖。

```bash
python run_demo.py --mock
```

**输出内容**：
- 6个Agent角色介绍
- Round 1: 4位专家并行独立分析（机会、风险、优缺点、竞品）
- Round 2: 反向思考师交叉质疑
- Round 3: 策略综合官输出最终决策（STRONG-GO / CONDITIONAL-GO / HOLD / STOP）

### 场景2：自定义营销主题

```bash
python run_demo.py --mock --topic "小红书种草新品牌冷启动方案，预算50万，目标Z世代"
```

### 场景3：查看Agent团队配置

```bash
python run_demo.py --list-agents
```

输出6个Agent的角色定义、所属辩论轮次和职责描述。

### 场景4：API连接验证

```bash
# 先配置 .env 文件
cp .env.example .env
# 编辑 .env 填入 SPARK_APP_ID / SPARK_API_KEY / SPARK_API_SECRET

python run_demo.py --test-api
```

### 场景5：完整Web演示

```bash
# 终端1：启动后端
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8009

# 终端2：打开前端
# 浏览器访问 frontend/index.html
# 或直接访问 http://localhost:8009/docs 查看API文档
```

---

## 核心功能展示要点

### 1. 多Agent协作辩论

6个专业AI Agent模拟企业营销决策委员会：

| Agent | 轮次 | 职责 |
|-------|------|------|
| 机会分析师 | Round 1 | 市场空间、增长潜力、机会窗口 |
| 风险控制官 | Round 1 | 风险等级、威胁因素、潜在损失 |
| 优缺点分析师 | Round 1 | 量化利弊、净得分计算 |
| 竞品环境分析师 | Round 1 | 竞争格局、进入时机、壁垒分析 |
| 反向思考师 | Round 2 | 质疑假设、挑战结论、找盲区 |
| 策略综合官 | Round 3 | 汇总决策、置信度评估 |

### 2. 结构化决策输出

最终决策为四种标签之一：

- **STRONG-GO** -- 机会>70 且 风险<40，强烈推荐
- **CONDITIONAL-GO** -- 满足特定条件才推进
- **HOLD** -- 需要更多信息再决定
- **STOP** -- 风险过高或机会不足

### 3. 量化评分体系

- 机会评分: 0-100
- 风险评分: 0-100
- 置信度: 0-100%
- 决策阈值可在 `config.yaml` 中配置

---

## 文件结构

```
marketing-council/
├── run_demo.py              # 主演示脚本（Mock模式零依赖）
├── config.yaml              # 全局配置
├── requirements.txt         # Python依赖
├── start.bat / start.sh     # 一键启动脚本
├── docs/
│   └── DEMO_GUIDE.md        # 本文档
├── scripts/
│   └── run_demo.py          # 启动脚本（委托至根目录run_demo.py）
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI入口（端口8009）
│   │   ├── agents/          # 6个Agent实现
│   │   ├── core/            # 辩论编排器、LLM工厂
│   │   └── routers/         # API路由
│   └── app.py               # uvicorn入口
└── frontend/
    └── index.html            # Vue3单页前端
```

---

## 常见问题

**Q: 演示需要安装依赖吗？**
A: Mock模式不需要。`run_demo.py --mock` 使用内置Mock LLM，零依赖运行。

**Q: 如何切换到真实LLM？**
A: 在 `.env` 中配置讯飞星火API Key，或在 `config.yaml` 中切换 `llm.provider` 为 `dify`。

**Q: 前端如何连接后端？**
A: 前端默认连接 `http://localhost:8009`，确保后端已启动。也支持前端内置的演示模式（无需后端）。

**Q: 如何自定义Agent？**
A: 编辑 `config.yaml` 中的 `agents` 配置，或修改 `backend/app/agents/` 下的对应文件。
