# 餐饮智能推荐引擎 - AI Agent

基于大模型的餐饮智能推荐系统，提供个性化菜品推荐、智能搭售、情景感知推荐等功能。

## 项目概述

本项目是一个完整的餐饮智能推荐引擎，采用AI Agent架构设计，集成了大语言模型(LLM)、向量数据库、多目标优化等技术，为餐饮场景提供智能化的推荐服务。

### 核心特性

- **智能对话推荐**：基于LLM的自然语言交互，理解顾客需求并提供个性化推荐
- **多场景支持**：支持搭售推荐、情景感知推荐、新客冷启动、服务员助手等多种场景
- **记忆系统**：基于向量数据库的用户偏好和对话历史存储
- **反思学习**：LLM自我评估推荐质量，支持人工反馈迭代优化
- **多目标排序**：综合考虑顾客偏好、毛利、人气、搭配度、新颖度等因素

## 系统架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                     应用与交互层 (Application Layer)               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│  │ 扫码点餐    │ │ 服务员POS   │ │ 餐桌平板    │ │ 外卖平台    │   │
│  │ 小程序      │ │ 手持终端    │ │ 交互界面    │ │ 集成模块    │   │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘   │
└─────────┼───────────────┼───────────────┼───────────────┼───────────┘
          ▼               ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     AI Agent 核心层 (Agent Core)                   │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    LLM 推理引擎                               │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐   │  │
│  │  │ 意图识别    │→│ 对话管理    │→│ 策略决策与推荐生成   │   │  │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘   │  │
│  └──────────────────────────────────────────────────────────────┘  │
│         ┌────────────────────┼────────────────────┐               │
│         ▼                    ▼                    ▼               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐           │
│  │ 工具调用    │    │ 记忆系统    │    │ 反思学习    │           │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘           │
└─────────┼──────────────────┼──────────────────┼───────────────────┘
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     数据与工具层 (Data & Tools)                    │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│  │ 用户画像    │ │ 菜品知识    │ │ 经营数据    │ │ 策略规则    │   │
│  │ 数据库      │ │ 图谱        │ │ 实时库存    │ │ 配置引擎    │   │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## 目录结构

```
recommended-dishes/
├── agent/                    # AI Agent核心层
│   ├── __init__.py
│   ├── core_agent.py         # 核心推荐Agent
│   ├── tools.py              # 工具调用模块
│   ├── memory.py             # 记忆系统
│   └── reflection.py         # 反思学习模块
├── scenarios/                # 场景模块
│   ├── __init__.py
│   ├── upsell.py             # 智能搭售推荐
│   ├── scene_based.py        # 情景感知推荐
│   ├── cold_start.py         # 新客引导冷启动
│   └── waiter_assistant.py   # 服务员助手
├── services/                 # 服务层
│   ├── __init__.py
│   ├── llm_service.py        # LLM推理引擎
│   ├── dish_service.py       # 菜品服务
│   ├── user_service.py       # 用户服务
│   └── order_service.py      # 订单服务
├── data/                     # 数据层
│   ├── __init__.py
│   ├── database.py           # MySQL数据库连接
│   └── chroma_store.py       # Chroma向量数据库
├── models/                   # 数据模型
│   ├── __init__.py
│   ├── base.py               # 基础模型
│   ├── dish.py               # 菜品模型
│   ├── user.py               # 用户模型
│   ├── order.py              # 订单模型
│   └── recommendation.py     # 推荐记录模型
├── api/                      # API接口
│   ├── __init__.py
│   └── routes.py             # RESTful API路由
├── utils/                    # 工具模块
│   ├── __init__.py
│   └── logger.py             # 日志工具
├── config.py                 # 配置文件
├── main.py                   # 应用入口
├── requirements.txt          # 依赖包
└── test_agent.py             # 测试脚本
```

## 核心组件

### 1. LLM推理引擎

支持多种大语言模型（GPT-4、Qwen-Plus等），提供以下功能：

- **意图识别**：识别用户输入的意图类型
- **推荐生成**：根据上下文生成个性化推荐
- **对话响应**：维护对话流畅性
- **偏好分析**：提取用户口味偏好
- **推荐评估**：评估推荐质量

### 2. 意图识别模块

支持9种意图类型：

| 意图类型 | 说明 |
|---------|------|
| `recommend` | 请求菜品推荐 |
| `add_to_cart` | 添加菜品到购物车 |
| `inquire` | 询问菜品信息 |
| `greet` | 问候语 |
| `goodbye` | 告别 |
| `clarify` | 需要追问澄清 |
| `cold_start` | 新客冷启动 |
| `upsell` | 搭售推荐 |
| `scene_based` | 情景感知推荐 |

