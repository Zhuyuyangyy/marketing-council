# marketing-council 评测报告
> 评测时间：2026-05-27 | 评测人：Alice
> 代码量：22个.py文件 | 后端端口：8009 | 前端：✅ | Benchmark：✅

---

## 整体完成度：**85%**

| 模块 | 完成度 | 说明 |
|------|--------|------|
| 6个专业Agent | 88% | base + 5个专业Agent，协作辩论 |
| 策略合成器 | 85% | strategy_synthesizer.py 完整 |
| 风险控制器 | 80% | risk_controller.py |
| SSE实时输出 | 75% | 需验证EventSourceResponse |
| 前端 | 85% | Vue3 + 实时Agent状态 |
| 测试/Benchmark | 70% | run_demo.py + spark测试脚本 |

---

## 核心模块评估

### ✅ 6个专业Agent（完整）
- `competitive_analyst.py` — 竞争分析
- `devil_advocate.py` — 反向论证
- `opportunity_analyst.py` — 机会分析
- `proscons_analyst.py` — 利弊分析
- `risk_controller.py` — 风险控制
- `strategy_synthesizer.py` — 策略综合

### ⚠️ 潜在问题
1. **SSE输出** — 需确认EventSourceResponse是否正确实现
2. **Spark集成** — 有 _test_spark.py 和 _test_spark_direct.py，说明Spark LLM调用有两条路径

---

## 问题清单

| 优先级 | 问题 | 说明 |
|--------|------|------|
| P1 | SSE可靠性 | 需压力测试验证实时输出稳定性 |
| P1 | Spark双路径 | 两套Spark调用代码需合并统一 |
| P2 | Benchmark缺失 | 只有demo脚本，无自动化CI测试 |

---

## 优化建议

1. **统一Spark调用路径** — 合并 _test_spark.py 和 _test_spark_direct.py
2. **添加SSE压力测试** — 多并发下的EventSourceResponse稳定性
3. **补Benchmark** — 标准化评测6个Agent协作决策质量

---

**综合评价：** 营销决策系统最完整的项目之一，6Agent架构清晰，辩论流程成型。Spark双路径和SSE稳定性是主要优化点。