class DualModalPredictor:
    """文本+语音双模态融合预测器"""
    
    def __init__(self):
        # 文本和语音的权重
        self.text_weight = 0.55
        self.voice_weight = 0.45
        
        # 预警阈值
        self.thresholds = {
            'red': 0.7,      # 紧急干预
            'yellow': 0.5,   # 心理辅导
            'blue': 0.3      # 持续关注
        }
        
        # 建议库
        self.suggestions = {
            'red': "⚠️ 紧急干预：建议立即联系心理医生或拨打心理援助热线 12356",
            'yellow': "🟡 心理辅导：建议预约心理咨询，进行专业评估",
            'blue': "🔵 持续关注：建议多关注情绪变化，保持规律作息",
            'green': "🟢 状态良好：继续保持积极心态"
        }
    
    def predict(self, text_result, voice_result):
        """
        综合文本和语音的结果进行最终预测
        
        参数:
            text_result: 文本分析结果 {'emotion': str, 'confidence': float}
            voice_result: 语音分析结果 {'emotion': str, 'confidence': float, 'speech_rate': int}
        
        返回:
            report: 综合评估报告
        """
        # 提取置信度和情绪
        text_conf = text_result.get('confidence', 0.5)
        voice_conf = voice_result.get('confidence', 0.5)
        
        # 情绪值：需关注=1，正常=0
        text_emo = 1 if text_result.get('emotion') == '需关注' else 0
        voice_emo = 1 if voice_result.get('emotion') == '需关注' else 0
        
        # 加权融合计算风险分数
        final_score = (
            text_emo * text_conf * self.text_weight +
            voice_emo * voice_conf * self.voice_weight
        )
        
        # 确保分数在0-1之间
        final_score = min(max(final_score, 0), 1)
        
        # 确定风险等级
        if final_score >= self.thresholds['red']:
            risk_level = 'red'
            risk_desc = '紧急干预'
        elif final_score >= self.thresholds['yellow']:
            risk_level = 'yellow'
            risk_desc = '心理辅导'
        elif final_score >= self.thresholds['blue']:
            risk_level = 'blue'
            risk_desc = '持续关注'
        else:
            risk_level = 'green'
            risk_desc = '状态良好'
        
        # 获取建议
        suggestion = self.suggestions[risk_level]
        
        # 添加语音详细分析
        voice_details = {}
        if 'speech_rate' in voice_result:
            voice_details['speech_rate'] = voice_result['speech_rate']
        if 'pitch' in voice_result:
            voice_details['pitch'] = voice_result['pitch']
        if 'energy' in voice_result:
            voice_details['energy'] = voice_result['energy']
        
        # 构建详细报告
        report = {
            'risk_level': risk_level,
            'risk_desc': risk_desc,
            'risk_score': round(final_score, 3),
            'suggestion': suggestion,
            'details': {
                'text': {
                    'emotion': text_result.get('emotion', '未知'),
                    'confidence': text_result.get('confidence', 0)
                },
                'voice': {
                    'emotion': voice_result.get('emotion', '未知'),
                    'confidence': voice_result.get('confidence', 0),
                    **voice_details
                }
            },
            'fusion_weights': {
                'text': self.text_weight,
                'voice': self.voice_weight
            }
        }
        
        return report
    
    def get_risk_color(self, risk_level):
        """获取风险等级对应的显示颜色"""
        colors = {
            'green': '#4CAF50',
            'blue': '#2196F3',
            'yellow': '#FFC107',
            'red': '#F44336'
        }
        return colors.get(risk_level, '#9E9E9E')
    
    def get_risk_icon(self, risk_level):
        """获取风险等级对应的图标"""
        icons = {
            'green': '🟢',
            'blue': '🔵',
            'yellow': '🟡',
            'red': '🔴'
        }
        return icons.get(risk_level, '⚪')

# 测试代码
if __name__ == "__main__":
    predictor = DualModalPredictor()
    
    # 测试用例
    test_cases = [
        ({"emotion": "需关注", "confidence": 0.85}, {"emotion": "需关注", "confidence": 0.72, "speech_rate": 120}),
        ({"emotion": "正常", "confidence": 0.90}, {"emotion": "正常", "confidence": 0.88, "speech_rate": 180}),
        ({"emotion": "需关注", "confidence": 0.60}, {"emotion": "正常", "confidence": 0.75, "speech_rate": 150}),
    ]
    
    for text_res, voice_res in test_cases:
        report = predictor.predict(text_res, voice_res)
        print(f"文本: {text_res['emotion']}, 语音: {voice_res['emotion']}")
        print(f"风险: {report['risk_icon']} {report['risk_desc']} (分数: {report['risk_score']:.2f})")
        print(f"建议: {report['suggestion']}\n")