"""
MarketingCouncil Complete Demo Script
完整演示脚本 - 支持 Mock 模式和真实 API 模式

用法:
    python run_demo.py                 # 交互式演示
    python run_demo.py --mock          # 纯Mock模式演示
    python run_demo.py --topic "..."   # 指定主题
    python run_demo.py --list-agents   # 显示Agent列表
    python run_demo.py --test-api      # 测试Spark API连接
"""

import sys
import os
import argparse
import time
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))


def print_header(title: str):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_step(step: str):
    print(f"\n[STEP] {step}")


def demo_mock_mode(topic: str = "抖音电商美妆新品推广方案"):
    """纯Mock模式演示 - 不需要任何API Key"""
    print_header("MarketingCouncil - Mock 演示模式")
    print("🎭 当前运行: Mock LLM (无 API Key)")
    print(f"📋 辩论主题: {topic}")
    print()

    from app.core.llm_factory import get_crewai_llm

    llm = get_crewai_llm(temperature=0.7)
    print(f"✅ LLM 初始化: {type(llm).__name__}")

    # Simulate debate flow
    agents = [
        ("🎯 机会分析师", "分析市场空间、增长潜力、机会窗口"),
        ("⚠️ 风险控制官", "识别风险因素、评估威胁等级"),
        ("⚖️ 优缺点分析师", "量化利弊、计算净得分"),
        ("📊 竞品环境分析师", "分析竞争格局、进入时机"),
    ]

    print_step("Round 1: 5位专家并行独立分析")
    round1_results = {}
    for emoji, desc in agents:
        print(f"  {emoji} {desc}...", end=" ", flush=True)
        time.sleep(0.8)
        result = llm(f"作为{desc}，请分析这个营销方案: {topic}")
        # Parse key info from mock response
        score = 60 + int(hash(result[:10]) % 35)
        round1_results[emoji] = {"score": score, "raw": result[:100]}
        print(f"✓ (得分: {score}/100)")

    print_step("Round 2: 反向思考师交叉质疑")
    print("  😈 反向思考师正在质疑各专家的结论...", end=" ", flush=True)
    time.sleep(1.2)
    challenge_result = llm(f"作为反向思考师，请质疑这个营销方案的最脆弱假设: {topic}")
    print(f"✓")
    print(f"     💀 最脆弱假设: GMV增长假设过于乐观")
    print(f"     ⚡ 关键质疑: 达人翻车风险、供应链峰值承载能力")

    print_step("Round 3: 策略综合官最终决策")
    print("  🏛️ 策略综合官正在汇总所有观点...", end=" ", flush=True)
    time.sleep(1.0)

    # Calculate decision
    avg_score = sum(r["score"] for r in round1_results.values()) / len(round1_results)
    decision = "STRONG-GO" if avg_score > 75 else "CONDITIONAL-GO" if avg_score > 55 else "HOLD"
    confidence = min(95, max(30, int(avg_score * 1.2)))

    print(f"✓")

    print_header("🏛️ 最终决策")
    print(f"""
    ╔══════════════════════════════════════╗
    ║  决策: {decision:<28}║
    ║  置信度: {confidence}%{' '*25}║
    ╠══════════════════════════════════════╣
    ║  📋 通过条件:                        ║
    ║    1. 通过合规审查（功效宣称）        ║
    ║    2. 首期预算降低30%试水            ║
    ║    3. 建立达人翻车应急预案           ║
    ╠══════════════════════════════════════╣
    ║  ⚠️ 关键风险:                        ║
    ║    - 合规风险（广告法）               ║
    ║    - 冷启动ROI压力                    ║
    ║    - 供应链峰值承载                   ║
    ╠══════════════════════════════════════╣
    ║  📅 下一步:                           ║
    ║    1. 法务合规审查（1周）             ║
    ║    2. 3-5位KOC小规模测试（2周）       ║
    ║    3. 根据ROI决定是否扩大             ║
    ╚══════════════════════════════════════╝
    """)

    print(f"    💡 总结: 美妆新品抖音推广有机会但风险中等，建议小步快跑。")
    print(f"    ⏱️ 演示耗时: ~5秒")
    print(f"    🎭 模式: Mock LLM (无需API Key)")
    print()

    return {
        "decision": decision,
        "confidence": confidence,
        "topic": topic,
        "mode": "mock"
    }


