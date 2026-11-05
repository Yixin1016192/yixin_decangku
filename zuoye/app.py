# -*- coding: utf-8 -*-
"""智能数据分析智能体 —— Streamlit 主程序。

运行方式：
    streamlit run app.py
"""
import json
import os
from pathlib import Path

import pandas as pd
import streamlit as st

from core import agent, analyzer, charts, data_loader, report as report_mod

st.set_page_config(page_title="智能数据分析智能体", page_icon="🤖", layout="wide")

BASE_DIR = Path(__file__).resolve().parent
SAMPLE_DATA = BASE_DIR / "示例数据" / "电商销售数据.csv"

# ---------------------------------------------------------------- 会话状态
if "df" not in st.session_state:
    st.session_state.df = None
if "df_name" not in st.session_state:
    st.session_state.df_name = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "trace" not in st.session_state:
    st.session_state.trace = []
if "conclusion" not in st.session_state:
    st.session_state.conclusion = ""


def get_client():
    """按当前配置创建大模型客户端；未配置 Key 返回 None。"""
    key = st.session_state.get("api_key", "").strip()
    if not key:
        return None
    return agent.make_client(key, st.session_state.get("base_url", "https://api.deepseek.com"))


# ---------------------------------------------------------------- 侧边栏
with st.sidebar:
    st.title("🤖 智能数据分析智能体")
    st.caption("基于大模型 API 与工具调用的自动数据分析系统")

    with st.expander("🔑 大模型 API 设置", expanded=True):
        st.session_state.api_key = st.text_input(
            "API Key", type="password", value=st.session_state.get("api_key", ""),
            help="DeepSeek 开放平台（platform.deepseek.com）申请；也支持任意 OpenAI 兼容接口")
        st.session_state.base_url = st.text_input(
            "Base URL", value=st.session_state.get("base_url", "https://api.deepseek.com"))
        st.session_state.model = st.text_input(
            "模型", value=st.session_state.get("model", "deepseek-chat"))
        if st.button("测试连接", width="stretch"):
            client = get_client()
            if client is None:
                st.warning("请先填写 API Key")
            else:
                try:
                    resp = client.chat.completions.create(
                        model=st.session_state.model,
                        messages=[{"role": "user", "content": "你好，请回复：连接成功"}],
                        max_tokens=20)
                    st.success("✅ " + resp.choices[0].message.content)
                except Exception as e:  # noqa: BLE001
                    st.error(f"连接失败：{e}")

    with st.expander("📁 数据源", expanded=True):
        st.caption("上传 CSV / Excel 文件，或使用内置示例数据")
        uploaded = st.file_uploader("选择数据文件", type=["csv", "txt", "xlsx", "xls"])
        if uploaded is not None:
            try:
                df_new = data_loader.load_file(uploaded.getvalue(), uploaded.name)
                if st.session_state.df is None or st.session_state.df_name != uploaded.name:
                    st.session_state.df = df_new
                    st.session_state.df_name = uploaded.name
                    st.session_state.chat_history = []
                    st.session_state.conclusion = ""
                    st.success(f"已加载 {uploaded.name}（{len(df_new)} 行 × {df_new.shape[1]} 列）")
                else:
                    st.info("数据已加载")
            except Exception as e:  # noqa: BLE001
                st.error(f"文件解析失败：{e}")
        if st.button("📦 使用内置示例数据（电商销售）", width="stretch"):
            df_new = pd.read_csv(SAMPLE_DATA, encoding="utf-8-sig")
            st.session_state.df = df_new
            st.session_state.df_name = "电商销售数据.csv（示例）"
            st.session_state.chat_history = []
            st.session_state.conclusion = ""
            st.success(f"已加载示例数据（{len(df_new)} 行 × {df_new.shape[1]} 列）")

    st.divider()
    st.caption("《人工智能导论》期末课程设计\n\n大数据管理与应用 26-3 班　261560305 佟宇鑫")

# ---------------------------------------------------------------- 主体
df = st.session_state.df