### 3. 对话管理

- 维护对话状态和历史
- 追踪上下文信息
- 支持多轮对话

### 4. 策略决策引擎

多目标排序权重配置：

```python
SORTING_WEIGHTS = {
    'customer_preference': 0.35,  # 顾客偏好
    'profit_margin': 0.25,        # 毛利
    'popularity': 0.20,           # 人气
    'compatibility': 0.15,        # 搭配度
    'novelty': 0.05               # 新颖度
}
```

### 5. 工具调用模块

提供9种工具：

| 工具名称 | 功能描述 |
|---------|---------|
| `get_user_profile` | 获取用户画像信息 |
| `get_dish_info` | 获取菜品详情 |
| `get_all_dishes` | 获取所有可用菜品 |
| `get_dishes_by_category` | 按类别获取菜品 |
| `get_user_orders` | 获取用户历史订单 |
| `search_dishes` | 搜索菜品 |
| `get_dish_compatibility` | 获取菜品搭配推荐 |
| `get_hot_dishes` | 获取热门菜品 |
| `get_new_dishes` | 获取新品菜品 |

### 6. 记忆系统

基于Chroma向量数据库实现：

- **用户偏好存储**：持久化用户口味偏好
- **对话历史存储**：保存多轮对话记录
- **推荐记录存储**：记录推荐历史和反馈

### 7. 反思学习模块

- **推荐评估**：从相关性、多样性、吸引力、实用性四个维度评估
- **反馈分析**：分析用户接受/拒绝情况
- **策略优化**：根据反馈调整推荐策略

## 应用场景

### 场景一：智能搭售推荐

**触发条件**：顾客将菜品加入购物车

**执行流程**：
1. 识别搭售意图
2. 查询菜品搭配关系
3. 多目标排序（客单价+毛利+顾客偏好）
4. 生成自然语言推荐话术

**示例**：
```
用户：加入烤鸭到购物车
Agent："搭配烤鸭，98%的顾客会选择这碗鲜香鸭架汤，要来一份吗？"
```

### 场景二：情景感知推荐

**触发条件**：根据时间、人数、场景自动推荐

**场景识别**：
- 周末晚餐 → 约会场景（高颜值、浪漫、精品）
- 工作日午餐 → 快捷场景（快速、健康、实惠）
- 周末聚餐 → 分享场景（多样、适合分享）

**示例**：
```
场景：周六晚市，2人桌
推荐：浪漫套餐、高颜值菜品
Banner："周末约会，为您精选浪漫晚餐"
```

### 场景三：新客引导冷启动

**触发条件**：首次扫码的非会员顾客

**执行流程**：
1. 引导对话："初次见面，告诉我您今天的心情"
2. 动态问题生成："喜欢川味麻辣还是湘味香辣？"
3. 实时构建临时用户画像
4. 生成个性化推荐

**示例**：
```
Agent: "初次见面，告诉我您今天的心情，我帮您量身定制一桌好菜。"
User: "想吃点辣的"
Agent: "好的，喜欢川味麻辣还是湘味香辣呢？"
User: "川味吧"
Agent: "明白了！为您推荐今日川味精选..."
```

### 场景四：服务员助手

**触发条件**：服务员需要为顾客推荐

**执行流程**：
1. 识别顾客会员身份
2. 查询口味偏好
3. 获取当日推荐菜品
4. 筛选符合偏好的菜品
5. 生成推荐话术推送到服务员终端

**示例**：
```
顾客：7号桌，喜辣
推荐话术："这位顾客喜欢辣味，推荐水煮鱼、麻婆豆腐..."
推送至：服务员手表
```

## API接口文档

### 基础URL

```
http://localhost:8001/api
```

### 接口列表

#### 1. 对话接口

**POST** `/chat`

请求体：
```json
{
  "user_input": "推荐一些菜品",
  "user_id": "user_001",
  "session_id": "session_001"
}
```

响应：
```json
{
  "session_id": "session_001",
  "intent": "recommend",
  "response": "为您推荐以下菜品...",
  "context": {...}
}
```

#### 2. 添加到购物车

**POST** `/add_to_cart`

请求体：
```json
{
  "session_id": "session_001",
  "dish_id": "dish_001"
}
```

响应：
```json
{
  "status": "success",
  "message": "搭配烤鸭，98%的顾客会选择这碗鲜香鸭架汤，要来一份吗？"
}
```

#### 3. 情景推荐

**POST** `/scene_recommend`

