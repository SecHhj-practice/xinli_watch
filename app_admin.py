import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from user_tracker import UserTracker
from auth import login, init_admin
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="心语 · 管理后台", page_icon="📊", layout="wide")

init_admin()

# 管理员专用登录
if "admin_user" not in st.session_state:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #D6E9F8, #B0D4F0); padding:2rem; border-radius:28px; text-align:center; box-shadow: 0 8px 20px rgba(0,0,0,0.05);">
        <h2 style="color: #1E3A5F; margin:0;">🔐 管理后台登录</h2>
        </div>
        """, unsafe_allow_html=True)
        u = st.text_input("用户名")
        p = st.text_input("密码", type="password")
        if st.button("登录"):
            ok, role = login(u, p)
            if ok and role == "admin":
                st.session_state.admin_user = u
                st.rerun()
            else:
                st.error("仅限管理员访问")
        st.stop()

st.sidebar.markdown(f"### 👑 管理员：{st.session_state.admin_user}")
if st.sidebar.button("退出"):
    del st.session_state.admin_user
    st.rerun()

# 加载所有用户数据
tracker = UserTracker()
all_reports = tracker.get_all_user_reports()

# 标题
st.markdown("""
<style>
    /* 全局背景 */
    .stApp {
        background: linear-gradient(145deg, #F4F7F5, #EAEEE9);
    }

    /* 管理端头部卡片 */
    .admin-header {
        background: linear-gradient(105deg, #2C4A3E 0%, #3D5F50 100%);
        padding: 2rem 2.5rem;
        border-radius: 36px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 20px 30px rgba(44, 74, 62, 0.15);
        border: 1px solid rgba(255,255,255,0.1);
    }

    /* 卡片容器 */
    div[data-testid="stExpander"] {
        background: rgba(255,255,255,0.7);
        backdrop-filter: blur(8px);
        border-radius: 24px !important;
        border: 1px solid rgba(255,255,255,0.5) !important;
        box-shadow: 0 8px 20px rgba(0,0,0,0.03) !important;
        margin-bottom: 1rem !important;
    }

    /* 表格美化 */
    .stDataFrame {
        border-radius: 20px !important;
        overflow: hidden;
        box-shadow: 0 4px 14px rgba(0,0,0,0.03);
    }

    /* 侧边栏 */
    section[data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(16px);
    }

    /* 按钮 */
    button, .stButton > button {
        border-radius: 40px !important;
        background: #5C7A6E !important;
        color: white !important;
        border: none !important;
        font-weight: 600;
        transition: all 0.2s;
    }
    button:hover {
        background: #6C8E7E !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(92, 122, 110, 0.3);
    }

    /* 指标卡片 */
    div[data-testid="metric-container"] {
        background: rgba(255,255,255,0.7);
        backdrop-filter: blur(8px);
        border-radius: 24px;
        padding: 8px;
        border: 1px solid rgba(255,255,255,0.5);
        box-shadow: 0 6px 14px rgba(0,0,0,0.02);
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<p style='text-align: center; color: #4A6A5C; margin-top: -10px; margin-bottom: 20px;'>🌸 心语 · 管理后台 | 温柔守护每一份情绪</p>", unsafe_allow_html=True)

# 顶部统计卡片
total_users = len(all_reports)
high_risk = sum(1 for r in all_reports if r["risk_level"] in ["red", "yellow"])
avg_negative = sum(r["metrics"]["negative_ratio"] for r in all_reports) / total_users if total_users else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("👥 总用户数", total_users)
col2.metric("⚠️ 需关注用户", high_risk, delta=f"{(high_risk/total_users*100):.0f}%" if total_users else "0")
col3.metric("📉 平均负面比例", f"{avg_negative:.1f}%")
col4.metric("📅 近14天追踪", "动态更新")

# 风险分组展示（类似代码一）
st.markdown("---")
st.subheader("🔍 用户风险分类")

def make_table(users):
    rows = []
    for u in users:
        rows.append({
            "用户": u["user_name"],
            "负面比例": f"{u['metrics']['negative_ratio']}%",
            "恶化趋势": f"{u['metrics']['worsening_trend']}%",
            "连续负面天数": f"{u['metrics']['consecutive_bad_days']}天",
            "风险分数": f"{u['risk_score']:.0%}"
        })
    return pd.DataFrame(rows)

red = [r for r in all_reports if r["risk_level"] == "red"]
yellow = [r for r in all_reports if r["risk_level"] == "yellow"]
blue = [r for r in all_reports if r["risk_level"] == "blue"]
green = [r for r in all_reports if r["risk_level"] == "green"]

if red:
    with st.expander(f"🔴 高风险用户 ({len(red)}) - 建议立即关注", expanded=True):
        st.dataframe(make_table(red), use_container_width=True)
if yellow:
    with st.expander(f"🟡 中风险用户 ({len(yellow)}) - 需要关注", expanded=False):
        st.dataframe(make_table(yellow), use_container_width=True)
if blue:
    with st.expander(f"🔵 低风险用户 ({len(blue)}) - 可留意", expanded=False):
        st.dataframe(make_table(blue), use_container_width=True)
if green:
    with st.expander(f"🟢 正常用户 ({len(green)})", expanded=False):
        st.dataframe(make_table(green), use_container_width=True)

# 全局概览表
st.markdown("---")
st.subheader("📋 所有用户风险概览")
overview = []
for r in all_reports:
    icon = {"red":"🔴","yellow":"🟡","blue":"🔵","green":"🟢"}[r["risk_level"]]
    overview.append({
        "用户": f"{icon} {r['user_name']}",
        "风险等级": r["risk_desc"],
        "负面比例": f"{r['metrics']['negative_ratio']}%",
        "恶化趋势": f"{r['metrics']['worsening_trend']}%",
        "连续负面天数": f"{r['metrics']['consecutive_bad_days']}天"
    })
st.dataframe(pd.DataFrame(overview), use_container_width=True, height=400)

# ---------- 导出 Excel ----------
st.markdown("---")
st.subheader("📤 数据导出")
if st.button("📊 导出全部用户数据为 Excel"):
    # 准备导出数据
    export_data = []
    for r in all_reports:
        export_data.append({
            "用户名": r["user_name"],
            "风险等级": r["risk_desc"],
            "风险分数": f"{r['risk_score'] * 100:.1f}%",
            "负面比例": f"{r['metrics']['negative_ratio']:.1f}%",
            "恶化趋势": f"{r['metrics']['worsening_trend']:.1f}%",
            "连续负面天数": f"{r['metrics']['consecutive_bad_days']}天",
            "危机信号": "有" if r['metrics']['crisis_days'] > 0 else "无",
            "快乐次数": r["emotion_counts"].get("快乐", 0),
            "平静次数": r["emotion_counts"].get("平静", 0),
            "焦虑次数": r["emotion_counts"].get("焦虑", 0),
            "悲伤次数": r["emotion_counts"].get("悲伤", 0),
            "愤怒次数": r["emotion_counts"].get("愤怒", 0)
        })
    df_export = pd.DataFrame(export_data)

    # 转为 Excel
    from io import BytesIO

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_export.to_excel(writer, index=False, sheet_name='用户风险数据')
    output.seek(0)

    st.download_button(
        label="📥 点击下载 Excel 文件",
        data=output,
        file_name=f"用户心理健康数据_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="export_excel_btn"
    )
    st.success("Excel 文件已生成，点击上方按钮下载。")

# 用户详情搜索（模仿代码一）
st.markdown("---")
st.subheader("🔎 查看用户详情")
search = st.text_input("输入用户名搜索")
if search:
    matched = [r for r in all_reports if search.lower() in r["user_name"].lower()]
    if matched:
        selected = st.selectbox("选择用户", [r["user_name"] for r in matched])
        report = next(r for r in matched if r["user_name"] == selected)
        # 展示该用户的详细图表
        st.markdown(f"### 📈 {selected} 的情绪分析")
        df_daily = pd.DataFrame(report["daily_emotions"], columns=["日期", "情绪"])
        emo_map = {"快乐":0,"平静":1,"焦虑":2,"悲伤":3,"愤怒":4}
        df_daily["值"] = df_daily["情绪"].map(emo_map)
        fig = px.line(df_daily, x="日期", y="值", markers=True, title="情绪变化趋势")
        fig.update_yaxes(tickvals=[0,1,2,3,4], ticktext=["快乐","平静","焦虑","悲伤","愤怒"])
        st.plotly_chart(fig, use_container_width=True)

        # 情绪分布柱状图
        emo_counts = report["emotion_counts"]
        df_bar = pd.DataFrame({"情绪": list(emo_counts.keys()), "次数": list(emo_counts.values())})
        fig_bar = px.bar(df_bar, x="情绪", y="次数", color="情绪", title="情绪分布")
        st.plotly_chart(fig_bar, use_container_width=True)

        # 规则建议
        st.info(report["advice"])
        # ---------- 模拟发送关怀 ----------
        st.markdown("---")
        col_care1, col_care2 = st.columns([3, 1])
        with col_care1:
            st.markdown("#### 💌 发送关怀提醒")
        with col_care2:
            if st.button("📨 发送关怀", key=f"care_{selected}"):
                # 记录日志（存为 CSV 或显示成功提示）
                import csv
                import os
                log_file = "care_log.csv"
                log_entry = {
                    "时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "管理员": st.session_state.admin_user,
                    "目标用户": selected,
                    "操作": "发送关怀提醒"
                }
                file_exists = os.path.isfile(log_file)
                with open(log_file, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=["时间", "管理员", "目标用户", "操作"])
                    if not file_exists:
                        writer.writeheader()
                    writer.writerow(log_entry)
                st.success(f"✅ 已向 {selected} 发送关怀提醒（已记录日志）")
                st.balloons()
    else:
        st.warning("未找到用户")            