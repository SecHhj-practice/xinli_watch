import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class LLMPredictor:
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("请在.env文件中设置 DEEPSEEK_API_KEY")
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )

    def predict_emotion(self, user_text: str, history_records: list = None):
        """
        分析用户文本，返回情绪分类及详细预警信息。
        输出JSON格式：
        {
            "primary_emotion": "快乐/平静/焦虑/悲伤/愤怒",
            "is_negative": true/false,
            "is_crisis": true/false,
            "confidence": 0.0~1.0,
            "phq9_score": 0-27,
            "gad7_score": 0-21,
            "key_signals": ["信号1", "信号2"],
            "recommendation": "简短建议（30字以内）"
        }
        """
        # 处理历史记录（可选）
        context = ""
        if history_records:
            recent_texts = [r.get('content', '') for r in history_records[-3:]]
            context = "用户近几天的表达：\n" + "\n".join(recent_texts) + "\n\n"

        system_prompt = """你是一位专业的心理健康评估助手。
你的任务是分析用户的日常表达，判断其情绪状态和心理风险。
请严格按照以下JSON格式输出结果，不要包含其他内容：
{
    "primary_emotion": "快乐/平静/焦虑/悲伤/愤怒",
    "is_negative": true/false,
    "is_crisis": true/false,
    "confidence": 0.0~1.0,
    "phq9_score": 0-27,
    "gad7_score": 0-21,
    "key_signals": ["信号1", "信号2"],
    "recommendation": "简短建议（30字以内）"
}

判断规则：
- primary_emotion 必须且只能是五种情绪之一。
- is_negative 为 true 当且仅当 primary_emotion 是焦虑、悲伤或愤怒。
- is_crisis 为 true 当且仅当用户表达了自杀、自伤、绝望、不想活等极端内容。
- key_signals 列出文本中最能体现情绪的关键词或短语（2-3个）。
- recommendation 给出温暖、鼓励且专业的简短建议。"""

        user_prompt = f"""请分析以下用户发言：
{context}用户最新发言："{user_text}"
请严格按照JSON格式输出。"""

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            # 确保字段完整
            required_keys = ["primary_emotion", "is_negative", "is_crisis", "confidence",
                             "phq9_score", "gad7_score", "key_signals", "recommendation"]
            for k in required_keys:
                if k not in result:
                    result[k] = None
            return result
        except Exception as e:
            # 出错时返回一个安全的默认值（保守策略：判定为平静）
            return {
                "primary_emotion": "平静",
                "is_negative": False,
                "is_crisis": False,
                "confidence": 0.0,
                "phq9_score": 0,
                "gad7_score": 0,
                "key_signals": ["API调用失败"],
                "recommendation": "服务暂时不可用，请稍后再试。"
            }