def demo_test_api():
    """测试 Spark API 连接"""
    print_header("MarketingCouncil - API 连接测试")

    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv("SPARK_API_KEY", "").strip()
    api_secret = os.getenv("SPARK_API_SECRET", "").strip()
    app_id = os.getenv("SPARK_APP_ID", "").strip()

    if not api_key or not api_secret:
        print("⚠️  未配置 API Key，将使用 Mock 模式")
        print("   请在 .env 文件中配置:")
        print("   SPARK_APP_ID=your_app_id")
        print("   SPARK_API_KEY=your_api_key")
        print("   SPARK_API_SECRET=your_api_secret")
        print()
        print("   或访问 https://console.xfyun.cn/ 申请讯飞星火API")
        return

    print(f"✅ API Key: {api_key[:8]}...")
    print(f"✅ API Secret: {api_secret[:6]}...")
    print(f"✅ App ID: {app_id}")
    print()

    print("🔄 正在测试 Spark API 连接...")

    try:
        from app.core.llm_spark_mock import SparkChatModel
        model = SparkChatModel(
            spark_app_id=app_id,
            spark_api_key=api_key,
            spark_api_secret=api_secret,
            spark_model_version="generalv3.5",
            max_tokens=100,
        )

        from langchain_core.messages import HumanMessage
        result = model._generate([HumanMessage(content="说hello")])

        content = result.generations[0].message.content
        print(f"✅ API 调用成功!")
        print(f"   响应: {content[:100]}...")
    except Exception as e:
        print(f"❌ API 调用失败: {e}")
        print("   详细信息:", str(e))


def demo_list_agents():
    """显示所有 Agent 信息"""
    print_header("MarketingCouncil - Agent 列表")

    agents = [
        ("🎯 机会分析师", "opportunity_analyst", 1,
         "识别营销方案的市场空间、机会窗口、增长潜力"),
        ("⚠️ 风险控制官", "risk_controller", 1,
         "评估营销方案的风险等级、威胁因素、潜在损失"),
        ("⚖️ 优缺点分析师", "proscons_analyst", 1,
         "量化分析营销方案的正面和负面因素"),
        ("📊 竞品环境分析师", "competitive_analyst", 1,
         "分析竞争格局、竞品动向、市场进入时机"),
        ("😈 反向思考师", "devil_advocate", 2,
         "故意唱反调，质疑假设，找出方案中的漏洞和盲区"),
        ("🏛️ 策略综合官", "strategy_synthesizer", 3,
         "汇总所有Agent观点，输出最终决策建议"),
    ]

    print("\n6个专业AI Agent团队:")
    print("-" * 60)
    for emoji, key, round_num, desc in agents:
        print(f"  {emoji} {key}")
        print(f"      Round {round_num} | {desc}")
        print()

    print("辩论流程:")
    print("  Round 1: 5位专家并行独立分析")
    print("  Round 2: 反向思考师交叉质疑")
    print("  Round 3: 策略综合官汇总决策")
    print()


def demo_full_flow(topic: str):
    """完整流程演示（需要后端运行）"""
    print_header(f"MarketingCouncil - 完整辩论流程")
    print(f"📋 主题: {topic}")
    print()
    print("⚠️  此模式需要后端服务运行中:")
    print("   cd backend && python -m uvicorn app.main:app --port 8009")
    print()
    print("💡 建议使用 Mock 演示模式: python run_demo.py --mock")
    print()


def main():
    parser = argparse.ArgumentParser(description="MarketingCouncil 完整演示脚本")
    parser.add_argument("--topic", "-t", type=str, default="", help="辩论主题")
    parser.add_argument("--mock", "-m", action="store_true", help="Mock模式演示")
    parser.add_argument("--test-api", action="store_true", help="测试Spark API连接")
    parser.add_argument("--list-agents", action="store_true", help="显示Agent列表")
    args = parser.parse_args()

    topic = args.topic or "抖音电商美妆新品推广，主打年轻女性市场，预算100万，周期3个月"

    if args.test_api:
        demo_test_api()
    elif args.list_agents:
        demo_list_agents()
    elif args.mock:
        demo_mock_mode(topic)
    else:
        print_header("MarketingCouncil 演示")
        print("请选择演示模式:")
        print()
        print("  1. Mock 演示 (无需API Key): python run_demo.py --mock")
        print("  2. 测试 API 连接:          python run_demo.py --test-api")
        print("  3. 显示 Agent 列表:        python run_demo.py --list-agents")
        print("  4. 完整辩论 (需后端运行):   cd backend && python -m uvicorn app.main:app --port 8009")
        print()
        print("  💡 快速体验: python run_demo.py --mock")
        print()

        # Auto-run mock demo
        time.sleep(1)
        demo_mock_mode(topic)


if __name__ == "__main__":
    main()
