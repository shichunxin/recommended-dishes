import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.core_agent import RecommendationAgent
from scenarios.upsell import UpsellScenario
from scenarios.scene_based import SceneBasedScenario
from scenarios.cold_start import ColdStartScenario
from scenarios.waiter_assistant import WaiterAssistantScenario

def test_chat():
    print("=== 测试核心Agent对话 ===")
    agent = RecommendationAgent()
    
    result = agent.run("您好", session_id="test_session")
    print(f"用户: 您好")
    print(f"Agent: {result['response']}")
    print(f"意图: {result['intent']}")
    print()
    
    result = agent.run("推荐一些菜品", session_id="test_session")
    print(f"用户: 推荐一些菜品")
    print(f"Agent: {result['response']}")
    print(f"意图: {result['intent']}")
    print()

def test_upsell():
    print("=== 测试智能搭售推荐 ===")
    upsell = UpsellScenario()
    
    result = upsell.recommend_complements("dish_001")
    if result.get("success"):
        print(f"主菜品: {result['main_dish']['name']}")
        print(f"搭配推荐: {result['recommendation']}")
        print(f"搭配菜品: {[d['name'] for d in result['complements'][:3]]}")
    else:
        print(f"错误: {result.get('error')}")
    print()

def test_scene_based():
    print("=== 测试情景感知推荐 ===")
    scene = SceneBasedScenario()
    
    result = scene.recommend_for_scene(user_id="user_001")
    if result.get("success"):
        print(f"场景: {result['scene_name']}")
        print(f"Banner: {result['banner']}")
        print(f"推荐菜品: {[d['name'] for d in result['recommendations']]}")
    else:
        print(f"错误: {result.get('error')}")
    print()

def test_cold_start():
    print("=== 测试新客引导冷启动 ===")
    cold_start = ColdStartScenario()
    
    result = cold_start.start_dialog("cold_start_test")
    print(f"Step {result['step']}: {result['response']}")
    
    result = cold_start.continue_dialog("cold_start_test", "想吃点辣的", 0)
    print(f"用户: 想吃点辣的")
    print(f"Step {result['step']}: {result['response']}")
    
    result = cold_start.continue_dialog("cold_start_test", "川味吧", 1)
    print(f"用户: 川味吧")
    print(f"Step {result['step']}: {result['response']}")
    print()

def test_waiter_assistant():
    print("=== 测试服务员助手 ===")
    waiter = WaiterAssistantScenario()
    
    result = waiter.recommend_for_table("table_007", ["user_001", "user_002"])
    if result.get("success"):
        print(f"餐桌: {result['table_id']}")
        print(f"顾客数: {result['customer_count']}")
        print(f"推荐话术: {result['recommendation_text']}")
        print(f"推荐菜品: {[d['name'] for d in result['recommendations']]}")
    else:
        print(f"错误: {result.get('error')}")
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("餐饮智能推荐引擎 - AI Agent 测试")
    print("=" * 60)
    print()
    
    try:
        test_chat()
        test_upsell()
        test_scene_based()
        test_cold_start()
        test_waiter_assistant()
        
        print("=" * 60)
        print("所有测试完成!")
        print("=" * 60)
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()