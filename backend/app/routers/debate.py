"""
============================================
营销辩论 API 路由
POST /api/v1/debate - 发起辩论（同步）
POST /api/v1/debate/stream - 发起辩论（流式SSE）
GET  /api/v1/debate/demo - 演示模式快速测试
============================================
"""

import asyncio
import json
import yaml
from datetime import datetime
from typing import Any, AsyncIterator, Dict, List, Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.core.debate_orchestrator import DebateOrchestrator


router = APIRouter(prefix="/api/v1/debate", tags=["辩论"])


# ============================================================
# Request/Response 模型
# ============================================================

class DebateRequest(BaseModel):
    topic: str = Field(..., min_length=5, max_length=500, description="营销方案/问题描述")
    stream: bool = Field(default=True, description="是否使用流式输出")
    include_round2: bool = Field(default=True, description="是否包含第2轮交叉辩论")


class AgentResult(BaseModel):
    agent: str
    role: str
    output: Dict[str, Any]


class FinalDecision(BaseModel):
    decision: str  # STRONG-GO / CONDITIONAL-GO / HOLD / STOP
    confidence: int
    conditions: list
    key_concerns: list
    next_steps: list
    summary: str


class DebateResponse(BaseModel):
    session_id: str
    topic: str
    created_at: str
    round1: Dict[str, Any]
    round2: Dict[str, Any]
    final_decision: Dict[str, Any]
    total_time_seconds: float
    disclaimer: str


# ============================================================
# Helper: 获取免责声明
# ============================================================

def _get_disclaimer() -> str:
    try:
        cfg = yaml.safe_load(open(Path(__file__).parent.parent.parent.parent / "config.yaml", "r"))
        return cfg.get("anti_hallucination", {}).get(
            "disclaimer",
            "⚠️ 本分析由AI生成，仅供决策参考。"
        )
    except Exception:
        return "⚠️ 本分析由AI生成，仅供决策参考，不构成专业建议。"


# ============================================================
# API 端点
# ============================================================

@router.post("", response_model=DebateResponse)
async def create_debate(request: DebateRequest):
    """
    发起营销方案辩论（同步版本）
    返回完整的三轮辩论结果
    """
    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="topic不能为空")

    orchestrator = DebateOrchestrator()
    result = await orchestrator.run_debate(request.topic)

    return DebateResponse(
        session_id=result["session_id"],
        topic=result["topic"],
        created_at=datetime.now().isoformat(),
        round1=result["round1"],
        round2=result["round2"],
        final_decision=result["final_decision"],
        total_time_seconds=result["total_time_seconds"],
        disclaimer=_get_disclaimer(),
    )


@router.post("/stream")
async def create_debate_stream(request: DebateRequest):
    """
    发起营销方案辩论（流式SSE版本）
    实时推送每个Agent的分析进度
    """
    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="topic不能为空")

    orchestrator = DebateOrchestrator()

    async def event_generator() -> AsyncIterator[str]:
        try:
            async for event in orchestrator.run_debate_stream(request.topic):
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.05)  # 避免过快
        except Exception as e:
            yield f"data: {json.dumps({'event': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"
        finally:
            yield f"data: {json.dumps({'event': 'done'}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.get("/demo")
async def demo_debate():
    """
    演示模式：不调用真实LLM，返回预设的演示结果
    用于快速测试前端界面
    """
    demo_result = {
        "session_id": "demo-session-001",
        "topic": "抖音电商美妆新品推广方案",
        "round1": {
            "opportunity_analyst": {
                "opportunity_score": 78,
                "opportunity_points": [
                    "美妆细分市场年增长率23%，窗口期约6个月",
                    "抖音日活8亿，流量红利仍在",
                    "KOC种草策略ROI预期3.2x"
                ],
                "window_period": "6-12个月",
                "target_segment": "一二线城市18-30岁女性",
                "market_size": "约200亿元",
                "growth_potential": "高",
                "agent": "市场机会分析师"
            },
            "risk_controller": {
                "risk_level": "中等",
                "risk_score": 52,
                "risk_items": [
                    {"category": "政策合规", "severity": "高", "probability": "中", "impact": "广告法功效宣称限制"},
                    {"category": "资金财务", "severity": "中", "probability": "中", "impact": "冷启动流量成本超预期"}
                ],
                "agent": "风险控制官"
            },
            "proscons_analyst": {
                "pros": [
                    {"title": "流量红利明显", "weight": 8},
                    {"title": "目标用户活跃度高", "weight": 7},
                    {"title": "种草+转化闭环完整", "weight": 8}
                ],
                "cons": [
                    {"title": "竞争激烈获客成本高", "severity": 7},
                    {"title": "品牌认知度低初期转化难", "severity": 6}
                ],
                "net_score": 15,
                "net_verdict": "优势明显",
                "agent": "优缺点分析师"
            },
            "competitive_analyst": {
                "competitive_intensity": "激烈",
                "timing_assessment": {
                    "is_good_timing": True,
                    "window_status": "窗口开放",
                    "window_closing_time": "约4个月"
                },
                "agent": "竞品环境分析师"
            },
            "devil_advocate": {
                "challenges": [
                    {"question": "如果达人翻车怎么办？", "difficulty": "高"},
                    {"question": "供应链能否支撑爆款峰值？", "difficulty": "高"}
                ],
                "weakest_assumption": "GMV增长假设过于乐观",
                "agent": "反向思考师"
            }
        },
        "round2": {
            "devil_advocate": {
                "challenges": [
                    {"question": "竞品已提前2个月布局，我们的差异化在哪里？", "difficulty": "高"},
                    {"question": "如果用户兴趣转移，现有投入是否成为沉没成本？", "difficulty": "中"}
                ],
                "weakest_assumption": "市场增长假设缺乏数据支撑",
                "probable_failure_reason": "获客成本高于预期导致ROI为负",
                "agent": "反向思考师"
            }
        },
        "final_decision": {
            "decision": "CONDITIONAL-GO",
            "confidence": 73,
            "conditions": [
                "通过合规审查（特别是功效宣称）",
                "首期预算降低30%试水",
                "建立达人翻车应急预案"
            ],
            "key_concerns": [
                "合规风险",
                "冷启动期ROI压力",
                "供应链峰值承载能力"
            ],
            "next_steps": [
                "1. 法务合规审查（1周）",
                "2. 选定3-5位KOC进行小规模测试（2周）",
                "3. 根据测试ROI决定是否扩大投放"
            ],
            "summary": "美妆新品抖音推广有机会但风险中等，建议小步快跑、迭代验证。",
            "agent": "策略综合官"
        },
        "total_time_seconds": 12.5,
        "disclaimer": _get_disclaimer()
    }

    return demo_result


@router.get("/agents")
async def list_agents():
    """列出所有可用的Agent及其角色"""
    return {
        "agents": [
            {"key": "opportunity_analyst", "role": "市场机会分析师", "round": 1},
            {"key": "risk_controller", "role": "风险控制官", "round": 1},
            {"key": "proscons_analyst", "role": "优缺点分析师", "round": 1},
            {"key": "devil_advocate", "role": "反向思考师", "round": 2},
            {"key": "competitive_analyst", "role": "竞品环境分析师", "round": 1},
            {"key": "strategy_synthesizer", "role": "策略综合官（决策主席）", "round": 3},
        ],
        "total": 6,
        "rounds": {
            "1": "5位专家并行独立分析",
            "2": "反向思考师交叉质疑",
            "3": "策略综合官最终决策"
        }
    }
