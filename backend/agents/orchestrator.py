"""
智能体编排器
将所有智能体串联成完整的处理流水线
Pipeline: 数据采集 → 意图分析 → 工单路由 → 回复生成
"""

import json
from typing import List, Dict, Optional
from backend.agents.data_collector import DataCollectorAgent, FeedbackCreate
from backend.agents.intent_analyzer import IntentAnalyzerAgent
from backend.agents.ticket_router import TicketRouterAgent
from backend.agents.reply_generator import ReplyGeneratorAgent
from backend.agents.review_analyzer import ReviewAnalyzerAgent


class AgentOrchestrator:
    """智能体编排器 - 管理所有智能体的协作流程"""

    def __init__(self):
        """初始化所有智能体"""
        self.data_collector = DataCollectorAgent()
        self.intent_analyzer = IntentAnalyzerAgent()
        self.ticket_router = TicketRouterAgent()
        self.reply_generator = ReplyGeneratorAgent()
        self.review_analyzer = ReviewAnalyzerAgent()

    def process_feedback(self, feedback_data: dict, knowledge_base: Optional[List[dict]] = None) -> dict:
        """
        处理单条反馈 - 完整流水线

        参数:
            feedback_data: 原始反馈数据
            knowledge_base: 知识库数据

        返回:
            {
                "feedback": {...},      # 分析后的反馈
                "ticket": {...},        # 路由后的工单
                "reply": "回复文本"      # 生成的回复
            }
        """
        # 步骤1: 意图分析
        analysis_result = self.intent_analyzer.analyze(feedback_data.get("content", ""))

        # 合并分析结果到反馈数据
        enriched_feedback = {
            **feedback_data,
            "intent": analysis_result["intent"],
            "sentiment": analysis_result["sentiment"],
            "tags": analysis_result["tags"],
        }

        # 步骤2: 工单路由
        ticket_info = self.ticket_router.route(enriched_feedback)

        # 步骤3: 回复生成
        reply = self.reply_generator.generate(enriched_feedback, knowledge_base)

        return {
            "feedback": enriched_feedback,
            "ticket": ticket_info,
            "reply": reply,
        }

    def process_batch(
        self, feedback_list: List[dict], knowledge_base: Optional[List[dict]] = None
    ) -> List[dict]:
        """
        批量处理反馈

        参数:
            feedback_list: 反馈数据列表
            knowledge_base: 知识库数据

        返回:
            处理结果列表
        """
        results = []
        for feedback_data in feedback_list:
            try:
                result = self.process_feedback(feedback_data, knowledge_base)
                results.append(result)
            except Exception as e:
                results.append({
                    "feedback": feedback_data,
                    "ticket": None,
                    "reply": f"处理失败: {str(e)}",
                    "error": str(e),
                })
        return results

    def collect_and_process(self, knowledge_base: Optional[List[dict]] = None) -> dict:
        """
        从所有渠道采集并处理反馈

        返回:
            {
                "collected": 采集到的反馈数,
                "processed": 成功处理数,
                "results": [...]
            }
        """
        # 采集所有渠道的反馈
        all_feedback = self.data_collector.collect_all()

        # 转换为字典格式
        feedback_dicts = []
        for fb in all_feedback:
            feedback_dicts.append(fb.model_dump())

        # 批量处理
        results = self.process_batch(feedback_dicts, knowledge_base)

        return {
            "collected": len(all_feedback),
            "processed": len([r for r in results if "error" not in r]),
            "results": results,
        }

    def generate_analysis_report(self, feedbacks: Optional[List[dict]] = None) -> dict:
        """
        生成反馈分析报告

        参数:
            feedbacks: 历史反馈数据列表

        返回:
            分析报告字典
        """
        return self.review_analyzer.generate_report(feedbacks)
