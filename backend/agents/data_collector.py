"""
数据采集智能体
模拟从多个渠道（企业微信、抖音、邮件）采集客户反馈数据
所有渠道采集均为模拟数据，无需真实 API 密钥
"""

import random
from datetime import datetime
from typing import List
from pydantic import BaseModel


class FeedbackCreate(BaseModel):
    """反馈创建的数据传输对象"""
    channel: str
    content: str
    customer_name: str
    customer_contact: str


class DataCollectorAgent:
    """多渠道数据采集智能体"""

    # 模拟数据池 - 企业微信渠道
    WECOM_SAMPLES = [
        {"name": "张伟", "content": "请问你们的产品怎么退货？买了三天就不想要了", "contact": "zhangwei_wecom"},
        {"name": "李娜", "content": "你们的APP登录不了，一直显示网络错误，太烦了", "contact": "lina_wecom"},
        {"name": "王强", "content": "建议增加夜间模式功能，晚上看屏幕太刺眼了", "contact": "wangqiang_wecom"},
        {"name": "赵敏", "content": "客服态度太差了，问了三次都没人理我，要求退款！", "contact": "zhaomin_wecom"},
        {"name": "刘洋", "content": "请问会员有什么优惠？怎么开通年费会员？", "contact": "liuyang_wecom"},
        {"name": "陈静", "content": "下单后多久能发货？已经等了三天了还没动静", "contact": "chenjing_wecom"},
        {"name": "周磊", "content": "产品做工不错，包装也很好，好评！", "contact": "zhoulei_wecom"},
        {"name": "孙丽", "content": "积分怎么兑换？我有5000积分不知道怎么用", "contact": "sunli_wecom"},
    ]

    # 模拟数据池 - 抖音渠道
    DOUYIN_SAMPLES = [
        {"name": "匿名用户_8291", "content": "在你们直播间买的鞋子质量太差了，穿了一天就开胶，要求退货赔偿", "contact": "douyin_8291"},
        {"name": "甜心小公主", "content": "你们家的东西真好用，回购第三次了！推荐给闺蜜了", "contact": "douyin_txgzy"},
        {"name": "数码达人007", "content": "这个产品的续航不行啊，说好的24小时，实际用6小时就没电了", "contact": "douyin_sm007"},
        {"name": "佛系买家", "content": "希望能出一个白色款的，黑色太容易脏了", "contact": "douyin_fxbj"},
        {"name": "暴躁老哥", "content": "垃圾产品！用了两次就坏了，还不给退款，投诉！@消费者协会", "contact": "douyin_bzlg"},
        {"name": "精打细算", "content": "双十一有活动吗？上次错过了，这次想囤一些", "contact": "douyin_jdds"},
        {"name": "新手妈妈", "content": "请问你们的产品适合孕妇使用吗？成分安全吗？", "contact": "douyin_xsmm"},
        {"name": "技术宅", "content": "APP更新后闪退了，安卓12系统，已经重装还是不行", "contact": "douyin_jsz"},
    ]

    # 模拟数据池 - 邮件渠道
    EMAIL_SAMPLES = [
        {"name": "上海-张经理", "content": "你好，我是上海分公司的负责人，我们想谈一批企业采购合作，大约500台设备，请问有什么优惠政策？", "contact": "zhang_manager@company.com"},
        {"name": "深圳-李工", "content": "贵司产品接口文档有错误，API v2版本的签名算法说明与实际不一致，导致我们对接一直失败，请尽快修正", "contact": "li_engineer@tech.com"},
        {"name": "北京-王总", "content": "合作两年了，最近一批产品质量明显下降，退货率上升了30%，希望贵司重视并给出解决方案", "contact": "wang_ceo@corp.com"},
        {"name": "广州-陈小姐", "content": "我于3月15日购买的产品（订单号：GD20240315001）出现质量问题，已拍照发送，请安排退换货", "contact": "chen_miss@gz.com"},
        {"name": "杭州-赵博士", "content": "建议贵司在产品说明书中增加更多技术参数的详细说明，目前信息不够完整，影响我们做技术评估", "contact": "zhao_phd@uni.edu"},
        {"name": "成都-刘经理", "content": "请提供最新的产品目录和价格表，我们准备进行年度采购招标", "contact": "liu_mgr@cd.com"},
        {"name": "武汉-孙工", "content": "产品使用中发现安全隐患，充电时发热严重，温度超过60度，已停止使用，等待贵司回复", "contact": "sun_eng@wh.com"},
        {"name": "南京-周女士", "content": "你们的售后服务非常好，上次的问题处理得很快，给客服小王点赞！", "contact": "zhou_ms@nj.com"},
    ]

    def __init__(self):
        """初始化采集智能体"""
        self.collected_count = 0

    def collect_from_wecom(self) -> List[FeedbackCreate]:
        """
        从企业微信渠道采集反馈
        实际生产中应调用企业微信API获取客服消息
        这里使用模拟数据
        """
        # 随机选取2-3条模拟数据
        sample_count = random.randint(2, 3)
        samples = random.sample(self.WECOM_SAMPLES, min(sample_count, len(self.WECOM_SAMPLES)))

        results = []
        for sample in samples:
            feedback = FeedbackCreate(
                channel="wecom",
                content=sample["content"],
                customer_name=sample["name"],
                customer_contact=sample["contact"],
            )
            results.append(feedback)

        self.collected_count += len(results)
        return results

    def collect_from_douyin(self) -> List[FeedbackCreate]:
        """
        从抖音渠道采集反馈
        实际生产中应调用抖音开放平台API获取评论/私信
        这里使用模拟数据
        """
        sample_count = random.randint(2, 3)
        samples = random.sample(self.DOUYIN_SAMPLES, min(sample_count, len(self.DOUYIN_SAMPLES)))

        results = []
        for sample in samples:
            feedback = FeedbackCreate(
                channel="douyin",
                content=sample["content"],
                customer_name=sample["name"],
                customer_contact=sample["contact"],
            )
            results.append(feedback)

        self.collected_count += len(results)
        return results

    def collect_from_email(self) -> List[FeedbackCreate]:
        """
        从邮件渠道采集反馈
        实际生产中应连接邮箱服务器获取邮件
        这里使用模拟数据
        """
        sample_count = random.randint(2, 3)
        samples = random.sample(self.EMAIL_SAMPLES, min(sample_count, len(self.EMAIL_SAMPLES)))

        results = []
        for sample in samples:
            feedback = FeedbackCreate(
                channel="email",
                content=sample["content"],
                customer_name=sample["name"],
                customer_contact=sample["contact"],
            )
            results.append(feedback)

        self.collected_count += len(results)
        return results

    def collect_all(self) -> List[FeedbackCreate]:
        """
        从所有渠道采集反馈数据
        返回合并后的反馈列表
        """
        all_feedback = []
        all_feedback.extend(self.collect_from_wecom())
        all_feedback.extend(self.collect_from_douyin())
        all_feedback.extend(self.collect_from_email())
        return all_feedback
