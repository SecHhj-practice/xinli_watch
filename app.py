import streamlit as st
from user_tracker import UserTracker
from auth import login, register, init_admin
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from collections import defaultdict
from datetime import datetime, timedelta  # 添加 timedelta 用于时区转换
import random
from pdf_report import generate_report_pdf
from emotion_card import generate_emotion_card
from advice_generator import AdviceGenerator

# ---------- 页面配置 ----------
st.set_page_config(page_title="心语 · 个人空间", page_icon="🌸", layout="wide")

init_admin()

# ---------- 自定义CSS ----------
st.markdown("""
<style>
    /* ========== 全局字体与背景 ========== */
    .stApp {
        background: linear-gradient(145deg, #F9F7F5 0%, #F0EFEA 100%);
    }

    /* 保证 emoji 颜色正常 */
    h1, h2, h3, p, span, div {
        font-family: 'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji', sans-serif;
    }

    /* ========== 登录页美化 ========== */
    div[data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 32px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.05), 0 6px 12px rgba(0, 0, 0, 0.1);
        padding: 2.5rem 2rem;
        border: 1px solid rgba(255, 255, 255, 0.5);
        transition: all 0.3s ease;
    }

    /* 登录页标题 */
    .stApp h1 {
        font-size: 3.2rem !important;
        font-weight: 700;
        background: linear-gradient(135deg, #5C7A6E, #3A5A4A);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        margin-bottom: 1rem;
        text-align: center;
        letter-spacing: -0.01em;
    }

    /* 输入框圆角 */
    input, textarea, .stTextInput > div > div > input {
        border-radius: 20px !important;
        border: 1.5px solid #E0DCD5 !important;
        background: #FFFFFF !important;
        padding: 12px 18px !important;
        font-size: 1rem !important;
        transition: all 0.25s ease;
        box-shadow: inset 0 2px 5px rgba(0,0,0,0.02) !important;
    }

    input:focus, textarea:focus {
        border-color: #7C9D8E !important;
        box-shadow: 0 0 0 4px rgba(124, 157, 142, 0.2), inset 0 2px 5px rgba(0,0,0,0.02) !important;
        outline: none;
    }

    /* 移除输入框外多余白框 */
div[data-baseweb="base-input"] {
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
    outline: none !important;
}
div[data-baseweb="base-input"] > div {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
input, textarea, .stTextInput > div > div > input {
    border-radius: 20px !important;
    border: 1.5px solid #E0DCD5 !important;
    background: #FFFFFF !important;
    padding: 12px 18px !important;
    font-size: 1rem !important;
    transition: all 0.25s ease;
    box-shadow: inset 0 2px 5px rgba(0,0,0,0.02) !important;
}
input:focus, textarea:focus {
    border-color: #7C9D8E !important;
    box-shadow: 0 0 0 4px rgba(124, 157, 142, 0.2), inset 0 2px 5px rgba(0,0,0,0.02) !important;
    outline: none;
}
/* 确保 textarea 也适用 */
textarea {
    border-radius: 20px !important;
    border: 1.5px solid #E0DCD5 !important;
    background: #FFFFFF !important;
    padding: 12px 18px !important;
}

    /* 按钮统一风格 */
    button, .stButton > button {
        border-radius: 40px !important;
        border: none !important;
        background: linear-gradient(145deg, #7C9D8E, #5C7A6E) !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 12px 28px !important;
        font-size: 1.1rem !important;
        box-shadow: 0 8px 18px rgba(92, 122, 110, 0.2), 0 2px 4px rgba(0,0,0,0.05) !important;
        transition: all 0.25s ease !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        letter-spacing: 0.3px;
    }

    button:hover, .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 16px 28px rgba(92, 122, 110, 0.3), 0 4px 8px rgba(0,0,0,0.05) !important;
        background: linear-gradient(145deg, #8DB1A0, #6C8E7E) !important;
    }

    button:active, .stButton > button:active {
        transform: translateY(1px);
        box-shadow: 0 6px 12px rgba(92, 122, 110, 0.2) !important;
    }

    /* ========== 侧边栏美化 ========== */
    section[data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-right: 1px solid rgba(255,255,255,0.3);
        box-shadow: 4px 0 20px rgba(0,0,0,0.02);
    }

    .sidebar-card {
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        border-radius: 24px;
        padding: 18px 16px;
        margin-bottom: 20px;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.03), 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid rgba(255,255,255,0.6);
        transition: transform 0.2s ease;
    }

    .sidebar-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.05);
    }

    /* ========== 聊天消息气泡 ========== */
    .chat-message-user {
        background: linear-gradient(145deg, #E4EBE6, #D2DFD8);
        padding: 14px 20px;
        border-radius: 28px 28px 8px 28px;
        margin: 12px 0;
        color: #1E2A2F;
        max-width: 80%;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
        border: 1px solid rgba(255,255,255,0.5);
        font-size: 1.05rem;
        line-height: 1.5;
    }

    .chat-message-assistant {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        padding: 16px 22px;
        border-radius: 28px 28px 28px 8px;
        margin: 12px 0 20px 0;
        color: #2E3A3F;
        border-left: 6px solid #7C9D8E;
        line-height: 1.7;
        box-shadow: 0 8px 18px rgba(0, 0, 0, 0.03);
        border: 1px solid rgba(255,255,255,0.6);
    }

    /* ========== 分析结果内样式 ========== */
    .analysis-header {
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 16px;
        color: #3A5A4A;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .analysis-section {
        margin: 14px 0;
        padding: 8px 0;
    }

    .advice-box {
        background: linear-gradient(135deg, rgba(124, 157, 142, 0.08), rgba(124, 157, 142, 0.03));
        padding: 20px;
        border-radius: 24px;
        margin: 18px 0;
        border-left: 4px solid #7C9D8E;
        box-shadow: inset 0 1px 4px rgba(0,0,0,0.02);
    }

    /* ========== 风险徽章 ========== */
    .risk-badge-red { background: rgba(220, 80, 80, 0.12); color: #B13E3E; padding: 8px 16px; border-radius: 30px; text-align: center; font-weight: 700; backdrop-filter: blur(4px); }
    .risk-badge-yellow { background: rgba(255, 180, 70, 0.12); color: #C97C1E; padding: 8px 16px; border-radius: 30px; text-align: center; font-weight: 700; backdrop-filter: blur(4px); }
    .risk-badge-blue { background: rgba(70, 130, 200, 0.12); color: #2C639E; padding: 8px 16px; border-radius: 30px; text-align: center; font-weight: 700; backdrop-filter: blur(4px); }
    .risk-badge-green { background: rgba(70, 160, 120, 0.12); color: #2E7D5E; padding: 8px 16px; border-radius: 30px; text-align: center; font-weight: 700; backdrop-filter: blur(4px); }

    /* 热线卡片 */
    .hotline {
        background: linear-gradient(145deg, #7C9D8E, #5C7A6E);
        padding: 16px;
        border-radius: 24px;
        text-align: center;
        margin: 15px 0;
        color: white;
        box-shadow: 0 8px 18px rgba(92, 122, 110, 0.2);
        border: 1px solid rgba(255,255,255,0.2);
    }

    /* 固定右下角小提示 */
    .fixed-bottom-right {
        position: fixed;
        bottom: 30px;
        right: 30px;
        z-index: 999;
        background: rgba(255,255,255,0.7);
        backdrop-filter: blur(12px);
        padding: 8px 18px;
        border-radius: 40px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.08);
        font-weight: 500;
        color: #3A5A4A;
        border: 1px solid rgba(255,255,255,0.8);
    }

    /* 滚动条美化 */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(0,0,0,0.02);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(124, 157, 142, 0.3);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(124, 157, 142, 0.5);
    }
    
        /* Plotly 工具栏美化 */
    .modebar {
        background: rgba(255, 255, 255, 0.5) !important;
        backdrop-filter: blur(4px);
        border-radius: 12px !important;
        padding: 2px !important;
    }
    .modebar-btn {
        color: #3A5A4A !important;
        border-radius: 8px !important;
        transition: all 0.2s;
    }
    .modebar-btn:hover {
        background: rgba(124, 157, 142, 0.2) !important;
    }
    .modebar-group {
        border-right: 1px solid rgba(0,0,0,0.05) !important;
    }
    
</style>
""", unsafe_allow_html=True)

