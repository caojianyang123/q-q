# SmartAgent Hub 🤖

基于 LangChain 框架构建的多智能体协作平台，实现情报搜集、数据分析、报告撰写的自动化工作流。

## ✨ 功能特性

- **多智能体协作**：情报搜集、数据分析、报告撰写三智能体协同工作
- **智能路由调度**：主智能体自动选择合适的智能体处理任务
- **多对话管理**：支持创建、切换、删除多个独立对话
- **记忆功能**：对话上下文记忆，历史对话自动注入
- **文件隔离存储**：每个对话生成的文件存储在独立目录
- **实时新闻搜索**：接入天行数据 API 获取真实新闻数据
- **自动报告生成**：根据素材自动生成格式化周报

## 🛠️ 技术栈

- **框架**：LangChain v1.x
- **前端**：Streamlit
- **模型**：阿里云百炼 / OpenAI API
- **数据**：天行数据 API（新闻搜索）
- **存储**：JSON 序列化 + 文件系统

## 📁 项目结构

```
SmartAgent-Hub/
├── app.py              # Streamlit 前端主程序
├── agents.py           # 智能体定义与调度逻辑
├── tools.py            # 工具函数（搜索、读取、生成）
├── llm.py              # LLM 模型配置
├── .env                # API 密钥配置（需自行创建）
├── requirements.txt    # 依赖清单
├── data/
│   └── raw_materials/  # 搜索数据存储目录
└── reports/            # 报告生成目录
```

## 🚀 快速开始

### 环境要求

- Python 3.10+
- pip

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置 API 密钥

创建 `.env` 文件：

```env
# 阿里云百炼 API（或 OpenAI API）
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# 天行数据 API（可选，用于新闻搜索）
TIANAPI_KEY=your-tianapi-key
```

### 启动应用

```bash
streamlit run app.py
```

访问 http://localhost:8501 即可使用。

## 📖 使用说明

1. **创建对话**：点击左侧「新对话」按钮创建新对话
2. **选择智能体**：在侧边栏选择智能体（自动选择 / 情报搜集 / 数据分析 / 报告撰写）
3. **发送消息**：在底部输入框输入问题并发送
4. **查看文件**：右侧面板显示当前对话生成的文件，点击可展开查看
5. **删除对话**：点击对话右侧的删除按钮删除对话

## 🔧 智能体介绍

| 智能体 | 职责 | 工具 |
|--------|------|------|
| **情报搜集智能体** | 搜索行业新闻、获取实时数据 | `search_news` |
| **数据分析智能体** | 阅读素材、提炼核心观点 | `read_materials` |
| **报告撰写智能体** | 按模板生成格式化周报 | `generate_report` |
| **主智能体** | 任务路由与调度 | `call_search_agent` / `call_analysis_agent` / `call_report_agent` |

## 📝 工作流程

```
用户提问 → 主智能体路由 → 情报搜集 → 数据分析 → 报告撰写 → 返回结果
```

## 📄 License

MIT License

