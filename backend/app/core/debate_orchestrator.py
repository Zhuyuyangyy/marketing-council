"""
============================================
营销辩论 orchestrator - 多轮辩论编排器
============================================
管理3轮辩论流程：
- 第1轮：5个Agent并行独立分析
- 第2轮：交叉辩论（互相挑战）
- 第3轮：策略综合官汇总决策
============================================
"""

import asyncio
import json
import time
import uuid
from typing import Any, AsyncIterator, Dict, List, Optional
from loguru import logger

from app.agents.opportunity_analyst import OpportunityAnalyst
from app.agents.risk_controller import RiskController
from app.agents.proscons_analyst import ProsConsAnalyst
from app.agents.devil_advocate import DevilAdvocate
from app.agents.competitive_analyst import CompetitiveAnalyst
from app.agents.strategy_synthesizer import StrategySynthesizer


class DebateOrchestrator:
    """
    多轮辩论编排器

    流程：
    Round 1 → 并行5Agent分析 → Round2 → 交叉挑战 → Round3 → 策略综合 → 最终决策
    """

    def __init__(self):
        self.agents = {
            "opportunity_analyst": OpportunityAnalyst(),
            "risk_controller": RiskController(),
            "proscons_analyst": ProsConsAnalyst(),
            "devil_advocate": DevilAdvocate(),
            "competitive_analyst": CompetitiveAnalyst(),
        }
        self.synthesizer = StrategySynthesizer()
        self.session_id = str(uuid.uuid4())

    def run_debate(self, topic: str) -> Dict[str, Any]:
        """
        同步运行完整辩论，返回最终结果
        """
        logger.info(f"[{self.session_id}] 开始辩论: {topic}")
        start = time.time()

        # Round 1: 并行5Agent分析
        round1_results = self._run_round1(topic)
        logger.info(f"[{self.session_id}] Round1 完成，耗时 {time.time()-start:.1f}s")

        # Round 2: 交叉辩论（Devil Advocate挑战其他Agent）
        round2_results = self._run_round2(topic, round1_results)
        logger.info(f"[{self.session_id}] Round2 完成，耗时 {time.time()-start:.1f}s")

        # Round 3: 策略综合官汇总
        final_decision = self._run_round3(topic, round1_results, round2_results)
        logger.info(f"[{self.session_id}] 辩论完成，总耗时 {time.time()-start:.1f}s")

        return {
            "session_id": self.session_id,
            "topic": topic,
            "round1": round1_results,
            "round2": round2_results,
            "final_decision": final_decision,
            "total_time_seconds": round(time.time() - start, 1),
        }

    async def run_debate_stream(self, topic: str) -> AsyncIterator[Dict[str, Any]]:
        """
        异步流式运行辩论，实时推送每个Agent的输出
        """
        logger.info(f"[{self.session_id}] 开始流式辩论: {topic}")
        start = time.time()

        # Round 1: 并行分析（模拟流式）
        yield {"event": "round_start", "round": 1, "message": "第1轮：5位专家开始独立分析..."}

        round1_tasks = {}
        for key, agent in self.agents.items():
            yield {"event": "agent_start", "round": 1, "agent": key, "role": agent.role}
            try:
                result = await asyncio.to_thread(agent.analyze, topic, {})
            except Exception as e:
                logger.error(f"[{self.session_id}] {key} 分析失败: {e}")
                result = {"error": str(e), "agent": key}
            round1_tasks[key] = result
            yield {"event": "agent_complete", "round": 1, "agent": key, "result": result}

        yield {"event": "round_complete", "round": 1, "results": round1_tasks}

        # Round 2: 交叉辩论
        yield {"event": "round_start", "round": 2, "message": "第2轮：反向思考师质疑其他专家..."}

        devil = self.agents["devil_advocate"]
        try:
            round2_result = await asyncio.to_thread(devil.analyze, topic, {"other_agent_outputs": round1_tasks})
        except Exception as e:
            round2_result = {"error": str(e), "agent": "devil_advocate"}
            logger.error(f"[{self.session_id}] Devil Advocate 失败: {e}")

        yield {"event": "agent_complete", "round": 2, "agent": "devil_advocate", "result": round2_result}
        yield {"event": "round_complete", "round": 2, "results": {"devil_advocate": round2_result}}

        # Round 3: 策略综合
        yield {"event": "round_start", "round": 3, "message": "第3轮：策略综合官汇总决策..."}

        try:
            final_decision = await asyncio.to_thread(
                self.synthesizer.synthesize, topic, round1_tasks, round2_result
            )
        except Exception as e:
            logger.error(f"[{self.session_id}] 策略综合失败: {e}")
            final_decision = {"error": str(e), "decision": "HOLD", "confidence": 0}

        yield {"event": "final_decision", "decision": final_decision}
        yield {"event": "debate_complete", "total_time": round(time.time() - start, 1)}

    def _run_round1(self, topic: str) -> Dict[str, Any]:
        """第1轮：并行5Agent独立分析"""
        results = {}
        for key, agent in self.agents.items():
            try:
                results[key] = agent.analyze(topic, {})
            except Exception as e:
                logger.error(f"[{self.session_id}] {key} failed: {e}")
                results[key] = {"error": str(e), "agent": key}
        return results

    def _run_round2(self, topic: str, round1: Dict[str, Any]) -> Dict[str, Any]:
        """第2轮：Devil Advocate 挑战其他Agent"""
        devil = self.agents["devil_advocate"]
        try:
            return {"devil_advocate": devil.analyze(topic, {"other_agent_outputs": round1})}
        except Exception as e:
            logger.error(f"[{self.session_id}] Devil Advocate failed: {e}")
            return {"devil_advocate": {"error": str(e)}}

    def _run_round3(self, topic: str, round1: Dict[str, Any], round2: Dict[str, Any]) -> Dict[str, Any]:
        """第3轮：策略综合官汇总"""
        try:
            return self.synthesizer.synthesize(topic, round1, round2)
        except Exception as e:
            logger.error(f"[{self.session_id}] 策略综合失败: {e}")
            return {"error": str(e), "decision": "HOLD", "confidence": 0}