# ---------- 辅助函数：获取记录中的日期（修复时区）----------
def get_record_date(record):
    """兼容获取记录中的日期字段，并转换为本地时间（北京时间 UTC+8）"""
    if "date" in record:
        return record["date"]
    elif "created_at" in record:
        created_at_str = record["created_at"]
        try:
            # 假设数据库存储的是 UTC 时间
            dt_utc = datetime.strptime(created_at_str, "%Y-%m-%d %H:%M:%S")
            dt_local = dt_utc + timedelta(hours=8)  # 转换为北京时间
            return dt_local.strftime("%Y-%m-%d %H:%M:%S")
        except:
            # 如果解析失败，返回原字符串
            return created_at_str
    return ""

# ---------- 图表美化函数 ----------
def beautify_chart(fig, title=""):
    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor='center', font=dict(size=18)),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=50, b=20),
        hovermode="x unified"
    )
    fig.update_xaxes(showgrid=False, tickangle=-30)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(200,200,200,0.2)")
    return fig

# ---------- 聚合函数（仅用于图表）----------
def aggregate_by_day(records):
    """按天聚合情绪记录（仅用于图表展示）"""
    day_map = defaultdict(list)
    for r in records:
        date_str = get_record_date(r).split()[0]
        if date_str:
            day_map[date_str].append(r)

    daily_data = []
    for date_str, day_records in sorted(day_map.items()):
        emotion_counts = {"快乐":0, "平静":0, "焦虑":0, "悲伤":0, "愤怒":0}
        neg, pos = 0, 0
        for r in day_records:
            emo = r.get("primary_emotion", "平静")
            emotion_counts[emo] += 1
            if emo in ["焦虑", "悲伤", "愤怒"]:
                neg += 1
            else:
                pos += 1
        primary = max(emotion_counts, key=emotion_counts.get)
        is_bad = neg >= pos
        daily_data.append({
            "date": date_str,
            "primary_emotion": primary,
            "is_negative_day": is_bad,
            "records": day_records,
            "emotion_counts": emotion_counts,
            "negative_count": neg,
            "positive_count": pos
        })
    return daily_data

