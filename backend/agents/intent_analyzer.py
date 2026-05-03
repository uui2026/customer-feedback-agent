"""
意图分析智能体
基于中文关键词匹配实现意图分类和情感分析
无需外部 NLP 服务，纯规则引擎
"""

import json
from typing import Tuple, List


class IntentAnalyzerAgent:
    """意图与情感分析智能体"""

    # 投诉类关键词 - 包含这些词大概率为投诉
    COMPLAINT_KEYWORDS = [
        "投诉", "退款", "退货", "赔偿", "垃圾", "差评", "不满", "生气",
        "愤怒", "骗人", "欺骗", "虚假", "太差", "太烂", "骗", "坑",
        "举报", "曝光", "欺诈", "态度差", "不给退", "不理人", "没人管",
        "严重", "失望", "糟糕", "恶心", "受骗", "上当", "举报",
        "开胶", "坏了", "质量问题", "安全隐患", "发热", "爆炸",
        "没人理", "不理我", "无语", "受不了", "忍无可忍",
    ]

    # 建议类关键词 - 包含这些词大概率为建议
    SUGGESTION_KEYWORDS = [
        "建议", "希望", "能不能", "可以吗", "最好", "优化", "改进",
        "功能", "增加", "添加", "改进", "升级", "体验", "改善",
        "如果能", "要是能", "完善", "提升", "推荐", "出一个",
        "新功能", "新增", "需求", "期望", "更好的",
    ]

    # 正面情感关键词
    POSITIVE_KEYWORDS = [
        "好", "棒", "赞", "不错", "满意", "喜欢", "优秀", "推荐",
        "好评", "感谢", "谢谢", "太好了", "完美", "出色", "惊艳",
        "物超所值", "回购", "支持", "点赞", "打call", "真好",
        "很好", "非常好", "特别好", "太棒了", "良心",
    ]

    # 负面情感关键词
    NEGATIVE_KEYWORDS = [
        "差", "烂", "垃圾", "失望", "不满", "生气", "愤怒", "烦",
        "差评", "讨厌", "无语", "恶心", "难受", "坑", "骗",
        "太差", "很烂", "受不了", "忍不了", "差劲", "不行",
        "坏", "假", "虚", "劣质", "低劣", "投诉", "退款",
    ]

    # 标签关键词映射 - 用于提取反馈标签
    TAG_MAPPING = {
        "退款": ["退款", "退钱", "退费", "返还"],
        "售后": ["售后", "退换货", "维修", "保养"],
        "产品质量": ["质量", "做工", "材料", "做工差", "开胶", "损坏"],
        "物流": ["物流", "发货", "快递", "配送", "运输", "等了"],
        "客服态度": ["态度", "客服", "服务态度", "没人理"],
        "技术问题": ["bug", "故障", "崩溃", "报错", "闪退", "打不开", "登录"],
        "功能建议": ["功能", "建议", "希望", "增加", "优化", "改进"],
        "会员权益": ["会员", "积分", "优惠", "折扣", "权益"],
        "活动": ["活动", "促销", "双十一", "618", "优惠券"],
        "安全问题": ["安全", "隐患", "发热", "隐私", "泄露"],
        "企业合作": ["合作", "采购", "批量", "企业", "招标"],
        "使用咨询": ["怎么", "如何", "请问", "咨询", "了解"],
        "表扬": ["表扬", "点赞", "好评", "感谢", "谢谢", "服务好"],
    }

    def analyze(self, text: str) -> dict:
        """
        分析文本的意图、情感和标签

        参数:
            text: 待分析的文本内容

        返回:
            {
                "intent": "complaint|inquiry|suggestion",
                "sentiment": "positive|negative|neutral",
                "tags": ["标签1", "标签2"]
            }
        """
        # 转小写以便匹配（处理英文关键词）
        text_lower = text.lower()

        # 1. 意图分析 - 基于关键词匹配
        intent = self._detect_intent(text_lower)

        # 2. 情感分析 - 基于情感词匹配
        sentiment = self._detect_sentiment(text_lower)

        # 3. 标签提取 - 基于标签关键词映射
        tags = self._extract_tags(text_lower)

        return {
            "intent": intent,
            "sentiment": sentiment,
            "tags": tags,
        }

    def _detect_intent(self, text: str) -> str:
        """
        意图检测
        计算各类意图的关键词匹配得分，取最高分的意图
        默认为咨询类
        """
        complaint_score = sum(1 for kw in self.COMPLAINT_KEYWORDS if kw in text)
        suggestion_score = sum(1 for kw in self.SUGGESTION_KEYWORDS if kw in text)

        if complaint_score > suggestion_score and complaint_score > 0:
            return "complaint"
        elif suggestion_score > 0:
            return "suggestion"
        else:
            return "inquiry"

    def _detect_sentiment(self, text: str) -> str:
        """
        情感检测
        正面词加分，负面词减分，最终判断情感倾向
        """
        positive_count = sum(1 for kw in self.POSITIVE_KEYWORDS if kw in text)
        negative_count = sum(1 for kw in self.NEGATIVE_KEYWORDS if kw in text)

        # 计算净情感分数
        score = positive_count - negative_count

        if score > 0:
            return "positive"
        elif score < 0:
            return "negative"
        else:
            return "neutral"

    def _extract_tags(self, text: str) -> List[str]:
        """
        标签提取
        遍历标签关键词映射，匹配到的标签加入列表
        最多返回5个标签
        """
        tags = []
        for tag, keywords in self.TAG_MAPPING.items():
            if any(kw in text for kw in keywords):
                tags.append(tag)

        # 限制最多5个标签
        return tags[:5] if tags else ["其他"]
