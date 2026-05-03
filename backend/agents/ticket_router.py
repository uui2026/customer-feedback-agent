"""
工单路由智能体
根据反馈的意图和关键词，自动分配到合适的团队，并设置SLA截止时间
"""

import json
from datetime import datetime, timedelta
from typing import Dict, Optional
from backend.config import settings


class TicketRouterAgent:
    """工单智能路由智能体"""

    def __init__(self):
        """初始化路由智能体，加载团队配置"""
        self.teams = settings.teams
        self.sla_hours = settings.sla_hours

    def route(self, feedback: dict) -> dict:
        """
        根据反馈信息路由到对应团队

        参数:
            feedback: 反馈数据字典，需包含 intent, content, tags 字段

        返回:
            {
                "team": "团队名称",
                "priority": "high|medium|low",
                "sla_deadline": datetime,
                "assigned_to": "默认处理人"
            }
        """
        # 1. 确定优先级
        priority = self._determine_priority(feedback)

        # 2. 匹配最佳团队
        team = self._match_team(feedback)

        # 3. 计算 SLA 截止时间
        sla_deadline = self._calculate_sla_deadline(feedback.get("intent", "inquiry"), priority)

        # 4. 选择默认处理人（模拟）
        assigned_to = self._assign_handler(team)

        return {
            "team": team,
            "priority": priority,
            "sla_deadline": sla_deadline,
            "assigned_to": assigned_to,
        }

    def _determine_priority(self, feedback: dict) -> str:
        """
        确定工单优先级
        - 投诉类默认高优先级
        - 包含紧急关键词的提升优先级
        - 其他情况为中优先级
        """
        intent = feedback.get("intent", "inquiry")
        content = feedback.get("content", "")

        # 投诉类为高优先级
        if intent == "complaint":
            return "high"

        # 包含紧急关键词
        urgent_keywords = ["紧急", "马上", "尽快", "立刻", "马上", "急", "立即", "安全"]
        if any(kw in content for kw in urgent_keywords):
            return "high"

        # 建议类为低优先级
        if intent == "suggestion":
            return "low"

        return "medium"

    def _match_team(self, feedback: dict) -> str:
        """
        根据反馈内容匹配最佳处理团队
        通过关键词匹配打分，选择得分最高的团队
        """
        content = feedback.get("content", "").lower()
        tags = feedback.get("tags", [])
        intent = feedback.get("intent", "")

        # 将标签也加入匹配文本
        match_text = content + " " + " ".join(tags)

        team_scores = {}

        for team_name, team_config in self.teams.items():
            keywords = team_config["keywords"]
            score = sum(1 for kw in keywords if kw in match_text)
            team_scores[team_name] = score

        # 选择得分最高的团队
        best_team = max(team_scores, key=team_scores.get)

        # 如果所有团队得分为0，根据意图分配默认团队
        if team_scores[best_team] == 0:
            if intent == "complaint":
                return "客服组"
            elif intent == "suggestion":
                return "产品组"
            else:
                return "客服组"

        return best_team

    def _calculate_sla_deadline(self, intent: str, priority: str) -> datetime:
        """
        计算 SLA 截止时间
        - complaint(投诉): 4小时
        - inquiry(咨询): 24小时
        - suggestion(建议): 72小时
        - 高优先级额外缩短 50%
        """
        base_hours = self.sla_hours.get(intent, 24)

        # 高优先级 SLA 缩短50%
        if priority == "high":
            base_hours = max(1, base_hours // 2)

        return datetime.now() + timedelta(hours=base_hours)

    def _assign_handler(self, team: str) -> str:
        """
        为工单指派默认处理人
        实际生产中应根据团队成员的工作负载动态分配
        """
        handler_map = {
            "客服组": "客服小王",
            "技术组": "技术小李",
            "产品组": "产品小张",
            "运营组": "运营小赵",
        }
        return handler_map.get(team, "待分配")