def get_risk_style(risk_level):
    if risk_level == "高风险":
        return "risk-badge-red", "🔴"
    elif risk_level == "中风险":
        return "risk-badge-yellow", "🟡"
    elif risk_level == "低风险":
        return "risk-badge-blue", "🔵"
    else:
        return "risk-badge-green", "🟢"

# ---------- 登录 ----------
if "user" not in st.session_state:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'><span style='color: #F8B4B4;'>🌸</span> 心语Agent</h1>",
                    unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["登录", "注册"])
        with tab1:
            u = st.text_input("用户名")
            p = st.text_input("密码", type="password")
            if st.button("登录", use_container_width=True):
                ok, role = login(u, p)
                if ok:
                    st.session_state.user = u
                    st.session_state.role = role
                    st.rerun()
                else:
                    st.error("用户名或密码错误")
        with tab2:
            u = st.text_input("新用户名")
            p = st.text_input("新密码", type="password")
            if st.button("注册", use_container_width=True):
                ok, msg = register(u, p)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
    st.stop()

# ---------- 初始化聊天历史 ----------
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "show_preview" not in st.session_state:
    st.session_state.show_preview = False

# ---------- Sidebar ----------
tracker = UserTracker()
records = tracker.get_user_records(st.session_state.user)

# 用于图表的按天聚合（优先使用 session_state 中的缓存，解决刷新不及时问题）
if "daily_data" in st.session_state:
    daily_data = st.session_state.daily_data
else:
    daily_data = aggregate_by_day(records) if records else []

# 从 user_tracker 获取风险评估指标（与管理后台统一）
risk_report = tracker.analyze_risk_rule_based(st.session_state.user) if records else None

if risk_report:
    consecutive_negative_days = risk_report['metrics']['consecutive_bad_days']
    risk_desc = risk_report['risk_desc']
    negative_ratio = risk_report['metrics']['negative_ratio'] / 100  # 转为小数
    worsening_trend = risk_report['metrics']['worsening_trend'] / 100
    has_crisis = risk_report['metrics']['crisis_days'] > 0
    risk_score = risk_report['risk_score']
else:
    consecutive_negative_days = 0
    risk_desc = "暂无数据"
    negative_ratio = 0
    worsening_trend = 0
    has_crisis = False
    risk_score = 0

