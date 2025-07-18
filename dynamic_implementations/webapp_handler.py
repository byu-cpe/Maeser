# SPDX-License-Identifier: LGPL-3.0-or-later

import os
import yaml
import json
from datetime import datetime
from flask import send_from_directory
from flask import Flask, render_template, request, jsonify

from maeser.chat.chat_logs import ChatLogsManager
from maeser.chat.chat_session_manager import ChatSessionManager
from generate_response import handle_message, get_valid_course_ids
from config import CHAT_HISTORY_PATH, LOG_SOURCE_PATH

# --- Setup ---
app = Flask(__name__)
app.secret_key = "your-secret-key"

# Initialize chat managers
chat_logs_manager = ChatLogsManager(CHAT_HISTORY_PATH)
sessions_manager = ChatSessionManager(chat_logs_manager=chat_logs_manager)

CHAT_HISTORY_PATH = os.path.join(LOG_SOURCE_PATH, "chat_history")

# --- Routes ---
@app.route("/")
def home():
    return render_template("chat.html")

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json()
    user_id = data.get("user_id")
    course_id = data.get("course_id")
    message = data.get("message")

    if not all([user_id, course_id, message]):
        return jsonify({"error": "Missing user_id, course_id, or message"}), 400

    try:
        response = handle_message(user_id, course_id, message)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/courses", methods=["GET"])
def get_courses():
    return jsonify({"courses": get_valid_course_ids()})

@app.route("/api/logs/<user_id>/<course_id>")
def list_logs(user_id, course_id):
    session_prefix = f"{user_id}:{course_id}"
    try:
        all_files = os.listdir(LOG_SOURCE_PATH)
        session_files = [f for f in all_files if f.startswith(session_prefix) and f.endswith(".json")]
        session_files.sort(reverse=True)
        return jsonify({"sessions": session_files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/logs/<user>")
def list_logs_for_user(user):
    try:
        files = [
            f for f in os.listdir(CHAT_HISTORY_PATH)
            if f.endswith(f"{user}.log")
        ]
        files.sort(reverse=True)
        sessions = []

        for fname in files:
            with open(os.path.join(CHAT_HISTORY_PATH, fname), "r") as f:
                log = yaml.safe_load(f)
                sessions.append({
                    "session_id": log.get("session_id", fname),
                    "time": log.get("time", ""),
                    "branch": log.get("branch", ""),
                    "filename": fname
                })

        return jsonify({"sessions": sessions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/logs/content/<filename>")
def get_yaml_log_content(filename):
    try:
        full_path = os.path.join(CHAT_HISTORY_PATH, filename)
        if not os.path.exists(full_path):
            return jsonify({"error": "Log file not found"}), 404
        with open(full_path, "r") as f:
            log = yaml.safe_load(f)
            return jsonify({
                "messages": log.get("messages", []),
                "metadata": {
                    "session_id": log.get("session_id"),
                    "branch": log.get("branch"),
                    "time": log.get("time")
                }
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/logs/content/<filename>")
def get_log_content(filename):
    try:
        file_path = os.path.join(LOG_SOURCE_PATH, filename)
        if not os.path.isfile(file_path):
            return jsonify({"error": "Log not found."}), 404
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify({"messages": data.get("messages", [])})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Run App ---
if __name__ == "__main__":
    app.run(port=3002, debug=True)
