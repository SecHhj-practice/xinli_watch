import torch
import torch.nn as nn
from transformers import BertTokenizer, BertForSequenceClassification
from torch.utils.data import Dataset, DataLoader
import numpy as np

class TextDataset(Dataset):
    """文本数据集类"""
    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = self.texts[idx]
        label = self.labels[idx]
        
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

class TextEmotionClassifier:
    """文本情感分类器"""
    
    def __init__(self, model_name='bert-base-chinese'):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"使用设备: {self.device}")
        
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertForSequenceClassification.from_pretrained(
            model_name, 
            num_labels=2
        ).to(self.device)
        
        # 简单的模拟数据（用于演示）
        self._init_demo_data()
    
    def _init_demo_data(self):
        """初始化演示数据（模拟已训练好的模型）"""
        # 负面情绪关键词
        self.negative_keywords = ['累', '压力', '失眠', '难过', '焦虑', '抑郁', '痛苦', '绝望', '不想', '害怕']
        # 正面情绪关键词
        self.positive_keywords = ['开心', '快乐', '幸福', '兴奋', '满足', '期待', '希望']
    
    def predict(self, text):
        """
        预测单条文本的情感
        返回: {'emotion': '正常'/'需关注', 'confidence': 0.xx}
        """
        # 简单的关键词匹配（演示用，实际应使用训练好的模型）
        text_lower = text.lower()
        
        neg_score = sum(1 for kw in self.negative_keywords if kw in text_lower)
        pos_score = sum(1 for kw in self.positive_keywords if kw in text_lower)
        
        total_score = neg_score + pos_score
        if total_score > 0:
            neg_ratio = neg_score / total_score
        else:
            neg_ratio = 0.3  # 无明显关键词时默认偏向正常
        
        # 负面词占比高 → 需关注
        if neg_ratio > 0.5:
            emotion = "需关注"
            confidence = min(0.95, 0.6 + neg_ratio * 0.3)
        else:
            emotion = "正常"
            confidence = min(0.95, 0.7 + (1 - neg_ratio) * 0.2)
        
        return {
            'emotion': emotion,
            'confidence': round(confidence, 3),
            'text': text[:100]
        }
    
    def train(self, texts, labels, epochs=3):
        """训练模型（演示版，实际应实现完整训练逻辑）"""
        print(f"训练模式：使用 {len(texts)} 条数据训练 {epochs} 轮")
        # 实际项目中，这里应该实现完整的训练循环
        # 演示版直接返回
        return self
    
    def save(self, path):
        """保存模型"""
        self.model.save_pretrained(path)
        self.tokenizer.save_pretrained(path)
        print(f"模型已保存至 {path}")
    
    def load(self, path):
        """加载模型"""
        self.model = BertForSequenceClassification.from_pretrained(path).to(self.device)
        self.tokenizer = BertTokenizer.from_pretrained(path)
        print(f"模型已从 {path} 加载")

# 测试代码
if __name__ == "__main__":
    classifier = TextEmotionClassifier()
    
    # 测试样例
    test_texts = [
        "今天心情特别好，阳光明媚",
        "最近总是失眠，压力很大，什么都不想做",
        "和朋友出去玩，很开心",
        "感觉很累，不想说话"
    ]
    
    for text in test_texts:
        result = classifier.predict(text)
        print(f"文本: {text}")
        print(f"结果: {result['emotion']} (置信度: {result['confidence']:.1%})\n")