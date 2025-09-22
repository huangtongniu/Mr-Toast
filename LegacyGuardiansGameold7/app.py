# app.py (修改 V5 - 添加开场动画)
#   .chat-window { flex-grow: 1; overflow-y: auto; padding: 10px; background: rgba(0,0,0,0.2); border-radius: 10px; margin-top: 15px; display: flex; flex-direction: column; gap: 12px; }
from flask import Flask, jsonify, request, render_template, redirect, url_for # 导入 redirect, url_for
from flask_cors import CORS
import os
import openai
from dotenv import load_dotenv
from game.game_manager import GameManager

# --- 1. 初始化 ---
app = Flask(__name__)
CORS(app)
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    print("WARNING: OPENAI_API_KEY not found. Chat functionality will not be available.")

game_manager = GameManager(data_path='data/')
SESSION_ID = "local_player"

# --- 2. API 路由 (保持不变) ---
@app.route("/api/game_state", methods=["GET"])
def get_game_state():
    state = game_manager.get_game_state(SESSION_ID)
    return jsonify(state)

@app.route("/api/perform_action", methods=["POST"])
def perform_action():
    action_data = request.json
    result = game_manager.handle_action(SESSION_ID, action_data)
    if result.get("success"):
        return get_game_state()
    else:
        return jsonify({"error": result.get("message", "Unknown error")}), 400

@app.route("/api/advance_level", methods=["POST"])
def advance_level():
    result = game_manager.advance_level(SESSION_ID)
    if result.get("success"):
        return get_game_state()
    else:
        return jsonify({"error": result.get("message", "Failed to move to next level.")}), 400

@app.route("/api/reset", methods=["POST"])
def reset():
    game_manager.start_new_session(SESSION_ID)
    return get_game_state()

@app.route("/api/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    response = game_manager.handle_chat(SESSION_ID, user_message)
    return jsonify(response)

# --- 3. 页面渲染路由 (新增和修改的部分) ---
@app.route("/")
def home_redirect():
    """根路由现在重定向到开场动画"""
    return redirect(url_for('intro_animation')) # 重定向到开场动画页面

@app.route("/intro")
def intro_animation():
    """渲染开场动画页面"""
    return render_template("intro_animation.html")

@app.route("/game_main") # 修改了原来 / 的路由，现在它是游戏主页
def index():
    """渲染游戏主页，开场动画结束后会跳转到这里"""
    return render_template("index.html")

@app.route("/game/part1")
def game_part1():
    """渲染游戏的第一和第二部分页面"""
    return render_template("game_part1.html")

@app.route("/game/part2")
def game_part2():
    """渲染游戏的第三部分页面"""
    return render_template("game_part2.html")


# --- 4. 启动服务器 ---
if __name__ == "__main__":
    game_manager.start_new_session(SESSION_ID)

    print("\n========================= Legacy Guardian - Game Start Guide =========================")
    print("Backend services and page rendering have all started!")
    print(f"Service is running on: http://127.0.0.1:5002")
    print("\n--- How to Start the Game ---")
    print("1. [Keep This Window Open] Please do not close this window, it is the core game server.")
    print("2. [Start Game]          Open the following address in your browser to begin:")
    print(f"                         http://127.0.0.1:5002/") # 现在会先看到开场动画
    print("===============================================================================\n")

    app.run(port=5002, debug=True)