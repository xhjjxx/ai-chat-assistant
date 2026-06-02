# AI智能问答助手 - Flask + DeepSeek API
# 运行方式：python app.py
# 然后浏览器打开 http://127.0.0.1:5000

from flask import Flask, render_template_string, request, jsonify
from openai import OpenAI
import os

# =============================
# 配置DeepSeek API
# 优先从环境变量读取，没有则用下面的默认值
# =============================
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "your-api-key-here")

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.deepseek.com"
)

# =============================
# 创建Flask应用
# =============================
app = Flask(__name__)

# HTML页面
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AI问答助手</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: "Microsoft YaHei", sans-serif;
            background: #1a1a2e;
            color: #eee;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .header {
            background: #16213e;
            padding: 16px 24px;
            font-size: 20px;
            font-weight: bold;
            border-bottom: 2px solid #0f3460;
        }
        .chat-area {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }
        .message {
            margin-bottom: 12px;
            padding: 10px 16px;
            border-radius: 12px;
            max-width: 70%;
            line-height: 1.6;
            white-space: pre-wrap;
        }
        .user-msg {
            background: #0f3460;
            margin-left: auto;
            text-align: right;
        }
        .ai-msg {
            background: #16213e;
            border: 1px solid #0f3460;
        }
        .input-area {
            display: flex;
            padding: 16px;
            background: #16213e;
            border-top: 2px solid #0f3460;
        }
        .input-area input {
            flex: 1;
            padding: 12px 16px;
            border: none;
            border-radius: 8px;
            background: #1a1a2e;
            color: #eee;
            font-size: 16px;
            outline: none;
        }
        .input-area button {
            margin-left: 12px;
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            background: #e94560;
            color: white;
            font-size: 16px;
            cursor: pointer;
        }
        .input-area button:hover {
            background: #c81e45;
        }
    </style>
</head>
<body>
    <div class="header">🤖 AI问答助手</div>
    <div class="chat-area" id="chatArea"></div>
    <div class="input-area">
        <input type="text" id="userInput" placeholder="输入你的问题..."
               onkeypress="if(event.key==='Enter')sendMsg()">
        <button onclick="sendMsg()">发送</button>
    </div>

    <script>
        function sendMsg() {
            var input = document.getElementById('userInput');
            var text = input.value.trim();
            if (!text) return;
            input.value = '';

            addMessage(text, 'user-msg');

            fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            })
            .then(function(res) { return res.json(); })
            .then(function(data) {
                addMessage(data.reply, 'ai-msg');
            })
            .catch(function(err) {
                addMessage('出错了：' + err, 'ai-msg');
            });
        }

        function addMessage(text, className) {
            var div = document.createElement('div');
            div.className = 'message ' + className;
            div.textContent = text;
            document.getElementById('chatArea').appendChild(div);
            document.getElementById('chatArea').scrollTop = 99999;
        }
    </script>
</body>
</html>
"""

# =============================
# 路由
# =============================

@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

@app.route("/api/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一个helpful的AI助手，用简洁的中文回答。"},
            {"role": "user", "content": user_message}
        ]
    )

    ai_reply = response.choices[0].message.content
    return jsonify({"reply": ai_reply})


if __name__ == "__main__":
    print("🚀 服务器启动中...")
    print("📱 浏览器打开 → http://127.0.0.1:5000")
    app.run(debug=True)