if df is None:
    st.markdown("""
## 👋 欢迎使用智能数据分析智能体

本系统将 **大模型 API 与 Function Calling（工具调用）** 相结合，实现"**上传表格 → 自动分析 → 图表可视化 → AI 解读 → 对话式问数 → 报告导出**"的完整数据分析流程。

### 🚀 三步开始
1. 在左侧填写 **DeepSeek API Key**（不填也可以使用除"对话式问数"外的全部功能）；
2. 上传 CSV / Excel 数据文件，或点击"使用内置示例数据"；
3. 依次体验 **一键自动分析 → 智能图表 → AI 分析结论 → 对话式问数**。

### ✨ 核心能力
| 能力 | 说明 |
| --- | --- |
| 📊 自动 EDA | 描述统计、缺失值/重复值检测、字段类型自动识别 |
| 📈 智能图表 | 按字段类型自动选择直方图/箱线图/饼图/趋势图/热力图等交互图表 |
| 🤖 AI 解读 | 大模型把统计结果翻译成通俗结论与业务建议 |
| 💬 对话式问数 | 自然语言提问，AI Agent 自主选择分析工具并汇总回答（多轮对话） |
| 📄 报告导出 | 一键生成 Markdown / HTML 分析报告 |
""")
    st.stop()

st.subheader(f"📁 当前数据：{st.session_state.df_name}")
st.caption(f"{len(df)} 行 × {df.shape[1]} 列")

tab_data, tab_eda, tab_chart, tab_ai, tab_chat, tab_export = st.tabs(
    ["📤 数据预览", "📊 一键自动分析", "📈 智能图表", "🤖 AI 分析结论", "💬 对话式问数", "📄 报告导出"])

# ================================================================ Tab 1
with tab_data:
    st.write("**数据前 50 行预览**")
    st.dataframe(df.head(50), width="stretch")
    ov = analyzer.classify_columns(df)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("总行数", f"{len(df):,}")
    c2.metric("字段数", df.shape[1])
    c3.metric("数值型字段", len(ov["numeric"]))
    c4.metric("分类型字段", len(ov["categorical"]))
    st.write("**字段类型识别结果**")
    st.write(f"数值型：{'、'.join(ov['numeric']) or '无'}")
    st.write(f"分类型：{'、'.join(ov['categorical']) or '无'}")
    st.write(f"日期型：{'、'.join(ov['datetime']) or '无'}")
    st.write(f"文本型：{'、'.join(ov['text']) or '无'}")

# ================================================================ Tab 2
with tab_eda:
    if st.button("🚀 开始一键自动分析", type="primary"):
        with st.spinner("正在分析…"):
            overview = analyzer.overview(df)
            st.markdown("#### ① 数据概览")
            st.dataframe(pd.DataFrame(overview["columns"]), width="stretch")
            st.markdown("#### ② 缺失值检测")
            miss_df = pd.DataFrame(analyzer.missing_info(df))
            st.dataframe(miss_df, width="stretch")
            st.plotly_chart(charts.fig_missing(df), width="stretch")
            st.markdown("#### ③ 重复值检测")
            dup = analyzer.duplicates_info(df)
            if dup["count"] == 0:
                st.success("未发现重复行 ✅")
            else:
                st.warning(f"发现 {dup['count']} 条重复行（占 {dup['pct']}%）")
            st.markdown("#### ④ 数值字段描述统计")
            stats = analyzer.describe_statistics(df)["fields"]
            if stats:
                st.dataframe(pd.DataFrame(stats).T, width="stretch")
            else:
                st.info("数据集中没有数值型字段。")
            st.markdown("#### ⑤ 异常值检测（IQR 法）")
            for col in ov["numeric"][:6]:
                out = analyzer.outlier_detection(df, col)
                st.caption(f"{col}：异常值 {out['outlier_count']} 条（{out['pct']}%），"
                           f"正常范围 [{out['lower_bound']}, {out['upper_bound']}]")
    else:
        st.info("点击上方按钮，对当前数据集执行一键自动分析（描述统计、缺失值、重复值、异常值检测）。")

