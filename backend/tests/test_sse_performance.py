# marketing-council SSE Performance Test
# 测试多并发下EventSourceResponse稳定性

import asyncio
import time
import httpx
import pytest

BASE_URL = "http://localhost:8009"

async def stream_debate(client, query: str, session_id: str):
    """单次SSE辩论请求"""
    async with client.stream(
        "POST", f"{BASE_URL}/api/debate/stream",
        json={"query": query, "session_id": session_id},
        timeout=30.0,
    ) as resp:
        chunks = 0
        start = time.time()
        async for line in resp.aiter_lines():
            if line.strip():
                chunks += 1
        elapsed = time.time() - start
        return {"chunks": chunks, "elapsed": elapsed, "status": resp.status_code}

@pytest.mark.asyncio
async def test_sse_10_concurrent():
    """10并发SSE测试"""
    async with httpx.AsyncClient() as client:
        tasks = [
            stream_debate(client, f"分析产品{i}的市场策略", f"sse_test_{i}")
            for i in range(10)
        ]
        results = await asyncio.gather(*tasks)
        ok = sum(1 for r in results if r["status"] == 200)
        avg_chunks = sum(r["chunks"] for r in results) / len(results)
        avg_time = sum(r["elapsed"] for r in results) / len(results)
        print(f"\n10并发: {ok}/10 成功 | 平均chunks: {avg_chunks:.0f} | 平均耗时: {avg_time:.1f}s")
        assert ok >= 8, f"成功率 {ok}/10 < 80%"

@pytest.mark.asyncio
async def test_sse_50_concurrent():
    """50并发SSE测试"""
    async with httpx.AsyncClient() as client:
        tasks = [
            stream_debate(client, f"分析{chr(65+i%26)}品牌竞争策略", f"sse_50_{i}")
            for i in range(50)
        ]
        results = await asyncio.gather(*tasks)
        ok = sum(1 for r in results if r["status"] == 200)
        avg_chunks = sum(r["chunks"] for r in results) / len(results)
        print(f"\n50并发: {ok}/50 成功 | 平均chunks: {avg_chunks:.0f}")
        assert ok >= 35, f"成功率 {ok}/50 < 70%"

@pytest.mark.asyncio
async def test_sse_long_connection():
    """长连接稳定性（60秒）"""
    async with httpx.AsyncClient() as client:
        start = time.time()
        async with client.stream(
            "POST", f"{BASE_URL}/api/debate/stream",
            json={"query": "生成完整营销策略报告", "session_id": "long_test"},
            timeout=60.0,
        ) as resp:
            chunks = 0
            async for line in resp.aiter_lines():
                if line.strip():
                    chunks += 1
                    if chunks >= 50:  # 收到50条后断开
                        break
            elapsed = time.time() - start
            print(f"\n长连接: chunks={chunks} elapsed={elapsed:.1f}s status={resp.status_code}")
            assert resp.status_code == 200, f"长连接失败: {resp.status_code}"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])