请求体：
```json
{
  "user_id": "user_001",
  "table_info": {
    "table_id": "table_007",
    "guest_count": 2
  }
}
```

响应：
```json
{
  "success": true,
  "scene": "weekend_dinner",
  "scene_name": "周末约会",
  "recommendations": [...],
  "banner": "周末约会，为您精选浪漫晚餐"
}
```

#### 4. 冷启动引导

**POST** `/cold_start`

请求体：
```json
{
  "session_id": "session_002"
}
```

响应：
```json
{
  "success": true,
  "response": "初次见面，告诉我您今天的心情，我帮您量身定制一桌好菜。",
  "session_id": "session_002",
  "step": 0
}
```

#### 5. 服务员推荐

**POST** `/waiter_recommend`

请求体：
```json
{
  "table_id": "table_007",
  "user_ids": ["user_001", "user_002"]
}
```

响应：
```json
{
  "success": true,
  "table_id": "table_007",
  "customer_count": 2,
  "recommendation_text": "这两位顾客喜欢辣味，推荐...",
  "recommendations": [...]
}
```

#### 6. 提交反馈

**POST** `/submit_feedback`

请求体：
```json
{
  "session_id": "session_001",
  "feedback": {
    "accepted": ["dish_001"],
    "rejected": ["dish_002"],
    "rating": 4
  }
}
```

响应：
```json
{
  "status": "success",
  "message": "反馈已接收"
}
```

#### 7. 获取菜品列表

**GET** `/dishes?category=川菜`

响应：
```json
{
  "dishes": [
    {
      "dish_id": "dish_001",
      "name": "水煮鱼",
      "price": 68.0,
      "category": "川菜",
      ...
    }
  ]
}
```

#### 8. 获取热门菜品

**GET** `/hot_dishes?limit=10`

响应：
```json
{
  "dishes": [...]
}
```

## 安装部署

### 环境要求

- Python 3.8+
- MySQL 5.7+
- 内存：至少4GB

### 安装步骤

1. **克隆项目**
```bash
cd recommended-dishes
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**

创建 `.env` 文件：
```env
# 数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=password
MYSQL_DB=catering

# LLM配置
LLM_MODEL=qwen-7b-chat
LLM_API_KEY=your_api_key
LLM_BASE_URL=http://localhost:8000/v1

# 应用配置
APP_HOST=0.0.0.0
APP_PORT=8001
```

4. **初始化数据库**
```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE catering CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 表会在启动时自动创建
```

5. **启动服务**
```bash
python main.py
```

服务将在 `http://localhost:8001` 启动

### Docker部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["python", "main.py"]
```

```bash
docker build -t catering-recommendation .
docker run -p 8001:8001 catering-recommendation
```

## 配置说明

### 数据库配置

| 配置项 | 说明 | 默认值 |
|-------|------|--------|
| `MYSQL_HOST` | MySQL主机地址 | localhost |
| `MYSQL_PORT` | MySQL端口 | 3306 |
| `MYSQL_USER` | MySQL用户名 | root |
| `MYSQL_PASSWORD` | MySQL密码 | password |
| `MYSQL_DB` | 数据库名称 | catering |

### LLM配置

| 配置项 | 说明 | 默认值 |
|-------|------|--------|
| `LLM_MODEL` | 模型名称 | qwen-7b-chat |
| `LLM_API_KEY` | API密钥 | - |
| `LLM_BASE_URL` | API地址 | http://localhost:8000/v1 |

### 推荐策略配置

| 配置项 | 说明 | 默认值 |
|-------|------|--------|
| `RECOMMENDATION_MAX_ITEMS` | 最大推荐数量 | 6 |
| `CONFIDENCE_THRESHOLD` | 置信度阈值 | 0.7 |

### 多目标排序权重

可在 `config.py` 中调整：

```python
SORTING_WEIGHTS = {
    'customer_preference': 0.35,  # 顾客偏好权重
    'profit_margin': 0.25,        # 毛利权重
    'popularity': 0.20,           # 人气权重
    'compatibility': 0.15,        # 搭配度权重
    'novelty': 0.05               # 新颖度权重
}
```

## 使用示例

### Python SDK

```python
from agent.core_agent import RecommendationAgent

# 初始化Agent
agent = RecommendationAgent()

# 对话推荐
result = agent.run("推荐一些菜品", user_id="user_001")
print(result['response'])

# 添加到购物车
agent.add_to_cart(session_id="session_001", dish_id="dish_001")

