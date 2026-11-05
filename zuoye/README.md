# 智能数据分析智能体 —— 使用说明

《人工智能导论》期末课程设计　|　大数据管理与应用 26-3 班　|　261560305　佟宇鑫

## 一、项目简介

本项目实现一个**智能数据分析智能体**：上传 CSV/Excel 表格后，系统自动完成探索性数据分析（EDA）、智能图表可视化，并调用 **DeepSeek 大模型 API** 生成分析结论；用户还可以用**自然语言对话**向数据提问，AI Agent 通过 **Function Calling（工具调用）** 机制自主选择分析工具、执行查询并汇总回答，支持多轮对话；最后可一键导出分析报告（Markdown / HTML）。

## 二、运行环境

- Python 3.10+（Windows 10/11）
- 网络连接（调用 DeepSeek API 时需要；纯本地分析无需）

## 三、安装与启动

1. 安装依赖（首次运行）：

```bash
pip install -r requirements.txt
```

2. 启动系统（二选一）：
   - 双击 `启动程序.bat`；
   - 或在命令行执行：

```bash
streamlit run app.py
```

3. 浏览器自动打开 `http://localhost:8501`。

## 四、使用步骤

1. **（可选）配置 API Key**：左侧栏填写 DeepSeek 开放平台申请的 API Key（平台地址 platform.deepseek.com），点击"测试连接"验证。不配置 Key 时，除"AI 分析结论"和"对话式问数"外，其余功能均可正常使用。
2. **上传数据**：左侧栏上传 CSV / Excel 文件，或点击"使用内置示例数据"（电商销售数据 500 行）。
3. **体验功能**：依次体验 数据预览 → 一键自动分析 → 智能图表 → AI 分析结论 → 对话式问数 → 报告导出。
4. **对话式问数示例**（建议演示时使用）：
   - "这个数据集有哪些字段？"
   - "哪个月销售额最高？趋势如何？"
   - "各商品类别的销售额占比如何？"
   - "销售额和销量之间有相关性吗？"
   - "销售额有没有异常值？"

## 五、项目结构

```
代码/
├── app.py                # Streamlit 主程序（界面与会话管理）
├── core/
│   ├── __init__.py
│   ├── data_loader.py    # 数据加载（CSV/Excel，编码与分隔符自动识别）
│   ├── analyzer.py       # 规则化分析引擎（描述统计/缺失值/分布/趋势/相关性/异常值）
│   ├── charts.py         # 智能图表（Plotly 交互式图表自动生成）
│   ├── agent.py          # 大模型 Agent（Function Calling 工具调用循环）
│   └── report.py         # 分析报告导出（Markdown / HTML）
├── gen_sample_data.py    # 示例数据生成脚本
├── 示例数据/电商销售数据.csv
├── requirements.txt
└── 启动程序.bat
```

## 六、常见问题

- **端口被占用**：修改启动命令 `streamlit run app.py --server.port 8502`；
- **API 调用失败**：检查 Key 是否有效、余额是否充足、网络是否可访问 api.deepseek.com；
- **无 Key 演示**：系统自动降级为本地规则分析，EDA、图表、报告导出均可用，不会报错。
