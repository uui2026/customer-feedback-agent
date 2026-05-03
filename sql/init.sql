-- ============================================
-- 多渠道客户反馈智能处理系统 - 数据库初始化脚本
-- 数据库: SQLite / PostgreSQL / MySQL 均可
-- ============================================

-- 客户反馈表
CREATE TABLE IF NOT EXISTS feedbacks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel VARCHAR(20) NOT NULL COMMENT '反馈渠道: wecom/douyin/email',
    content TEXT NOT NULL COMMENT '反馈内容',
    customer_name VARCHAR(100) COMMENT '客户姓名',
    customer_contact VARCHAR(100) COMMENT '客户联系方式',
    intent VARCHAR(20) COMMENT '意图分类: inquiry(咨询)/complaint(投诉)/suggestion(建议)',
    sentiment VARCHAR(20) COMMENT '情感倾向: positive/negative/neutral',
    tags VARCHAR(500) COMMENT '业务标签(JSON数组)',
    status VARCHAR(20) DEFAULT 'pending' COMMENT '状态: pending/analyzing/routed/replied/closed',
    generated_reply TEXT COMMENT '智能生成的回复内容',
    reply_confirmed BOOLEAN DEFAULT 0 COMMENT '回复是否经人工确认',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 工单表
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    feedback_id INTEGER NOT NULL COMMENT '关联反馈ID',
    team VARCHAR(50) NOT NULL COMMENT '处理团队: 客服组/技术组/产品组/运营组',
    priority VARCHAR(10) DEFAULT 'medium' COMMENT '优先级: high/medium/low',
    sla_deadline TIMESTAMP COMMENT 'SLA截止时间',
    status VARCHAR(20) DEFAULT 'pending' COMMENT '状态: pending/accepted/resolved/closed',
    assigned_to VARCHAR(100) COMMENT '处理人',
    resolution TEXT COMMENT '处理结果',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (feedback_id) REFERENCES feedbacks(id)
);

-- 知识库文章表
CREATE TABLE IF NOT EXISTS knowledge_articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL COMMENT '文章标题',
    content TEXT NOT NULL COMMENT '文章内容',
    category VARCHAR(50) COMMENT '分类: 退款/售后/技术/活动/账号/物流/产品',
    keywords VARCHAR(500) COMMENT '关键词(JSON数组)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 团队表
CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE COMMENT '团队名称',
    description TEXT COMMENT '团队描述',
    keywords VARCHAR(500) COMMENT '匹配关键词(JSON)',
    member_count INTEGER DEFAULT 0 COMMENT '成员数量',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_feedbacks_channel ON feedbacks(channel);
CREATE INDEX IF NOT EXISTS idx_feedbacks_intent ON feedbacks(intent);
CREATE INDEX IF NOT EXISTS idx_feedbacks_status ON feedbacks(status);
CREATE INDEX IF NOT EXISTS idx_feedbacks_created_at ON feedbacks(created_at);
CREATE INDEX IF NOT EXISTS idx_tickets_feedback_id ON tickets(feedback_id);
CREATE INDEX IF NOT EXISTS idx_tickets_team ON tickets(team);
CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);
CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge_articles(category);

-- ============================================
-- 初始数据：4个处理团队
-- ============================================
INSERT OR IGNORE INTO teams (name, description, keywords, member_count) VALUES
('客服组', '处理客户咨询、投诉、售后服务等', '["咨询","投诉","售后","退换货","退款","服务","态度","客服"]', 10),
('技术组', '处理技术故障、系统问题、功能异常等', '["bug","故障","崩溃","报错","技术","系统","功能","无法","异常","闪退"]', 8),
('产品组', '处理产品功能建议、需求反馈、体验优化等', '["建议","功能","需求","优化","改进","体验","希望","新增","改进"]', 6),
('运营组', '处理营销活动、用户运营、内容相关反馈等', '["活动","优惠","推广","运营","积分","会员","券","促销","折扣"]', 5);
