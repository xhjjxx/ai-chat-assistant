# AI智能问答助手

基于 Flask + DeepSeek API 的网页版 AI 问答应用。

## 功能

- 浏览器端与 AI 实时对话
- 深色主题聊天界面
- 支持回车键发送消息
- 流式响应显示

## 技术栈

- **后端**: Python · Flask
- **AI**: DeepSeek API (OpenAI 兼容接口)
- **前端**: HTML · CSS · JavaScript

## 快速开始

### 1. 安装依赖

```bash
pip install flask openai
```

### 2. 配置 API Key

在 `app.py` 中替换你的 DeepSeek API Key：

```python
API_KEY = "your-api-key-here"
```

申请地址：https://platform.deepseek.com

### 3. 运行

```bash
python app.py
```

浏览器打开 http://127.0.0.1:5000 即可使用。

## 项目结构

```
ai-chat-assistant/
├── app.py           # 主程序（Flask服务 + API调用）
├── .gitignore
└── README.md
```

## License

MIT