st.sidebar.markdown("<h2 style='text-align: center; margin-bottom: 0;'>🌸 心语 · 你的情绪树洞</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; color: #6A7E77; margin-top: -5px;'>看见情绪，温柔陪伴</p>", unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.markdown(f"### 👤 欢迎，{st.session_state.user}")
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 当前风险状态")

if records and daily_data:
    risk_icon = "🔴" if "高" in risk_desc else "🟡" if "中" in risk_desc else "🔵" if "低" in risk_desc else "🟢"
    st.sidebar.markdown(f"""
    <div class="sidebar-card">
        <div style="text-align:center; margin-bottom:10px;">
            <span style="font-size:48px;">{risk_icon}</span>
        </div>
        <div class="{get_risk_style(risk_desc)[0]}">
            {risk_desc}
        </div>
        <div style="margin-top:10px; font-size:13px; text-align:center;">
            负面天数比例: {negative_ratio*100:.1f}%<br>
            连续负面天数: {consecutive_negative_days}天<br>
            ⚡ 风险分数: {risk_score*100:.1f}%
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.markdown("""
    <div class="sidebar-card" style="text-align:center;">
        <span style="font-size:48px;">📝</span><br>
        暂无足够数据
    </div>
    """, unsafe_allow_html=True)

# 风险分数计算说明（临床科学版）
with st.sidebar.expander("📖 风险分数如何计算？"):
    st.markdown("""
    **【临床标准】风险分数**

    🔴 **危机信号** → 直接 **100%风险**

    🟢 **无危机时**，综合评分公式：
    
    > **风险分数 = PHQ-9/GAD-7量表分 × 40% + 负面天数占比 × 30% + 连续负面天数 × 20% + 恶化趋势 × 10%**
    ---
    **📊 各指标含义**

    - **量表分（PHQ-9/GAD-7）**：抑郁/焦虑临床金标准，权重 **40%**
    - **负面比例**：近14天负面天数占比，权重 **30%**
    - **连续负面天数**：最近连续情绪不佳天数，权重 **20%**
    - **恶化趋势**：本周比上周变差程度，权重 **10%**
    - **危机信号**：自伤/自杀/绝望等，**出现即最高风险（100%）**
    ---
    📈 分数范围 **0 ~ 1**，**越高风险越大**。
    """)

st.sidebar.markdown("### 📞 心理援助热线")
st.sidebar.markdown("""
<div class="hotline" style="background: linear-gradient(145deg, #7FB0D4, #5C9AC0);">
    <strong>💙 全国心理援助热线</strong><br>
    <span style="font-size:24px; font-weight:bold;">12356</span>
</div>
<div class="hotline" style="background: linear-gradient(145deg, #F09B7E, #E07A5F);">
    <strong>🧡 希望24h热线</strong><br>
    <span style="font-size:18px; font-weight:bold;">400-161-9995</span>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("### 💡 使用小贴士")
st.sidebar.markdown("""
<div class="sidebar-card">
    • 每天记录心情，系统会分析你的情绪变化<br>
    • 连续记录7天以上，趋势分析更准确<br>
    • 有困扰时随时倾诉，我会温柔陪伴
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("### 🌈 今日小贴士")
tips = [
    "🌿 深呼吸三次，给自己一个安静的瞬间",
    "💧 喝一杯温水，照顾好自己的身体",
    "📖 做一件你喜欢的小事，哪怕只有5分钟",
    "🤗 允许自己今天不那么完美",
    "🌟 你已经很努力了，辛苦了",
    "🌸 情绪没有对错，接纳就是疗愈的开始"
]
st.sidebar.markdown(f"""
<div class="sidebar-card" style="text-align:center;">
    <span style="font-size:28px;">{random.choice(tips)}</span>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
if st.sidebar.button("🚪 退出登录", use_container_width=True):
    # 清除用户信息
    if "user" in st.session_state:
        del st.session_state.user
    if "role" in st.session_state:
        del st.session_state.role
    # 清空聊天历史
    st.session_state.chat_messages = []
    # 清空情绪卡片
    if "latest_card" in st.session_state:
        del st.session_state.latest_card
    if "latest_card_emotion" in st.session_state:
        del st.session_state.latest_card_emotion
    if "latest_card_quote" in st.session_state:
        del st.session_state.latest_card_quote
    # 清除 daily_data 缓存
    if "daily_data" in st.session_state:
        del st.session_state.daily_data
    st.rerun()

# ---------- 主区域 ----------
st.markdown("""
<div style="text-align:center; padding:0.5rem; margin-bottom:1rem;">
    <h1><span style='color: #6C8E7E;'>💬</span> 心语Agent · 个人空间</h1>
    <p>记录心情 · 看见情绪 · 温柔陪伴</p>
</div>
""", unsafe_allow_html=True)

# ---------- 快捷短语 ----------
st.markdown("**💬 快速表达心情**")
quick_cols = st.columns(4)
quick_phrases = {
    "😊 开心": "今天心情不错，挺开心的～",
    "😔 难过": "今天有点难过，心里闷闷的。",
    "😡 生气": "今天特别生气，感觉很不爽。",
    "😨 焦虑": "今天一直很焦虑，静不下心来。"
}
for idx, (label, phrase) in enumerate(quick_phrases.items()):
    with quick_cols[idx]:
        if st.button(label, use_container_width=True, key=f"quick_{idx}"):
            st.session_state.user_input = phrase

# ---------- 输入区域 ----------
st.markdown("---")
col_input, col_btn = st.columns([5, 1])
with col_input:
    user_input = st.text_area("", placeholder="写下你今天的心情...", key="user_input", label_visibility="collapsed", height=80)
with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📤 发送", use_container_width=True, type="primary"):
        if user_input.strip():
            st.session_state.chat_messages.append({"role": "user", "content": user_input})
            with st.spinner("🤔 正在分析你的心情..."):
                result = tracker.add_real_record(st.session_state.user, user_input)
                # 刷新记录和风险报告
                records = tracker.get_user_records(st.session_state.user)
                if records:
                    # 更新缓存的 daily_data（解决刷新不及时）
                    st.session_state.daily_data = aggregate_by_day(records)
                    
                    # 刷新风险报告（用于侧边栏）
                    risk_report = tracker.analyze_risk_rule_based(st.session_state.user)
                    if risk_report:
                        consecutive_negative_days = risk_report['metrics']['consecutive_bad_days']
                        risk_desc = risk_report['risk_desc']
                        negative_ratio = risk_report['metrics']['negative_ratio'] / 100
                        worsening_trend = risk_report['metrics']['worsening_trend'] / 100
                        has_crisis = risk_report['metrics']['crisis_days'] > 0
                        risk_score = risk_report['risk_score']
                    
                    last_record = records[0]
                    llm_detail = last_record.get("llm_detail", {})
                    
                    phq9 = last_record.get("phq9_score", "?")
                    gad7 = last_record.get("gad7_score", "?")
                    
                    analysis_detail = f"""
<div class="analysis-header">📊 情绪分析结果</div>

<div class="analysis-section">
<strong>🎭 识别情绪：</strong> {result['emotion']}
</div>

<div class="analysis-section">
<strong>🔑 关键信号：</strong><br>
{', '.join(llm_detail.get('key_signals', ['检测到情绪波动']))}
</div>

<div class="analysis-section">
<strong>📈 心理健康评估：</strong><br>
• PHQ-9（抑郁倾向评分）：{phq9}/27<br>
• GAD-7（焦虑倾向评分）：{gad7}/21
</div>

<div class="advice-box">
<strong>💝 给您的暖心建议</strong><br><br>
{result['feedback']}
</div>
"""
                    if result["warning"]:
                        analysis_detail += """
<div style="background:rgba(244,67,54,0.2); padding:12px; border-radius:12px; margin-top:10px;">
⚠️ <strong>重要提醒：</strong> 检测到危机信号，请及时联系心理援助热线 12356，你不是一个人，我们都在。
</div>
"""
                    
                    st.session_state.chat_messages.append({"role": "assistant", "content": analysis_detail})
                    # ---------- 生成情绪卡片（使用 AdviceGenerator 获取优美句子） ----------
                    from advice_generator import AdviceGenerator

                    emotion = result['emotion']

                    # 尝试从 AdviceGenerator 获取一句有文采的话
                    try:
                        advice_gen = AdviceGenerator()
                        issue_map = {
                            "快乐": "通用",
                            "平静": "通用",
                            "焦虑": "焦虑",
                            "悲伤": "抑郁",
                            "愤怒": "愤怒"
                        }
                        issue = issue_map.get(emotion, "压力")
                        warm_text = advice_gen.get_advice(issue)
                        # 提取第一行（通常是带 emoji 的暖心句子）
                        first_line = warm_text.split('\n')[0]
                        # 去掉可能存在的 emoji 前缀（如 "💬 "）
                        quote = first_line.replace("💬 ", "").strip()
                        if not quote or len(quote) < 5:
                            # 如果获取失败，回退到 LLM 推荐
                            raise ValueError("AdviceGenerator 返回为空")
                    except:
                        # 回退方案：使用 LLM 的 recommendation 或默认语句
                        last_record = records[0] if records else {}
                        llm_detail = last_record.get("llm_detail", {})
                        quote = llm_detail.get("recommendation", f"今天你感到{emotion}，记得照顾好自己。")
                        if len(quote) > 60:
                            quote = quote[:60] + "..."

                    # 生成图片并存入 session
                    try:
                        card_img = generate_emotion_card(emotion, quote)
                        st.session_state.latest_card = card_img
                        st.session_state.latest_card_emotion = emotion
                        st.session_state.latest_card_quote = quote
                    except Exception as e:
                        st.session_state.latest_card = None
                        st.warning(f"情绪卡片生成失败: {e}")
            st.rerun()
        else:
            st.warning("请先写下你的心情～")

st.markdown("""
<div class="fixed-bottom-right">
    <small style="background:#0f6efd; padding:5px 12px; border-radius:20px; color:white;">💬 随时倾诉，我在听</small>
</div>
""", unsafe_allow_html=True)

# 显示聊天历史
for msg in st.session_state.chat_messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-message-user">💬 <strong>{msg["content"]}</strong></div>', unsafe_allow_html=True)
    else:
        with st.expander("🤖 查看本次分析结果（点击收起）", expanded=True):
            st.markdown(f'<div class="chat-message-assistant" style="margin:0;">{msg["content"]}</div>', unsafe_allow_html=True)

# ---------- 展示最新情绪卡片（如果存在） ----------
if "latest_card" in st.session_state and st.session_state.latest_card is not None:
    st.markdown("---")
    st.markdown("### 🎴 你的最新情绪卡片")
    st.image(st.session_state.latest_card, caption="点击下方按钮下载保存", use_container_width=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.download_button(
            label="📥 下载情绪卡片",
            data=st.session_state.latest_card,
            file_name=f"emotion_card_{st.session_state.user}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
            mime="image/png",
            key="download_latest_card"
        )

# ---------- 情绪数据统计 ----------
st.markdown("---")
st.subheader("📊 你的情绪数据统计")

if len(daily_data) > 0:
    mapping = {"快乐":0, "平静":1, "焦虑":2, "悲伤":3, "愤怒":4}

    df_daily = pd.DataFrame([{
        "date": d["date"],
        "emotion": d["primary_emotion"]
    } for d in daily_data])
    df_daily["value"] = df_daily["emotion"].map(mapping)

    fig_daily = px.line(df_daily, x="date", y="value", markers=True, line_shape="spline")
    fig_daily.update_traces(line=dict(width=4), marker=dict(size=8))
    fig_daily.update_yaxes(tickvals=list(mapping.values()), ticktext=list(mapping.keys()))
    fig_daily = beautify_chart(fig_daily, "📈 每日情绪趋势（按天聚合）")
    config_daily = {
        'modeBarButtonsToRemove': ['zoom', 'pan', 'select', 'lasso', 'zoomIn', 'zoomOut', 'autoScale', 'resetScale'],
        'displaylogo': False,
        'toImageButtonOptions': {
            'format': 'png',
            'filename': '每日情绪趋势',
            'scale': 2
        }
    }
    st.plotly_chart(fig_daily, use_container_width=True, config=config_daily)

    
    # ---------- 实时情绪变化 ----------
    with st.expander("⏱️ 查看实时情绪变化", expanded=False):
        df_raw_list = []
        for r in records:
            date_val = get_record_date(r)
            if date_val:
                df_raw_list.append({
                    "datetime": date_val,
                    "emotion": r.get("primary_emotion", "平静")
                })
        if df_raw_list:
            df_raw = pd.DataFrame(df_raw_list)
            df_raw["value"] = df_raw["emotion"].map(mapping)
            fig_raw = px.line(df_raw, x="datetime", y="value", markers=True, line_shape="spline")
            fig_raw.update_traces(line=dict(width=2, dash="dot"), marker=dict(size=6))
            fig_raw.update_yaxes(tickvals=list(mapping.values()), ticktext=list(mapping.keys()))
            fig_raw = beautify_chart(fig_raw, "⏱️ 实时情绪变化")
            config_raw = {
                'modeBarButtonsToRemove': ['zoom', 'pan', 'select', 'lasso', 'zoomIn', 'zoomOut', 'autoScale',
                                           'resetScale'],
                'displaylogo': False,
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': '实时情绪变化',
                    'scale': 2
                }
            }
            st.plotly_chart(fig_raw, use_container_width=True, config=config_raw)
        else:
            st.write("暂无数据")

    # ---------- 情绪分布柱状图 ----------
    emotion_days = defaultdict(int)
    for d in daily_data:
        emotion_days[d["primary_emotion"]] += 1
    df_bar = pd.DataFrame({"情绪": list(emotion_days.keys()), "天数": list(emotion_days.values())})
    color_map = {"快乐":"#4CAF50", "平静":"#2196F3", "焦虑":"#FF9800", "悲伤":"#9C27B0", "愤怒":"#F44336"}
    fig_bar = px.bar(df_bar, x="情绪", y="天数", color="情绪", color_discrete_map=color_map, text="天数")
    fig_bar.update_traces(textposition="outside")
    fig_bar = beautify_chart(fig_bar, "📊 情绪分布")
    config_bar = {
        'modeBarButtonsToRemove': ['zoom', 'pan', 'select', 'lasso', 'zoomIn', 'zoomOut', 'autoScale', 'resetScale'],
        'displaylogo': False,
        'toImageButtonOptions': {
            'format': 'png',
            'filename': '情绪分布',
            'scale': 2
        }
    }
    st.plotly_chart(fig_bar, use_container_width=True, config=config_bar)
    
    # ---------- 风险指标卡片 ----------
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📊 风险等级", risk_desc)
    col2.metric("📉 负面天数比例", f"{negative_ratio*100:.1f}%")
    col3.metric("⚡ 风险分数", f" {risk_score*100:.1f}%")
    col4.metric("📅 连续负面天数", consecutive_negative_days)

    # ---------- AI自动总结 ----------
    st.markdown("### 🤖 最近情绪总结")

    last_days = daily_data[-7:]
    emotions = [d["primary_emotion"] for d in last_days]
    neg_days = sum(1 for d in last_days if d["is_negative_day"])

    if neg_days >= 4:
        trend = "最近情绪偏低，建议多休息和倾诉 💙"
    elif neg_days == 0:
        trend = "最近状态很好，继续保持 🌿"
    else:
        trend = "情绪有波动，但总体可控"

    st.markdown(f"""
    <div class="advice-box">
    最近7天情绪：{' → '.join(emotions)}<br><br>
    负面天数：{neg_days} 天<br><br>
    💡 总结：{trend}
    </div>
    """, unsafe_allow_html=True)

    # ---------- 历史记录 ----------
    with st.expander("📜 查看历史记录"):
        if daily_data:
            for day in daily_data:
                icon = "😔" if day["is_negative_day"] else "😊"
                with st.expander(f"{icon} {day['date']} ({day['primary_emotion']}) | 负面:{day['negative_count']} 正面:{day['positive_count']}"):
                    for r in day["records"]:
                        date_val = get_record_date(r)
                        time_str = date_val.split()[1] if " " in date_val else ""
                        st.write(f"🕒 {time_str} | {r['primary_emotion']} | {r['content'][:100]}")
        else:
            st.write("还没有记录")

    # ---------- 增强版PDF报告（带预览） ----------
    st.markdown("### 📄 导出心理报告")

    # 计算累计情绪统计
    total_emotion_counts = {"快乐": 0, "平静": 0, "焦虑": 0, "悲伤": 0, "愤怒": 0}
    for d in daily_data:
        for emo, count in d['emotion_counts'].items():
            total_emotion_counts[emo] += count

    report_data = {
        'risk_desc': risk_desc,
        'risk_score': risk_score,
        'negative_ratio': negative_ratio * 100,
        'worsening_trend': worsening_trend * 100,
        'consecutive_bad': consecutive_negative_days,
        'has_crisis': has_crisis,
        'emotion_counts': total_emotion_counts,
        'daily_emotions': [(d['date'], d['primary_emotion']) for d in daily_data],
        'advice': f"根据您近期的情绪数据，当前风险等级为{risk_desc}。{trend}",
        'total_days': len(daily_data),
        'total_records': len(records)
    }
    
    col_download, col_preview = st.columns(2)
    
    with col_download:
        if st.button("📥 下载PDF报告", use_container_width=True, key="download_pdf_btn"):
            try:
                pdf_buffer = generate_report_pdf(st.session_state.user, report_data)
                st.download_button(
                    label="点击下载",
                    data=pdf_buffer,
                    file_name=f"心理报告_{st.session_state.user}_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    key="download_confirm_btn"
                )
            except Exception as e:
                st.error(f"报告生成失败: {e}")
    
    with col_preview:
        if st.button("👁️ 预览报告内容", use_container_width=True, key="preview_btn"):
            st.session_state.show_preview = True
    
    if st.session_state.get('show_preview', False):
        with st.expander("📄 报告预览（点击收起）", expanded=True):
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #D6E9F8, #B0D4F0); padding: 20px; border-radius: 15px; margin: 10px 0; color: #1A2A3A;">
                <h3 style="color: #1E3A5F;">🧠 心理健康评估报告</h3>
                <hr style="border-color: #8BB8D8;">
                <p><strong>用户：</strong> {st.session_state.user}</p>
                <p><strong>生成日期：</strong> {datetime.now().strftime('%Y年%m月%d日 %H:%M')}</p>
                <p><strong>追踪周期：</strong> {len(daily_data)}天</p>
            </div>
            """, unsafe_allow_html=True)
            
            risk_color = {'高风险': '#c0392b', '中风险': '#e67e22', '低风险': '#2980b9', '正常': '#27ae60'}.get(risk_desc, '#2c3e50')
            st.markdown(f"""
            <div style="background: rgba(15,110,253,0.1); padding: 20px; border-radius: 15px; margin: 10px 0;">
                <h4>⚠️ 风险概览</h4>
                <p><strong>当前风险等级：</strong> <span style="color:{risk_color}; font-weight:bold;">{risk_desc}</span></p>
                <p><strong>风险综合评分：</strong> {risk_score:.1%}</p>
                <p><strong>负面情绪比例：</strong> {negative_ratio*100:.1f}%</p>
                <p><strong>恶化趋势：</strong> {worsening_trend*100:.1f}%</p>
                <p><strong>连续负面天数：</strong> {consecutive_negative_days}天</p>
                <p><strong>危机信号：</strong> {'有' if has_crisis else '无'}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if daily_data:
                emotion_counts = daily_data[-1]['emotion_counts']
                st.markdown(f"""
                <div style="background: rgba(15,110,253,0.05); padding: 20px; border-radius: 15px; margin: 10px 0;">
                    <h4>😊 情绪分布统计</h4>
                    <p>快乐：{emotion_counts.get('快乐', 0)}次</p>
                    <p>平静：{emotion_counts.get('平静', 0)}次</p>
                    <p>焦虑：{emotion_counts.get('焦虑', 0)}次</p>
                    <p>悲伤：{emotion_counts.get('悲伤', 0)}次</p>
                    <p>愤怒：{emotion_counts.get('愤怒', 0)}次</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="background: rgba(15,110,253,0.05); padding: 20px; border-radius: 15px; margin: 10px 0;">
                <h4>📅 近期情绪记录</h4>
            </div>
            """, unsafe_allow_html=True)
            
            for d in daily_data[-7:]:
                st.markdown(f"- {d['date']}：{d['primary_emotion']}")
            
            st.markdown(f"""
            <div style="background: rgba(15,110,253,0.1); padding: 20px; border-radius: 15px; margin: 10px 0;">
                <h4>💡 综合建议</h4>
                <p>{trend}</p>
                <p style="margin-top:10px;">根据您近期的情绪数据，当前风险等级为{risk_desc}。建议持续关注自己的情绪变化，必要时寻求专业帮助。</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.info("📞 全国心理援助热线：12356")
            
            if st.button("关闭预览", use_container_width=True, key="close_preview_btn"):
                st.session_state.show_preview = False
                st.rerun()

else:
    st.info("暂无足够记录，写下第一篇心情吧～")