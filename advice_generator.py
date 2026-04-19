# advice_generator.py
import random

class AdviceGenerator:
    """基于用户14天情绪数据生成个性化综合建议"""

    def __init__(self):
        # 不同问题的建议库（按系统识别出来的问题来给）
        self.advice_library = {
            '焦虑': {
                'care_words': [
                    "最近可能一直在硬撑，很多事情压在心里，已经很不容易了。",
                    "看起来最近有些神经一直绷着，可能连休息都不太踏实。",
                    "这种持续紧张和心里放不下事的状态，往往会让人很累。"
                ],
                'action': [
                    "可以先别急着解决所有问题，先做一件最小的事：深呼吸 3 次，喝点温水，给自己 5 分钟缓冲。",
                    "建议先从睡眠和身体放松入手，比如睡前 30 分钟不看手机，尝试 4-7-8 呼吸法。",
                    "如果脑子停不下来，可以把担心的事写下来，区分“今天能做的”和“暂时做不了的”。"
                ],
                'warm_support': [
                    "如果身边有人愿意陪你说说话，哪怕只是陪着，也会有帮助。",
                    "不用逼自己立刻恢复状态，先让自己慢下来就已经很重要。",
                    "先照顾好自己，不需要一下子把所有事都处理完。"
                ]
            },
            '悲伤': {
                'care_words': [
                    "最近的状态可能有点低落，做很多事都提不起劲，这种感觉会很消耗人。",
                    "如果这段时间总觉得难过、无力，说明你已经承受了不少。",
                    "有些时候不是你不想变好，而是真的很难提起能量。"
                ],
                'action': [
                    "这时候不需要给自己太大目标，先完成一件很小的事就够了，比如洗个脸、出门晒晒太阳。",
                    "可以试着保持最基本的生活节奏：按时吃饭、起床、简单活动一下。",
                    "如果不想和很多人接触，也可以先联系一个你最信任的人，发一句“我最近状态不太好”。"
                ],
                'warm_support': [
                    "你现在最需要的不是“振作起来”，而是被温柔地接住。",
                    "允许自己慢一点，不代表你没有在努力。",
                    "先活过这几天，比什么都重要。"
                ]
            },
            '愤怒': {
                'care_words': [
                    "最近可能积压了不少情绪，有些委屈或不公平的感觉一直没有被消化。",
                    "如果最近特别容易烦躁、生气，很多时候不是脾气差，而是真的太累了。",
                    "持续愤怒有时是在提醒：你心里有很多东西没有被好好看见。"
                ],
                'action': [
                    "建议先让身体降下来：离开刺激环境、喝水、慢走几分钟，先不急着回应。",
                    "如果有想说的话，可以先写下来，不急着发出去，等情绪平一点再决定。",
                    "比起压住情绪，更重要的是找到触发点：最近最让你烦的到底是什么。"
                ],
                'warm_support': [
                    "情绪本身没有错，关键是别让它伤到你自己。",
                    "你不需要永远忍着，但可以先保护好自己再处理事情。",
                    "有些愤怒，其实背后是委屈和疲惫。"
                ]
            },
            '孤独': {
                'care_words': [
                    "最近可能会有点一个人扛着的感觉，很多情绪没地方放。",
                    "孤独有时候不是身边没人，而是心里没有被理解的感觉。",
                    "如果这段时间总觉得空空的，可能说明你真的需要一点连接。"
                ],
                'action': [
                    "不用一下子恢复热闹，可以先和一个熟悉的人恢复联系，哪怕只是发一句“最近怎么样”。",
                    "建议每天给自己安排一个“和外界接触”的小动作，比如出门、买东西、和人说一句话。",
                    "如果不想深聊，也可以先去有人的地方待一会儿，让自己不要完全封闭。"
                ],
                'warm_support': [
                    "你不需要立刻变得很外向，只要慢慢重新连回世界就够了。",
                    "很多人都会有这种阶段，不代表你真的被世界丢下了。",
                    "先让自己不那么孤单，就是很重要的一步。"
                ]
            },
            '失眠': {
                'care_words': [
                    "最近如果睡不好，很多情绪都会被放大，人也更容易撑不住。",
                    "长期休息不好，本身就会让心情更难稳定。",
                    "睡眠问题往往不是“矫情”，而是身体真的在报警。"
                ],
                'action': [
                    "建议先把重点放在“睡前降速”上，比如睡前 30 分钟不刷手机、关灯、少刺激。",
                    "即使睡不好，也尽量固定起床时间，帮助身体重新建立节律。",
                    "如果脑子停不下来，可以在睡前把烦心事写下来，告诉自己“明天再处理”。"
                ],
                'warm_support': [
                    "先把睡眠稳一点，很多情绪会跟着缓下来。",
                    "不需要强迫自己马上睡着，先让身体进入休息状态就很好。",
                    "你的累，可能真的不是“想太多”，而是休息太少了。"
                ]
            },
            '压力': {
                'care_words': [
                    "最近像是一直在扛事情，心里可能已经很满了。",
                    "如果最近总觉得喘不过气，说明你承担的东西可能已经超载了。",
                    "压力太久不释放，人会慢慢变得麻木、烦躁或疲惫。"
                ],
                'action': [
                    "建议先别想着一次处理完所有事，可以只选今天最重要的一件先做。",
                    "把脑子里的事写下来，很多时候压力来自“太多东西都在脑子里转”。",
                    "如果最近一直在撑，给自己安排一点固定的放松时间，不要等彻底崩了才休息。"
                ],
                'warm_support': [
                    "你不是不够努力，而是可能真的太久没有喘口气了。",
                    "先减一点负担，比继续硬撑更重要。",
                    "照顾好自己，不是偷懒，是为了能继续走下去。"
                ]
            }
        }

        self.general_support = [
            "如果最近状态持续变差，别一个人硬撑，及时找人聊聊会更安全。",
            "情绪问题很多时候不是“矫情”，而是身体和心理都在提醒你需要照顾自己了。",
            "先把状态稳住，比逼自己立刻变好更重要。"
        ]

    # ========== 新增：简单版 get_advice 方法，供按钮调用 ==========
    def get_advice(self, issue, context=""):
        """根据具体问题生成针对性建议（简单版，供按钮调用）"""
        issue_map = {
            '焦虑': '焦虑',
            '失眠': '失眠',
            '压力': '压力',
            '抑郁': '悲伤',
            '愤怒': '愤怒',
            '孤独': '孤独',
            '通用': '压力'
        }
        
        mapped_issue = issue_map.get(issue, '压力')
        
        if mapped_issue in self.advice_library:
            lib = self.advice_library[mapped_issue]
            advice_parts = []
            
            if 'care_words' in lib:
                advice_parts.append(f"💬 {random.choice(lib['care_words'])}")
            if 'action' in lib:
                advice_parts.append(f"\n📋 **建议**：{random.choice(lib['action'])}")
            if 'warm_support' in lib:
                advice_parts.append(f"\n💝 **支持**：{random.choice(lib['warm_support'])}")
            
            return "\n\n".join(advice_parts)
        else:
            return "💬 建议保持规律作息，适当运动，如有需要可以联系心理援助热线 12356"

    # ========== 原有：个性化综合建议方法 ==========
    def get_personalized_advice(
        self,
        user_name,
        emotion_counts,
        metrics,
        risk_level,
        weekly_comparison=None,
        recent_contents=None
    ):
        """
        根据用户综合数据生成个性化建议
        """
        weekly_comparison = weekly_comparison or {}
        recent_contents = recent_contents or []

        # 找主要问题
        negative_emotions = {
            '焦虑': emotion_counts.get('焦虑', 0),
            '悲伤': emotion_counts.get('悲伤', 0),
            '愤怒': emotion_counts.get('愤怒', 0)
        }

        main_issue = max(negative_emotions, key=negative_emotions.get) if max(negative_emotions.values()) > 0 else None

        # 根据 recent_contents 做补充识别
        recent_text = " ".join(recent_contents)

        if ("失眠" in recent_text or "睡不着" in recent_text) and main_issue in ['焦虑', '悲伤']:
            secondary_issue = "失眠"
        elif ("压力" in recent_text or "好累" in recent_text or "停不下来" in recent_text):
            secondary_issue = "压力"
        elif ("孤独" in recent_text or "没人理解" in recent_text):
            secondary_issue = "孤独"
        else:
            secondary_issue = None

        negative_ratio = metrics.get('negative_ratio', 0)
        worsening = metrics.get('worsening_trend', 0)
        consecutive_bad = metrics.get('consecutive_bad_days', 0)
        crisis_days = metrics.get('crisis_days', 0)

        if risk_level == 'red':
            risk_title = f"🔴 {user_name} 当前处于高风险状态"
            risk_intro = (
                f"近两周负面情绪比例达到 **{negative_ratio}%**，"
                f"并且连续 **{consecutive_bad} 天** 情绪不佳。"
            )
        elif risk_level == 'yellow':
            risk_title = f"🟡 {user_name} 近期需要重点关注"
            risk_intro = (
                f"近两周负面情绪比例为 **{negative_ratio}%**，"
                f"情绪状态较前一周有一定恶化。"
            )
        elif risk_level == 'blue':
            risk_title = f"🔵 {user_name} 情绪有一定波动"
            risk_intro = (
                f"近两周情绪整体可控，但存在一定起伏，"
                f"建议适度留意和陪伴。"
            )
        else:
            risk_title = f"🟢 {user_name} 当前整体状态稳定"
            risk_intro = (
                f"近两周整体情绪较平稳，当前风险较低，"
                f"建议继续保持日常连接与关注。"
            )

        care_part = ""
        action_part = ""
        support_part = ""

        if main_issue and main_issue in self.advice_library:
            care_part = random.choice(self.advice_library[main_issue]['care_words'])
            action_part = random.choice(self.advice_library[main_issue]['action'])
            support_part = random.choice(self.advice_library[main_issue]['warm_support'])

        secondary_part = ""
        if secondary_issue and secondary_issue in self.advice_library:
            secondary_part = f"\n\n**额外关注点：{secondary_issue}**\n{random.choice(self.advice_library[secondary_issue]['action'])}"

        trend_part = ""
        if worsening > 20:
            trend_part += "\n\n📈 **趋势提醒**：最近一周明显比前一周更吃力，说明状态正在往下走，建议尽早干预。"
        if consecutive_bad >= 4:
            trend_part += f"\n\n📅 **连续低落提醒**：已经连续 {consecutive_bad} 天处于负面状态，这通常意味着仅靠“熬过去”不太够了。"
        if crisis_days > 0:
            trend_part += "\n\n⚠️ **危机提醒**：近期出现过明显危机信号，建议务必优先保证现实支持和安全陪伴。"

        extra_action = ""
        if risk_level == 'red':
            extra_action = (
                "\n\n**建议优先行动：**\n"
                "1. 主动联系，先表达关心，而不是立刻讲道理\n"
                "2. 优先确认最近有没有失眠、崩溃、强烈无助感\n"
                "3. 如果对方出现“活着没意思 / 不想活”等表达，建议立即联系专业援助（12356）"
            )
        elif risk_level == 'yellow':
            extra_action = (
                "\n\n**建议陪伴方式：**\n"
                "- 可以先从一句轻一点的关心开始，比如：「最近是不是有点累？」\n"
                "- 不急着给建议，先让对方把话说出来\n"
                "- 比起“你应该…”，更适合说“我在”"
            )
        elif risk_level == 'blue':
            extra_action = (
                "\n\n**建议互动方式：**\n"
                "- 保持正常联系，不必突然过度干预\n"
                "- 可以适当邀请散步、吃饭、聊天，帮助情绪回稳"
            )
        else:
            extra_action = (
                "\n\n**建议保持：**\n"
                "- 继续维持正常连接和交流\n"
                "- 偶尔关心、分享轻松内容即可"
            )

        final_advice = f"""
{risk_title}

{risk_intro}

**当前更需要被看见的是：**  
{care_part if care_part else "近期状态整体稳定，建议继续保持观察和连接。"}

**更实用的下一步建议：**  
{action_part if action_part else "继续保持规律生活和正常社交连接。"}

**更温柔的一句提醒：**  
{support_part if support_part else random.choice(self.general_support)}

{secondary_part}
{trend_part}
{extra_action}
"""

        return final_advice.strip()


# 测试
if __name__ == "__main__":
    generator = AdviceGenerator()
    
    print("=== 按钮调用测试 ===")
    print(generator.get_advice('焦虑'))
    
    print("\n=== 个性化建议测试 ===")
    advice = generator.get_personalized_advice(
        user_name="小明",
        emotion_counts={'快乐': 2, '平静': 1, '焦虑': 8, '悲伤': 2, '愤怒': 1},
        metrics={'negative_ratio': 71.4, 'worsening_trend': 15, 'consecutive_bad_days': 5, 'crisis_days': 0},
        risk_level='yellow',
        weekly_comparison={'week1_negative': 50, 'week2_negative': 65},
        recent_contents=["最近总是失眠，压力很大", "焦虑得不行", "不想说话"]
    )
    print(advice)