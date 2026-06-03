# AI智能问答助手 - Flask + DeepSeek API
# Day 4 升级版：支持多轮对话记忆 + 清除对话按钮
# 运行方式：python app.py
# 然后浏览器打开 http://127.0.0.1:5000

from flask import Flask, render_template_string, request, jsonify, session
from openai import OpenAI
import os

# =============================
# 配置DeepSeek API
# =============================
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")

# 如果环境变量没设置，尝试从本地配置文件读取
try:
    from config import DEEPSEEK_API_KEY as CONFIG_KEY
    if not API_KEY and CONFIG_KEY:
        API_KEY = CONFIG_KEY
except ImportError:
    pass

client = OpenAI(
    api_key=API_KEY or "placeholder",
    base_url="https://api.deepseek.com"
)

# 检查API Key
if not API_KEY or API_KEY == "placeholder":
    print("⚠️  警告：API Key 未配置！")
    print("  方法1：设置环境变量 set DEEPSEEK_API_KEY=sk-你的Key")
    print("  方法2：在 config.py 里填入你的Key（不推GitHub）")
    print("=" * 50)

# =============================
# 创建Flask应用
# =============================
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")  # session需要密钥

# HTML页面（升级版）
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
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header-left {
            display: flex;
            align-items: center;
            gap: 8px;
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
        .system-msg {
            text-align: center;
            color: #888;
            font-size: 14px;
            margin: 10px 0;
        }
        .input-area {
            display: flex;
            padding: 16px;
            background: #16213e;
            border-top: 2px solid #0f3460;
            gap: 8px;
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
        .btn-send {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            background: #e94560;
            color: white;
            font-size: 16px;
            cursor: pointer;
        }
        .btn-send:hover { background: #c81e45; }
        .btn-clear {
            padding: 12px 16px;
            border: 1px solid #0f3460;
            border-radius: 8px;
            background: transparent;
            color: #aaa;
            font-size: 14px;
            cursor: pointer;
        }
        .btn-clear:hover { color: #e94560; border-color: #e94560; }
        .typing {
            display: none;
            color: #888;
            font-size: 14px;
            padding: 8px 16px;
        }
        .typing.show { display: block; }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-left">
            🤖 AI问答助手
        </div>
        <button class="btn-clear" onclick="clearChat()">🗑 清除对话</button>
    </div>
    <div class="chat-area" id="chatArea">
        <div class="system-msg">开始和AI对话吧，AI会记住你说过的话</div>
    </div>
    <div class="typing" id="typing">AI正在思考...</div>
    <div class="input-area">
        <input type="text" id="userInput" placeholder="输入你的问题..."
               onkeypress="if(event.key==='Enter')sendMsg()">
        <button class="btn-send" onclick="sendMsg()">发送</button>
    </div>

    <script>
        function sendMsg() {
            var input = document.getElementById('userInput');
            var text = input.value.trim();
            if (!text) return;
            input.value = '';

            addMessage(text, 'user-msg');
            showTyping(true);

            fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            })
            .then(function(res) {
                if (!res.ok) {
                    return res.text().then(function(text) {
                        throw new Error('服务器错误：' + text.substring(0, 100));
                    });
                }
                return res.json();
            })
            .then(function(data) {
                showTyping(false);
                addMessage(data.reply, 'ai-msg');
            })
            .catch(function(err) {
                showTyping(false);
                addMessage('出错了：' + err.message, 'ai-msg');
            });
        }

        function clearChat() {
            var chatArea = document.getElementById('chatArea');
            chatArea.innerHTML = '<div class="system-msg">对话已清除，重新开始吧</div>';

            fetch('/api/clear', { method: 'POST' })
            .then(function(res) { return res.json(); })
            .then(function(data) {
                console.log('对话已清除');
            });
        }

        function addMessage(text, className) {
            var div = document.createElement('div');
            div.className = 'message ' + className;
            div.textContent = text;
            document.getElementById('chatArea').appendChild(div);
            document.getElementById('chatArea').scrollTop = 99999;
        }

        function showTyping(show) {
            var el = document.getElementById('typing');
            if (show) {
                el.className = 'typing show';
            } else {
                el.className = 'typing';
            }
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
    try:
        user_message = request.json.get("message", "")

        # 检查API Key
        if not API_KEY or "your-api-key" in API_KEY:
            return jsonify({"reply": "⚠️ API Key 未配置，请先在app.py里填入你的DeepSeek Key！"})

        # 从session中取出对话历史（没有就创建空的）
        if "messages" not in session:
            session["messages"] = []

        # 把系统提示加到最前面（每次都加，确保第一轮也有）
        all_messages = [
            {"role": "system", "content": "你是一个helpful的AI助手，用简洁的中文回答。"}
        ]
        # 加上历史对话
        all_messages.extend(session["messages"])
        # 加上用户当前消息
        all_messages.append({"role": "user", "content": user_message})

        # 调用API
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=all_messages
        )

        ai_reply = response.choices[0].message.content

        # 把这一轮的对话存进session（用户消息+AI回复）
        session["messages"].append({"role": "user", "content": user_message})
        session["messages"].append({"role": "assistant", "content": ai_reply})
        # 标记session已修改，Flask才会保存
        session.modified = True

        return jsonify({"reply": ai_reply})

    except Exception as e:
        return jsonify({"reply": f"出错了：{str(e)}"})

@app.route("/api/clear", methods=["POST"])
def clear():
    """清除对话历史"""
    session["messages"] = []
    session.modified = True  # 标记已修改
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    print("🚀 服务器启动中...")
    print("📱 浏览器打开 → http://127.0.0.1:5000")
    app.run(debug=True)
