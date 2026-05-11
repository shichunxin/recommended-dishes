from fastapi import APIRouter, HTTPException
from agent.core_agent import RecommendationAgent
from scenarios.upsell import UpsellScenario
from scenarios.scene_based import SceneBasedScenario
from scenarios.cold_start import ColdStartScenario
from scenarios.waiter_assistant import WaiterAssistantScenario
from services.dish_service import DishService
from services.user_service import UserService
from services.order_service import OrderService
from typing import Dict, Any, List
import json

router = APIRouter()

agent = RecommendationAgent()
upsell_scenario = UpsellScenario()
scene_based_scenario = SceneBasedScenario()
cold_start_scenario = ColdStartScenario()
waiter_assistant_scenario = WaiterAssistantScenario()

@router.post("/chat")
async def chat(request: Dict[str, Any]):
    user_input = request.get("user_input")
    user_id = request.get("user_id")
    session_id = request.get("session_id")
    
    if not user_input:
        raise HTTPException(status_code=400, detail="user_input is required")
    
    result = agent.run(user_input, user_id, session_id)
    return result

@router.post("/add_to_cart")
async def add_to_cart(request: Dict[str, Any]):
    session_id = request.get("session_id")
    dish_id = request.get("dish_id")
    
    if not session_id or not dish_id:
        raise HTTPException(status_code=400, detail="session_id and dish_id are required")
    
    result = upsell_scenario.handle_add_to_cart(dish_id, session_id)
    return result

@router.get("/current_order/{session_id}")
async def get_current_order(session_id: str):
    order = agent.get_current_order(session_id)
    return {"order": order}

@router.post("/clear_order/{session_id}")
async def clear_order(session_id: str):
    result = agent.clear_order(session_id)
    return {"status": "success", "order": result}

@router.post("/scene_recommend")
async def scene_recommend(request: Dict[str, Any]):
    user_id = request.get("user_id")
    table_info = request.get("table_info")
    
    result = scene_based_scenario.recommend_for_scene(user_id, table_info)
    return result

@router.post("/cold_start")
async def cold_start(request: Dict[str, Any]):
    session_id = request.get("session_id")
    return cold_start_scenario.start_dialog(session_id)

@router.post("/cold_start/continue")
async def cold_start_continue(request: Dict[str, Any]):
    session_id = request.get("session_id")
    user_input = request.get("user_input")
    step = request.get("step", 0)
    
    if not session_id or not user_input:
        raise HTTPException(status_code=400, detail="session_id and user_input are required")
    
    result = cold_start_scenario.continue_dialog(session_id, user_input, step)
    return result

@router.post("/waiter_recommend")
async def waiter_recommend(request: Dict[str, Any]):
    table_id = request.get("table_id")
    user_ids = request.get("user_ids", [])
    
    if not table_id:
        raise HTTPException(status_code=400, detail="table_id is required")
    
    result = waiter_assistant_scenario.recommend_for_table(table_id, user_ids)
    return result

@router.post("/submit_feedback")
async def submit_feedback(request: Dict[str, Any]):
    session_id = request.get("session_id")
    feedback = request.get("feedback")
    
    if not session_id or not feedback:
        raise HTTPException(status_code=400, detail="session_id and feedback are required")
    
    result = agent.submit_feedback(session_id, feedback)
    return result

@router.get("/dishes")
async def get_dishes(category: str = None):
    if category:
        dishes = DishService.get_dishes_by_category(category)
    else:
        dishes = DishService.get_all_dishes()
    return {"dishes": dishes}

@router.get("/dishes/{dish_id}")
async def get_dish(dish_id: str):
    dish = DishService.get_dish(dish_id)
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    return dish

@router.get("/hot_dishes")
async def get_hot_dishes(limit: int = 10):
    dishes = DishService.get_hot_dishes(limit)
    return {"dishes": dishes}

@router.get("/new_dishes")
async def get_new_dishes(limit: int = 10):
    dishes = DishService.get_new_dishes(limit)
    return {"dishes": dishes}

@router.post("/dishes")
async def create_dish(dish_data: Dict[str, Any]):
    required_fields = ["dish_id", "name", "price"]
    if not all(f in dish_data for f in required_fields):
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    result = DishService.create_dish(dish_data)
    return {"status": "success", "dish": result}

@router.get("/users/{user_id}")
async def get_user(user_id: str):
    user = UserService.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/users")
async def create_user(user_data: Dict[str, Any]):
    if "user_id" not in user_data:
        raise HTTPException(status_code=400, detail="user_id is required")
    
    result = UserService.create_user(user_data)
    return {"status": "success", "user": result}

@router.post("/orders")
async def create_order(order_data: Dict[str, Any]):
    result = OrderService.create_order(order_data)
    return {"status": "success", "order": result}

@router.get("/orders/{order_id}")
async def get_order(order_id: str):
    order = OrderService.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order