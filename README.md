# 🎭 AI 辩论赛系统

> **让 AI 为你呈现一场精彩的思辨盛宴**

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![LangChain](https://img.shields.io/badge/LangChain-0.1+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## ✨ 项目简介

AI 辩论赛系统是一个基于 **LangChain/LangGraph** 构建的智能辩论平台，采用先进的**多智能体协作技术**，让 AI 扮演正方、反方和裁判，自动完成一场完整的辩论赛事。

系统支持 **DeepSeek** 和 **阿里云通义千问** 两大模型提供商，可根据需求自由选择不同模型，体验不同风格的辩论盛宴。

### 🎯 为什么选择 AI 辩论赛？

- 🧠 **深度思考**：采用 DeepSeek Reasoner 模型，展现推理过程
- ⚡ **实时生成**：所有辩论内容实时 AI 生成，拒绝预设脚本
- 🎓 **教育价值**：观摩高水平 AI 辩论，提升思辨能力
- 🎮 **互动体验**：自由选择辩题，打造专属辩论赛事
- 📊 **专业评分**：AI 裁判从多个维度公正评判
- 🔬 **模型评测**：作为评估大模型逻辑思维能力的基准测试工具

---

## 🚀 核心功能

### 🤖 多角色 AI 辩论手

| 角色 | 功能 | 模型支持 |
|------|------|----------|
| 🔵 **正方辩手** | 从正面立场阐述观点，逻辑严密 | DeepSeek / 通义千问 |
| 🔴 **反方辩手** | 从反面立场展开论述，反驳有力 | DeepSeek / 通义千问 |
| ⚖️ **AI 裁判** | 公正评分，专业点评 | DeepSeek / 通义千问 |
| 🎤 **主持人** | 引导辩论流程，把控节奏 | DeepSeek Chat |

### 📋 完整辩论流程

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  开篇立论   │ →  │  攻辩环节   │ →  │  自由辩论   │ →  │  总结陈词   │
│  双方各3分钟 │    │   共2轮     │    │   3轮交替   │    │  双方各2分钟 │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### 🎨 直观的用户界面

- **简洁设计**：基于 Streamlit 构建的现代化界面
- **模型选择**：侧边栏自由选择各角色使用的模型
- **实时展示**：辩论过程实时呈现，沉浸式体验
- **结果分析**：详细评分报告，包含裁判点评

---

## 🛠 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                       │
│                  Streamlit Web Interface                    │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    Application Layer                        │
│              ┌─────────────────────────────────┐             │
│              │      LangGraph State Machine     │             │
│              │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ │             │
│              │  │ Init│ →│Open│ →│Cross│ →│Free│ → ...    │             │
│              │  └─────┘ └─────┘ └─────┘ └─────┘ │             │
│              └─────────────────────────────────┘             │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                      Agent Layer                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│  │ Debater AI  │ │  Judge AI   │ │Moderator AI │            │
│  │  (Aff/Neg)  │ │ (Scoring)   │ │  (Host)     │            │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘            │
└─────────┼───────────────┼───────────────┼───────────────────┘
          │               │               │
┌─────────▼───────────────▼───────────────▼───────────────────┐
│                    LLM Provider Layer                        │
│  ┌──────────────┐              ┌──────────────┐             │
│  │   DeepSeek   │              │   DashScope  │             │
│  │   深度思考    │              │   通义千问    │             │
│  └──────────────┘              └──────────────┘             │
└─────────────────────────────────────────────────────────────┘
```

### 🧰 技术栈

| 类别 | 技术 | 说明 |
|------|------|------|
| **后端框架** | Python + LangChain + LangGraph | 多智能体编排 |
| **前端框架** | Streamlit | 快速构建 Web 应用 |
| **LLM 提供商** | DeepSeek / 阿里云 | 多模型支持 |
| **数据验证** | Pydantic | 类型安全 |
| **HTTP 客户端** | httpx | 异步请求 |
| **配置管理** | pydantic-settings | 环境变量管理 |

---

## 📦 快速开始

### 1️⃣ 安装依赖

```bash
git clone https://github.com/your-username/ai-debate.git
cd ai-debate
pip install -r requirements.txt
```

### 2️⃣ 配置 API 密钥

**方式一：环境变量（推荐）**

```bash
# macOS/Linux
export DEEPSEEK_API_KEY=your_deepseek_api_key_here
export DASHSCOPE_API_KEY=your_dashscope_api_key_here

# Windows PowerShell
$env:DEEPSEEK_API_KEY="your_deepseek_api_key_here"
$env:DASHSCOPE_API_KEY="your_dashscope_api_key_here"
```

**方式二：.env 文件**

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 API 密钥
```

### 3️⃣ 启动应用

```bash
streamlit run frontend/app.py
```

浏览器自动打开 `http://localhost:8501`

---

## 📖 使用指南

### 基础使用

1. **选择模型**：在侧边栏为正方、反方、裁判选择 AI 模型
2. **输入辩题**：输入自定义辩题或选择预设辩题
3. **开始辩论**：点击「开始辩论」按钮
4. **观赏辩论**：实时观看 AI 辩论过程
5. **查看结果**：查看详细评分和裁判点评

### 模型选择建议

| 使用场景 | 正方推荐 | 反方推荐 | 裁判推荐 |
|----------|----------|----------|----------|
| **深度辩论** | DeepSeek Reasoner | DeepSeek Reasoner | DeepSeek Reasoner |
| **快速体验** | DeepSeek Chat | DeepSeek Chat | DeepSeek Chat |
| **跨界对战** | DeepSeek Reasoner | 通义千问 Qwen3 | DeepSeek Reasoner |
| **高阶推理** | 通义千问 QwQ-Plus | 通义千问 QwQ-Plus | 通义千问 Qwen3 |

---

## 📐 评分标准

AI 裁判从以下四个维度对每位辩手进行评分：

| 维度 | 权重 | 评估要点 |
|------|------|----------|
| 🔹 **逻辑性** | 30% | 论证结构、推理严密性 |
| 🔸 **论据充分性** | 25% | 事实依据、数据支撑 |
| 🔻 **反驳有效性** | 25% | 针对性回应、观点拆解 |
| 🔺 **表达清晰度** | 20% | 语言表达、观点阐述 |

**胜负判定**：双方总分对比，分差小于 5% 判为平局。

---

## 🗂 项目结构

```
ai-debate/
├── 📁 config/                 # 配置中心
│   ├── settings.py            # 全局配置（多模型支持）
│   ├── debate_rules.yaml      # 辩论规则定义
│   └── prompts.yaml           # 系统 Prompt 模板
├── 📁 backend/                # 后端核心
│   ├── agents/                # AI 智能体
│   │   ├── base_agent.py      # 智能体基类
│   │   ├── debater_agent.py   # 辩论手实现
│   │   ├── judge_agent.py     # 裁判实现
│   │   └── moderator_agent.py # 主持人实现
│   ├── debate_flow/           # LangGraph 工作流
│   │   ├── state.py           # 状态定义
│   │   ├── nodes.py           # 图节点
│   │   └── graph.py           # 状态图构建
│   ├── models/                # 数据模型
│   └── utils/                 # 工具函数
├── 📁 frontend/               # 前端界面
│   └── app.py                 # Streamlit 应用
├── 📁 data/                   # 数据存储
│   └── logs/                  # 日志文件
├── 📄 .env.example            # 环境变量模板
├── 📄 .gitignore              # Git 忽略配置
├── 📄 requirements.txt        # Python 依赖
├── 📄 CLAUDE.md               # AI 开发指南
└── 📄 main.py                 # 程序入口
```

---

## 🔮 未来展望

### 🎯 模型评测基准

本系统天然适合作为 **LLM 逻辑思维能力评测工具**：

- **多维度评估**：逻辑性、论据充分性、反驳有效性、表达清晰度
- **实战场景**：真实辩论环境，全面考察模型推理能力
- **横向对比**：不同模型同台竞技，直观比较能力差异
- **量化评分**：标准化评分体系，可生成对比报告

**评测应用场景**：
- 🔬 **学术研究**：评估不同模型的推理能力
- 🏢 **企业选型**：为业务选择最适合的模型
- 📈 **模型优化**：跟踪模型迭代后的能力提升
- 🆚 **模型对战**：通义千问 vs DeepSeek vs GPT-4

### 🎙️ 语音合成
- **TTS 语音播报**：将 AI 辩论内容转换为自然语音
- **情感化表达**：根据辩论激烈程度调整语音语调
- **多音色选择**：正反方使用不同声音，增强区分度

### 🎥 视频生成
- **虚拟形象**：AI 辩手的 3D/2D 虚拟形象
- **肢体动作**：根据发言内容匹配手势和表情
- **场景渲染**：专业的辩论舞台背景

### 🌐 多语言支持
- **多语种辩论**：支持中英文双语辩论
- **实时翻译**：跨语言辩论场景

### 👥 多人互动
- **人机辩论**：用户作为一方与 AI 辩论
- **观众互动**：实时弹幕、投票功能
- **联机对战**：多位用户共同参与

### 📊 数据分析
- **辩论历史**：历史辩论记录与回放
- **数据分析**：辩题热度、模型表现统计
- **能力评估**：AI 辩论能力成长曲线

### 🧩 更多模型
- **GPT 系列**：OpenAI GPT-5
- **Claude 系列**：Anthropic Claude 4.5
- **文心一言**：百度 ERNIE Bot
- **星火认知**：科大讯飞 Spark

---

## 🤝 贡献指南

欢迎贡献代码、提出建议或报告问题！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 开源协议

本项目采用 [MIT](LICENSE) 协议开源。

---

## 🌟 致谢

感谢以下开源项目和技术社区：

- [LangChain](https://github.com/langchain-ai/langchain) - 强大的 LLM 应用开发框架
- [LangGraph](https://github.com/langchain-ai/langgraph) - 状态机编排工具
- [Streamlit](https://github.com/streamlit/streamlit) - 简洁高效的 Web 应用框架
- [DeepSeek](https://www.deepseek.com/) - 开放的高性能大模型 API
- [阿里云百炼](https://bailian.console.aliyun.com/) - 企业级大模型服务平台

---

<div align="center">

**如果这个项目对你有帮助，请给一个 ⭐ Star 支持一下！**

Made with ❤️ by AI Debate Team

</div>