# ================================================================ Tab 3
with tab_chart:
    st.write("**智能图表**：系统根据字段类型自动选择最合适的图表，图表均为 Plotly 交互式（可缩放、悬停查看数值）。")
    ov = analyzer.classify_columns(df)
    for col in ov["numeric"][:4]:
        st.plotly_chart(charts.fig_histogram(df, col), width="stretch")
    for col in ov["categorical"][:3]:
        st.plotly_chart(charts.fig_pie(df, col), width="stretch")
    if ov["datetime"] and ov["numeric"]:
        st.markdown("#### 时间趋势（按月汇总）")
        d_col = st.selectbox("日期字段", ov["datetime"], key="trend_date")
        v_col = st.selectbox("数值字段", ov["numeric"], key="trend_val")
        trend = analyzer.time_trend(df, d_col, v_col, "sum")
        st.plotly_chart(charts.fig_line(trend["trend"]), width="stretch")
    corr = analyzer.correlation_matrix(df)
    if corr["matrix"]:
        st.markdown("#### 相关性热力图")
        st.plotly_chart(charts.fig_heatmap(corr), width="stretch")
        st.markdown("#### 强相关字段对")
        for p in corr["top_pairs"][:5]:
            st.caption(f"{p['pair'][0]} 与 {p['pair'][1]}：r = {p['corr']}")
    if len(ov["numeric"]) >= 2:
        st.markdown("#### 散点图")
        c1, c2 = st.columns(2)
        with c1:
            sx = st.selectbox("X 轴", ov["numeric"], key="sc_x", index=0)
        with c2:
            sy = st.selectbox("Y 轴", ov["numeric"], key="sc_y",
                              index=min(1, len(ov["numeric"]) - 1))
        st.plotly_chart(charts.fig_scatter(df, sx, sy, ov["categorical"][0] if ov["categorical"] else None),
                        width="stretch")
    if ov["numeric"]:
        st.markdown("#### 箱线图（异常值可视化）")
        st.plotly_chart(charts.fig_box(df, ov["numeric"][0],
                                       ov["categorical"][0] if ov["categorical"] else None),
                        width="stretch")

# ================================================================ Tab 4
with tab_ai:
    st.write("**AI 分析结论**：把规则化统计结果交给大模型，自动生成通俗易懂的分析结论与业务建议。")
    if st.button("🧠 生成 AI 分析结论", type="primary"):
        client = get_client()
        if client is None:
            st.warning("请先在左侧填写 API Key（DeepSeek 开放平台申请）。")
        else:
            with st.spinner("大模型正在分析统计结果…"):
                summary = report_mod.build_analysis_summary(df)
                conclusion = agent.generate_conclusion(client, st.session_state.model, df, summary)
                st.session_state.conclusion = conclusion
    if st.session_state.conclusion:
        with st.expander("查看规则化统计摘要（模型输入）"):
            st.code(report_mod.build_analysis_summary(df), language=None)
        st.markdown(st.session_state.conclusion)
    else:
        st.info("点击按钮生成。即使不配置 API Key，也可以查看上方“规则化统计摘要”。")

# ================================================================ Tab 5
with tab_chat:
    st.write("**对话式问数**：用自然语言向数据提问。AI Agent 通过 Function Calling 自主选择分析工具、执行查询并汇总回答，支持多轮对话。")
    client = get_client()
    if client is None:
        st.warning("未配置 API Key，对话式问数不可用。其他功能（自动分析、图表、导出）不受影响，仍可正常使用。")
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    question = st.chat_input("例如：哪个月销售额最高？各地区销量占比如何？")
    if question:
        with st.chat_message("user"):
            st.markdown(question)
        if client is None:
            st.error("请先在左侧填写 API Key 后重试。")
        else:
            with st.chat_message("assistant"):
                with st.spinner("Agent 思考中（选择工具 → 执行 → 汇总）…"):
                    try:
                        answer, history, trace = agent.run_agent(
                            client, st.session_state.model, df, question,
                            st.session_state.chat_history)
                        st.session_state.chat_history = history
                        st.markdown(answer)
                        if trace:
                            with st.expander("🔍 Agent 工具调用轨迹（Function Calling）"):
                                for i, t in enumerate(trace, 1):
                                    st.caption(f"第 {i} 次调用：{t['name']} {json.dumps(t['arguments'], ensure_ascii=False)}")
                    except Exception as e:  # noqa: BLE001
                        st.error(f"调用失败：{e}")

# ================================================================ Tab 6
with tab_export:
    st.write("**报告导出**：一键生成分析报告，可下载 Markdown 或 HTML（含交互图表）版本。")
    c1, c2 = st.columns(2)
    conclusion = st.session_state.conclusion
    md_report = report_mod.build_markdown_report(df, conclusion)
    with c1:
        st.download_button("⬇️ 下载 Markdown 报告", md_report.encode("utf-8"),
                           file_name="数据分析报告.md", mime="text/markdown",
                           width="stretch")
    html_report = report_mod.build_html_report(df, conclusion)
    with c2:
        st.download_button("⬇️ 下载 HTML 报告（含交互图表）", html_report.encode("utf-8"),
                           file_name="数据分析报告.html", mime="text/html",
                           width="stretch")
    with st.expander("预览 Markdown 报告"):
        st.code(md_report, language="markdown")
