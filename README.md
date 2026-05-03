# 多渠道客户反馈智能处理系统

> 5-Agent Pipeline: 数据采集 → 意图分析 → 工单路由 → 回复生成 → 复盘分析

## 核心痛点

客户反馈分散在企微、抖音、邮件、客服系统等多个渠道，人工汇总、分类、响应效率低，
漏处理、超时回复频发，无法沉淀共性问题，导致客户体验差、运营复盘难。

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    前端 (Vue3 + ElementPlus + ECharts)   │
│  Dashboard │ 反馈管理 │ 工单管理 │ 知识库 │ 智能体管线    │
└──────────────────────────┬──────────────────────────────┘
                           │ HTTP API
┌──────────────────────────▼──────────────────────────────┐
│                    后端 (FastAPI + SQLAlchemy)            │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ 数据采集  │→│ 意图分析  │→│ 工单路由  │              │
│  │  Agent   │  │  Agent   │  │  Agent   │              │
│  └──────────┘  └──────────┘  └──────────┘              │
│       │                              │                   │
│  ┌────▼────┐  ┌──────────┐  ┌───────▼─────┐            │
│  │ 渠道采集 │  │ 回复生成  │  │  复盘分析   │            │
│  │ 企微/抖音│  │  Agent   │  │   Agent    │            │
│  │ /邮件   │  └──────────┘  └─────────────┘            │
│  └─────────┘                                            │
│                                                          │
│  ┌─────────────────────────────────────┐                │
│  │  SQLite (aiosqlite) + 知识库 (FAQ)  │                │
│  └─────────────────────────────────────┘                │
└─────────────────────────────────────────────────────────┘
```

## 5 个 Agent 说明

| Agent | 职责 | 技术实现 |
|-------|------|---------|
| 数据采集 Agent | 对接企微/抖音/邮件API，实时拉取反馈 | 模拟采集器（可对接真实API） |
| 意图分析 Agent | 识别咨询/投诉/建议意图 + 情感分析 | 中文关键词规则引擎 |
| 工单路由 Agent | 根据标签匹配团队，设置SLA提醒 | 关键词匹配 + SLA策略 |
| 回复生成 Agent | 基于知识库自动生成合规回复 | FAQ匹配 + 模板引擎 |
| 复盘分析 Agent | 汇总共性问题，生成趋势报告 | 统计聚合 + 趋势分析 |

## SLA 策略

- **投诉类**: 4小时响应
- **咨询类**: 24小时响应
- **建议类**: 72小时响应

## 处理团队

- 客服组：处理咨询、投诉、售后
- 技术组：处理故障、系统问题
- 产品组：处理功能建议、体验优化
- 运营组：处理活动、营销相关

## 快速开始

### 1. 环境要求

- Python 3.10+
- Node.js 16+（前端）
- pip / npm

### 2. 安装依赖

```bash
# 后端
pip install -r requirements.txt

# 前端
cd frontend
npm install
```

### 3. 启动服务

```bash
# 方式一：一键启动
chmod +x start.sh
./start.sh

# 方式二：分别启动
# 后端
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# 前端
cd frontend && npm run dev
```

### 4. 访问

- 后端 API 文档: http://localhost:8000/docs
- 前端管理界面: http://localhost:5173

## API 接口一览

### 反馈管理
```
GET    /api/feedbacks          获取反馈列表（支持分页、筛选）
GET    /api/feedbacks/{id}     获取反馈详情
POST   /api/feedbacks          创建反馈
DELETE /api/feedbacks/{id}     删除反馈
POST   /api/feedbacks/batch-collect  批量采集（触发数据采集Agent）
POST   /api/feedbacks/{id}/analyze   触发意图分析
POST   /api/feedbacks/{id}/reply     生成回复
```

### 工单管理
```
GET    /api/tickets            获取工单列表
GET    /api/tickets/{id}       获取工单详情
POST   /api/tickets            创建工单
PUT    /api/tickets/{id}       更新工单状态
```

### 仪表盘
```
GET    /api/dashboard/stats    系统统计数据
```

### 知识库
```
GET    /api/knowledge          获取知识库列表
POST   /api/knowledge          创建文章
PUT    /api/knowledge/{id}     更新文章
DELETE /api/knowledge/{id}     删除文章
```

### 智能体
```
POST   /api/agent/pipeline/run     运行完整流水线
GET    /api/agent/pipeline/status  获取流水线状态
POST   /api/agent/collect          触发数据采集Agent
POST   /api/agent/analyze/{id}     触发意图分析Agent
POST   /api/agent/route/{id}       触发工单路由Agent
POST   /api/agent/reply/{id}       触发回复生成Agent
GET    /api/agent/report           生成复盘分析报告
```

## 项目结构

```
customer-feedback-agent/
├── backend/
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置管理
│   ├── database.py          # 数据库连接
│   ├── agents/
│   │   ├── data_collector.py    # 数据采集 Agent
│   │   ├── intent_analyzer.py   # 意图分析 Agent
│   │   ├── ticket_router.py     # 工单路由 Agent
│   │   ├── reply_generator.py   # 回复生成 Agent
│   │   ├── review_analyzer.py   # 复盘分析 Agent
│   │   └── orchestrator.py      # Agent 编排器
│   ├── api/
│   │   ├── feedback.py      # 反馈接口
│   │   ├── ticket.py        # 工单接口
│   │   ├── dashboard.py     # 仪表盘接口
│   │   ├── knowledge.py     # 知识库接口
│   │   └── agent.py         # 智能体接口
│   ├── models/
│   │   ├── feedback.py      # 反馈模型
│   │   ├── ticket.py        # 工单模型
│   │   ├── knowledge.py     # 知识库模型
│   │   └── team.py          # 团队模型
│   ├── services/
│   │   ├── feedback_service.py
│   │   ├── ticket_service.py
│   │   └── knowledge_service.py
│   └── knowledge_base/
│       └── faq.json         # 初始FAQ数据（10+条）
├── frontend/
│   ├── src/
│   │   ├── App.vue          # 主布局
│   │   ├── main.js          # 入口
│   │   ├── views/
│   │   │   ├── Dashboard.vue        # 仪表盘
│   │   │   ├── FeedbackList.vue     # 反馈管理
│   │   │   ├── TicketList.vue       # 工单管理
│   │   │   ├── KnowledgeBase.vue    # 知识库管理
│   │   │   └── AgentPipeline.vue    # 智能体管线
│   │   ├── api/             # API 调用封装
│   │   └── router/          # 路由配置
│   ├── package.json
│   └── vite.config.js
├── sql/
│   └── init.sql             # 数据库建表+初始化SQL
├── requirements.txt
├── start.sh                 # 一键启动脚本
└── README.md
```

## 技术栈

- **后端**: Python 3.10+ / FastAPI / SQLAlchemy 2.0 / aiosqlite
- **前端**: Vue3 / Vite / Element Plus / ECharts / Axios
- **数据库**: SQLite（可切换 PostgreSQL/MySQL）
- **AI引擎**: 中文关键词规则引擎（可扩展接入 LLM）

## 扩展方向

1. 接入真实渠道API（企业微信开放平台、抖音开放平台、邮件SMTP/IMAP）
2. 接入大语言模型（如 GPT/Claude）提升意图分析和回复生成质量
3. 接入 Redis 实现消息队列和缓存
4. 添加用户认证和权限管理
5. 添加 Webhook 通知（钉钉、飞书、企微机器人）
6. 部署为 Docker 容器化服务
