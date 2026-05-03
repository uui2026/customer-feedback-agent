"""
评论分析智能体
分析反馈数据的趋势和共性问题，生成分析报告
用于管理层决策和产品优化参考
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import Counter


class ReviewAnalyzerAgent:
    """评论趋势分析智能体"""

    def generate_report(self, feedbacks: Optional[List[dict]] = None) -> dict:
        """
        生成反馈分析报告

        参数:
            feedbacks: 反馈数据列表

        返回:
            {
                "summary": "概要描述",
                "total_count": 总数,
                "by_channel": {...},
                "by_intent": {...},
                "by_sentiment": {...},
                "top_issues": [...],
                "top_tags": [...],
                "trends": [...],
                "recommendations": [...]
            }
        """
        if not feedbacks:
            return {
                "summary": "暂无反馈数据",
                "total_count": 0,
                "by_channel": {},
                "by_intent": {},
                "by_sentiment": {},
                "top_issues": [],
                "top_tags": [],
                "trends": [],
                "recommendations": [],
            }

        # 1. 基础统计
        total_count = len(feedbacks)
        by_channel = self._count_by_field(feedbacks, "channel")
        by_intent = self._count_by_field(feedbacks, "intent")
        by_sentiment = self._count_by_field(feedbacks, "sentiment")

        # 2. 热门问题分析
        top_issues = self._analyze_top_issues(feedbacks)

        # 3. 热门标签
        top_tags = self._analyze_top_tags(feedbacks)

        # 4. 趋势分析
        trends = self._analyze_trends(feedbacks)

        # 5. 生成建议
        recommendations = self._generate_recommendations(
            total_count, by_intent, by_sentiment, top_issues
        )

        # 6. 生成概要
        summary = self._generate_summary(
            total_count, by_channel, by_intent, by_sentiment, top_issues
        )

        return {
            "summary": summary,
            "total_count": total_count,
            "by_channel": by_channel,
            "by_intent": by_intent,
            "by_sentiment": by_sentiment,
            "top_issues": top_issues,
            "top_tags": top_tags,
            "trends": trends,
            "recommendations": recommendations,
        }

    def _count_by_field(self, items: List[dict], field: str) -> Dict[str, int]:
        """按指定字段分组计数"""
        counter = Counter()
        for item in items:
            value = item.get(field, "unknown")
            counter[value] += 1
        return dict(counter)

    def _analyze_top_issues(self, feedbacks: List[dict]) -> List[dict]:
        """
        分析热门问题
        统计投诉类反馈中的高频问题
        """
        # 筛选投诉类反馈
        complaints = [f for f in feedbacks if f.get("intent") == "complaint"]

        # 统计标签频率
        tag_counter = Counter()
        for complaint in complaints:
            tags_str = complaint.get("tags", "[]")
            if isinstance(tags_str, str):
                try:
                    import json
                    tags = json.loads(tags_str)
                except (json.JSONDecodeError, TypeError):
                    tags = []
            else:
                tags = tags_str if tags_str else []
            for tag in tags:
                tag_counter[tag] += 1

        # 返回 Top 5 问题
        top_issues = []
        for tag, count in tag_counter.most_common(5):
            top_issues.append({
                "issue": tag,
                "count": count,
                "severity": "high" if count >= 3 else "medium" if count >= 2 else "low",
            })

        return top_issues

    def _analyze_top_tags(self, feedbacks: List[dict]) -> List[dict]:
        """分析所有反馈的热门标签"""
        tag_counter = Counter()
        for fb in feedbacks:
            tags_str = fb.get("tags", "[]")
            if isinstance(tags_str, str):
                try:
                    import json
                    tags = json.loads(tags_str)
                except (json.JSONDecodeError, TypeError):
                    tags = []
            else:
                tags = tags_str if tags_str else []
            for tag in tags:
                tag_counter[tag] += 1

        top_tags = []
        for tag, count in tag_counter.most_common(10):
            top_tags.append({"tag": tag, "count": count})

        return top_tags

    def _analyze_trends(self, feedbacks: List[dict]) -> List[dict]:
        """
        分析反馈趋势
        按日期分组统计反馈数量变化
        """
        date_counter = Counter()
        for fb in feedbacks:
            created_at = fb.get("created_at", "")
            if isinstance(created_at, str):
                date_str = created_at[:10]  # 取日期部分
            elif hasattr(created_at, "strftime"):
                date_str = created_at.strftime("%Y-%m-%d")
            else:
                date_str = "unknown"
            date_counter[date_str] += 1

        trends = []
        for date, count in sorted(date_counter.items()):
            trends.append({"date": date, "count": count})

        return trends

    def _generate_recommendations(
        self, total: int, by_intent: dict, by_sentiment: dict, top_issues: list
    ) -> List[str]:
        """根据分析结果生成优化建议"""
        recommendations = []

        # 投诉占比过高
        complaint_count = by_intent.get("complaint", 0)
        if total > 0 and complaint_count / total > 0.3:
            recommendations.append("⚠️ 投诉占比较高（{:.0%}），建议重点关注产品质量和服务响应速度").format(
                complaint_count / total
            )

        # 负面情感占比
        negative_count = by_sentiment.get("negative", 0)
        if total > 0 and negative_count / total > 0.4:
            recommendations.append("⚠️ 负面情感占比偏高（{:.0%}），建议加强客户关怀和主动回访").format(
                negative_count / total
            )

        # 高频问题建议
        if top_issues:
            top_issue = top_issues[0]
            recommendations.append(f"📌 最高频问题：{top_issue['issue']}（{top_issue['count']}次），建议制定专项解决方案")

        # 一般性建议
        if total > 50:
            recommendations.append("📊 反馈量较大，建议增加客服人力配置")
        if total > 100:
            recommendations.append("📈 反馈量持续增长，建议启动客户满意度专项调研")

        if not recommendations:
            recommendations.append("✅ 当前反馈情况良好，建议持续关注")

        return recommendations

    def _generate_summary(
        self, total: int, by_channel: dict, by_intent: dict, by_sentiment: dict, top_issues: list
    ) -> str:
        """生成报告概要文字"""
        # 最活跃渠道
        top_channel = max(by_channel, key=by_channel.get) if by_channel else "无"
        top_channel_count = by_channel.get(top_channel, 0)

        # 主要意图
        top_intent = max(by_intent, key=by_intent.get) if by_intent else "无"

        # 主要情感
        top_sentiment = max(by_sentiment, key=by_sentiment.get) if by_sentiment else "无"

        summary = (
            f"共收到 {total} 条反馈，"
            f"主要来自{top_channel}渠道（{top_channel_count}条），"
            f"以{top_intent}类为主，"
            f"整体情感倾向为{top_sentiment}。"
        )

        if top_issues:
            summary += f" 高频问题包括：{'、'.join([i['issue'] for i in top_issues[:3]])}。"

        return summary