# 获取当前订单
order = agent.get_current_order(session_id="session_001")
print(order)
```

### 场景使用

```python
from scenarios.upsell import UpsellScenario
from scenarios.scene_based import SceneBasedScenario
from scenarios.cold_start import ColdStartScenario
from scenarios.waiter_assistant import WaiterAssistantScenario

# 智能搭售
upsell = UpsellScenario()
result = upsell.recommend_complements("dish_001")

# 情景推荐
scene = SceneBasedScenario()
result = scene.recommend_for_scene(user_id="user_001")

# 冷启动
cold_start = ColdStartScenario()
result = cold_start.start_dialog("session_002")

# 服务员助手
waiter = WaiterAssistantScenario()
result = waiter.recommend_for_table("table_007", ["user_001"])
```

### cURL示例

```bash
# 对话接口
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"user_input": "推荐一些菜品", "user_id": "user_001"}'

# 情景推荐
curl -X POST http://localhost:8001/api/scene_recommend \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_001"}'

# 获取菜品列表
curl http://localhost:8001/api/dishes
```

## 数据模型

### 菜品模型 (Dish)

| 字段 | 类型 | 说明 |
|-----|------|------|
| dish_id | String | 菜品ID（主键） |
| name | String | 菜品名称 |
| description | Text | 菜品描述 |
| price | Float | 价格 |
| category | String | 类别 |
| tags | JSON | 标签列表 |
| image_url | String | 图片URL |
| is_available | Boolean | 是否可用 |
| is_hot | Boolean | 是否热门 |
| is_new | Boolean | 是否新品 |
| cost | Float | 成本 |
| popularity | Float | 人气值 |
| compatibility | JSON | 搭配关系 |

### 用户模型 (User)

| 字段 | 类型 | 说明 |
|-----|------|------|
| user_id | String | 用户ID（主键） |
| name | String | 姓名 |
| phone | String | 电话 |
| email | String | 邮箱 |
| preferences | JSON | 偏好设置 |
| allergens | JSON | 过敏信息 |

### 订单模型 (Order)

| 字段 | 类型 | 说明 |
|-----|------|------|
| order_id | String | 订单ID（主键） |
| user_id | String | 用户ID |
| table_id | String | 餐桌ID |
| items | JSON | 菜品列表 |
| total_amount | Float | 总金额 |
| status | Enum | 订单状态 |

## 测试

运行测试脚本：

```bash
python test_agent.py
```

测试覆盖：
- 核心Agent对话
- 智能搭售推荐
- 情景感知推荐
- 新客引导冷启动
- 服务员助手

## 性能优化

### 1. 数据库优化

- 使用连接池管理数据库连接
- 添加适当的索引
- 定期清理过期数据

### 2. 缓存策略

- 使用Redis缓存热门菜品
- 缓存用户画像信息
- 缓存推荐结果

### 3. 异步处理

- 使用异步API提高并发性能
- 后台任务处理反馈学习

## 监控与日志

### 日志级别

- `DEBUG`: 详细调试信息
- `INFO`: 一般信息
- `WARNING`: 警告信息
- `ERROR`: 错误信息

### 日志配置

```python
LOG_LEVEL = INFO  # 可在.env中配置
```

## 扩展开发

### 添加新的意图类型

1. 在 `llm_service.py` 的 `extract_intent` 方法中添加新意图
2. 在 `core_agent.py` 的 `decide_tool_call` 方法中添加工具调用逻辑
3. 在 `generate_response` 方法中添加响应生成逻辑

### 添加新的工具

1. 在 `tools.py` 中添加静态方法
2. 在 `TOOLS` 列表中注册工具定义
3. 在Agent中调用新工具

### 添加新的场景

1. 在 `scenarios/` 目录创建新文件
2. 实现场景类
3. 在 `api/routes.py` 中添加API接口

## 常见问题

### Q: 如何切换LLM模型？

A: 修改 `.env` 文件中的 `LLM_MODEL` 和 `LLM_BASE_URL` 配置。

### Q: 如何调整推荐权重？

A: 修改 `config.py` 中的 `SORTING_WEIGHTS` 配置。

### Q: 如何添加新的菜品标签？

A: 在创建菜品时，在 `tags` 字段中添加新标签，系统会自动识别。

### Q: 如何处理用户过敏信息？

A: 在用户画像的 `allergens` 字段中记录过敏信息，推荐时会自动过滤相关菜品。

## 版本历史

- **v1.0.0** (2026-05-09)
  - 初始版本发布
  - 实现核心Agent功能
  - 支持4种推荐场景
  - 完整的API接口

## 许可证

MIT License

## 联系方式

- 项目地址：`recommended-dishes/`
- 技术支持：提交Issue或Pull Request