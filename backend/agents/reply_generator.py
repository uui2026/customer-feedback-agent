"""
回复生成智能体
根据反馈内容和知识库匹配结果，自动生成合适的回复文本
支持三种回复策略：标准回复、安抚回复、引导回复
"""

import json
from typing import List, Optional


class ReplyGeneratorAgent:
    """智能回复生成智能体"""

    # 不同意图的标准回复模板
    REPLY_TEMPLATES = {
        "complaint": {
            "with_knowledge": "尊敬的{customer_name}，非常抱歉给您带来了不好的体验。{knowledge_reply}我们会尽快为您处理，感谢您的反馈！",
            "without_knowledge": "尊敬的{customer_name}，非常抱歉给您带来了不好的体验。我们已收到您的反馈，客服团队将在4小时内与您联系处理。如有紧急情况，请拨打客服热线：400-XXX-XXXX。再次为给您带来的不便表示歉意！",
        },
        "inquiry": {
            "with_knowledge": "尊敬的{customer_name}，感谢您的咨询！{knowledge_reply}如有其他问题，欢迎随时联系我们。",
            "without_knowledge": "尊敬的{customer_name}，感谢您的咨询！您的问题我们已记录，客服人员将在24小时内回复您。您也可以访问我们的帮助中心获取更多信息。",
        },
        "suggestion": {
            "with_knowledge": "尊敬的{customer_name}，感谢您的宝贵建议！{knowledge_reply}我们会认真考虑您的意见，持续改进我们的产品和服务。",
            "without_knowledge": "尊敬的{customer_name}，感谢您的宝贵建议！我们已将您的建议记录并转交给产品团队评估。您的意见对我们非常重要，我们会持续优化产品体验。",
        },
    }

    # 知识库匹配后的回复片段
    KNOWLEDGE_REPLY_FORMAT = "根据您的情况，建议您：{answer} "

    def generate(self, feedback: dict, knowledge_base: Optional[List[dict]] = None) -> str:
        """
        生成客户回复

        参数:
            feedback: 反馈信息，需包含 customer_name, intent, content, tags 字段
            knowledge_base: 知识库文章列表

        返回:
            生成的回复文本
        """
        customer_name = feedback.get("customer_name", "用户")
        intent = feedback.get("intent", "inquiry")
        content = feedback.get("content", "")
        tags = feedback.get("tags", [])

        # 1. 在知识库中搜索匹配
        matched_article = self._search_knowledge(content, tags, knowledge_base)

        # 2. 根据匹配结果选择回复模板
        templates = self.REPLY_TEMPLATES.get(intent, self.REPLY_TEMPLATES["inquiry"])

        if matched_article:
            # 使用知识库匹配结果生成回复
            knowledge_reply = self.KNOWLEDGE_REPLY_FORMAT.format(
                answer=matched_article.get("content", "")
            )
            reply = templates["with_knowledge"].format(
                customer_name=customer_name,
                knowledge_reply=knowledge_reply,
            )
        else:
            # 使用默认模板回复
            reply = templates["without_knowledge"].format(
                customer_name=customer_name,
            )

        return reply

    def _search_knowledge(
        self, content: str, tags: List[str], knowledge_base: Optional[List[dict]]
    ) -> Optional[dict]:
        """
        在知识库中搜索匹配的文章
        基于关键词匹配打分，返回最佳匹配
        """
        if not knowledge_base:
            return None

        content_lower = content.lower()
        best_match = None
        best_score = 0

        for article in knowledge_base:
            score = 0
            # 标题匹配
            title = article.get("title", "").lower()
            if any(char in content_lower for char in title if len(char) > 1):
                score += 3

            # 关键词匹配
            keywords_str = article.get("keywords", "[]")
            try:
                keywords = json.loads(keywords_str) if isinstance(keywords_str, str) else keywords_str
            except (json.JSONDecodeError, TypeError):
                keywords = []

            for kw in keywords:
                if kw.lower() in content_lower:
                    score += 2
                # 标签与关键词交叉匹配
                for tag in tags:
                    if tag in kw or kw in tag:
                        score += 1

            # 分类匹配
            category = article.get("category", "")
            for tag in tags:
                if tag in category or category in tag:
                    score += 2

            if score > best_score:
                best_score = score
                best_match = article

        # 需要至少2分才返回匹配结果
        if best_score >= 2:
            return best_match
        return None

    def generate_batch_replies(
        self, feedbacks: List[dict], knowledge_base: Optional[List[dict]] = None
    ) -> List[dict]:
        """
        批量生成回复

        参数:
            feedbacks: 反馈列表
            knowledge_base: 知识库

        返回:
            [{"feedback_id": id, "reply": "回复内容"}, ...]
        """
        results = []
        for feedback in feedbacks:
            reply = self.generate(feedback, knowledge_base)
            results.append({
                "feedback_id": feedback.get("id"),
                "reply": reply,
            })
        return results
