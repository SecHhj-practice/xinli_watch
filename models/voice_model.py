import numpy as np
import librosa
import torch
import torch.nn as nn
import os
import tempfile

class VoiceEmotionModel(nn.Module):
    """语音情感识别模型（基于LSTM）"""
    
    def __init__(self, input_dim=128, hidden_dim=64, num_layers=2, num_classes=2):
        super().__init__()
        self.lstm = nn.LSTM(
            input_dim, hidden_dim, num_layers,
            batch_first=True, dropout=0.3
        )
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, num_classes)
        )
    
    def forward(self, x):
        lstm_out, (hidden, _) = self.lstm(x)
        last_hidden = hidden[-1]
        output = self.classifier(last_hidden)
        return output

def extract_mfcc(audio_path, n_mfcc=13, max_len=100):
    """
    从音频文件提取MFCC特征
    
    参数:
        audio_path: 音频文件路径
        n_mfcc: MFCC系数数量
        max_len: 最大时间步长（用于填充/截断）
    """
    try:
        # 加载音频
        y, sr = librosa.load(audio_path, sr=16000, duration=10)
        
        # 提取MFCC特征
        mfcc = librosa.feature.mfcc(
            y=y, sr=sr, n_mfcc=n_mfcc,
            n_fft=2048, hop_length=512
        )
        
        # 计算delta和delta-delta
        mfcc_delta = librosa.feature.delta(mfcc)
        mfcc_delta2 = librosa.feature.delta(mfcc, order=2)
        
        # 拼接特征 (13 + 13 + 13 = 39维)
        features = np.vstack([mfcc, mfcc_delta, mfcc_delta2])
        
        # 转置为 (time_steps, features)
        features = features.T
        
        # 填充或截断到固定长度
        if features.shape[0] < max_len:
            pad = np.zeros((max_len - features.shape[0], features.shape[1]))
            features = np.vstack([features, pad])
        else:
            features = features[:max_len, :]
        
        return features.astype(np.float32), sr
        
    except Exception as e:
        print(f"音频处理失败: {e}")
        # 返回零特征
        return np.zeros((max_len, 39), dtype=np.float32), 16000

class VoiceEmotionRecognizer:
    """语音情感识别器（演示版）"""
    
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = VoiceEmotionModel().to(self.device)
        self.model.eval()  # 演示模式，不实际训练
        
        # 简单的规则（用于演示）
        self._init_demo_params()
    
    def _init_demo_params(self):
        """初始化演示参数（模拟语音特征）"""
        # 情绪相关的语音参数
        self.negative_params = {
            'speech_rate': (80, 140),   # 语速慢
            'pitch': (100, 150),         # 音调低
            'energy': (0.02, 0.08)       # 能量低
        }
        self.positive_params = {
            'speech_rate': (160, 240),   # 语速快
            'pitch': (180, 250),         # 音调高
            'energy': (0.08, 0.20)       # 能量高
        }
    
    def _extract_audio_features(self, audio_path):
        """提取音频特征（用于规则判断）"""
        try:
            y, sr = librosa.load(audio_path, sr=16000, duration=10)
            
            # 计算语速（基于过零率估算）
            zcr = librosa.feature.zero_crossing_rate(y)[0]
            speech_rate = np.mean(zcr) * 100  # 简单估算
            
            # 计算音调（基频）
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            pitch = np.mean(pitches[pitches > 0]) if np.any(pitches > 0) else 150
            
            # 计算能量
            energy = np.mean(y**2)
            
            # 提取MFCC用于置信度
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            mfcc_mean = np.mean(mfcc)
            
            return {
                'speech_rate': min(max(int(speech_rate), 60), 300),
                'pitch': float(pitch),
                'energy': float(energy),
                'mfcc_mean': float(mfcc_mean)
            }
            
        except Exception as e:
            print(f"特征提取失败: {e}")
            return {'speech_rate': 150, 'pitch': 180, 'energy': 0.1, 'mfcc_mean': 0}
    
    def predict(self, audio_path):
        """
        预测音频的情感
        返回: {'emotion': '正常'/'需关注', 'confidence': 0.xx, 'speech_rate': xxx}
        """
        # 提取特征
        features = self._extract_audio_features(audio_path)
        
        speech_rate = features['speech_rate']
        pitch = features['pitch']
        energy = features['energy']
        
        # 规则判断
        neg_score = 0
        pos_score = 0
        
        # 语速判断
        if speech_rate < 120:
            neg_score += 0.5
        elif speech_rate > 180:
            pos_score += 0.4
        
        # 音调判断
        if pitch < 150:
            neg_score += 0.3
        elif pitch > 200:
            pos_score += 0.3
        
        # 能量判断
        if energy < 0.05:
            neg_score += 0.2
        elif energy > 0.1:
            pos_score += 0.3
        
        total = neg_score + pos_score
        if total > 0:
            neg_ratio = neg_score / total
        else:
            neg_ratio = 0.3
        
        # 判断情绪
        if neg_ratio > 0.6:
            emotion = "需关注"
            confidence = 0.65 + neg_ratio * 0.25
        elif neg_ratio > 0.4:
            emotion = "需关注"
            confidence = 0.55
        else:
            emotion = "正常"
            confidence = 0.65 + pos_score * 0.3
        
        return {
            'emotion': emotion,
            'confidence': round(min(confidence, 0.95), 3),
            'speech_rate': speech_rate,
            'pitch': round(pitch, 1),
            'energy': round(energy, 4)
        }

# 测试代码
if __name__ == "__main__":
    recognizer = VoiceEmotionRecognizer()
    print("语音模块已加载，请准备.wav文件进行测试")