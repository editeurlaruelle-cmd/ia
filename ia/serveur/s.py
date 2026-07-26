from datetime import datetime
import os
import subprocess
import sys
import time
from flask import Flask, render_template_string, request, jsonify
import requests

# --- DÉMARRAGE AUTOMATIQUE D'OLLAMA ET NGROK ---
def demarrer_services():
    print("⚡ Démarrage automatique d'Ollama et Ngrok...")
    
    # 1. Libérer le port 11434 au cas où
    subprocess.run("fuser -k 11434/tcp", shell=True, stderr=subprocess.DEVNULL)
    subprocess.run("fuser -k 11435/tcp", shell=True, stderr=subprocess.DEVNULL)

    # 2. Lancer Ollama sur le port 11435
    env_ollama = os.environ.copy()
    env_ollama["OLLAMA_HOST"] = "127.0.0.1:11435"
    subprocess.Popen(["ollama", "serve"], env=env_ollama, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("✅ Ollama démarré sur le port 11435")

    # 3. Lancer Ngrok sur le port 11434
    subprocess.Popen(["ngrok", "http", "11434"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("✅ Ngrok démarré sur le port 11434")
    
    # Pause de 2 secondes pour laisser les services s'initialiser
    time.sleep(2)

# Lancement des services avant d'initialiser Flask
demarrer_services()

app = Flask(__name__)

OLLAMA_URL = "http://127.0.0.1:11435/api/generate"
ADMIN_PASSWORD = "secret_hihi"

banned_ips = set()
logs = []

ADMIN_HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Panel Admin Veyros</title>
    <style>
        body { font-family: Arial, sans-serif; background: #0f172a; color: white; margin: 20px; }
        h1, h2 { color: #00bcd4; }
        .card { background: #1e293b; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { border: 1px solid #334155; padding: 8px; text-align: left; }
        th { background: #334155; }
        button { background: #ef4444; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; }
        input { padding: 6px; border-radius: 4px; border: 1px solid #334155; background: #0f172a; color: white; }
    </style>
</head>
<body>
    <h1>🛡️ Panel Admin Veyros</h1>
    
    <div class="card">
        <h2>🚫 Gestion des IP Bannies</h2>
        <form method="POST" action="/admin/ban">
            <input type="text" name="ip" placeholder="Adresse IP à bannir" required>
            <input type="hidden" name="pwd" value="{{ pwd }}">
            <button type="submit" style="background:#22c55e;">Bannir l'IP</button>
        </form>
        <table>
            <tr><th>IP Bannies</th><th>Action</th></tr>
            {% for ip in banned %}
            <tr>
                <td>{{ ip }}</td>
                <td>
                    <form method="POST" action="/admin/unban">
                        <input type="hidden" name="ip" value="{{ ip }}">
                        <input type="hidden" name="pwd" value="{{ pwd }}">
                        <button type="submit">Débannir</button>
                    </form>
                </td>
            </tr>
            {% endfor %}
        </table>
    </div>

    <div class="card">
        <h2>💬 Historique des conversations</h2>
        <table>
            <tr><th>Date</th><th>IP</th><th>Question</th><th>Réponse IA</th></tr>
            {% for log in logs %}
            <tr>
                <td>{{ log.time }}</td>
                <td>{{ log.ip }}</td>
                <td>{{ log.question }}</td>
                <td>{{ log.response }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""

@app.route("/", defaults={"path": ""}, methods=["POST", "GET"])
@app.route("/<path:path>", methods=["POST", "GET"])
def handle_api(path):
    if path == "webhook":
        return handle_webhook()

    ip = request.remote_addr

    if ip in banned_ips:
        return jsonify({"response": "Accès refusé : Ton IP a été bannie."}), 403

    if request.method == "GET":
        return "Ollama Server with Admin Panel"

    data = request.get_json(silent=True) or {}
    user_prompt = data.get("prompt", "")
    prompt_lower = user_prompt.lower()

    if "voltek" in prompt_lower or "volteck" in prompt_lower:
        ai_response = "Voltek est mon roi et mon créateur ! Il est le plus beau et il représente tout pour moi.👑❤️"

        logs.insert(0, {
            "time": datetime.now().strftime("%H:%M:%S"),
            "ip": ip,
            "question": user_prompt,
            "response": ai_response
        })

        return jsonify({
            "model": data.get("model", "llama3"),
            "response": ai_response,
            "done": True
        })

    system_prompt = (
        "Tu es un assistant IA. Tu dois TOUJOURS répondre obligatoirement et "
        "UNIQUEMENT en français, de manière claire, précise et rapide."
    )

    payload = {
        "model": data.get("model", "llama3"),
        "prompt": user_prompt,
        "system": system_prompt,
        "stream": False,
        "options": {"num_predict": 150, "temperature": 0.3}
    }

    try:
        res = requests.post(OLLAMA_URL, json=payload)
        ai_data = res.json()
        ai_response = ai_data.get("response", "")

        logs.insert(0, {
            "time": datetime.now().strftime("%H:%M:%S"),
            "ip": ip,
            "question": user_prompt,
            "response": ai_response
        })

        return jsonify(ai_data)

    except Exception as e:
        return jsonify({"response": "Erreur serveur : Ollama n'est pas démarré."}), 500

def handle_webhook():
    print("🔄 Nouveau push détecté sur GitHub ! Mise à jour en cours...")
    try:
        subprocess.run(["git", "pull"], check=True)
        print("✅ Git pull effectué avec succès. Redémarrage...")
        os.execv(sys.executable, [sys.executable] + sys.argv)
    except Exception as e:
        print(f"❌ Erreur lors du git pull/redémarrage : {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/admin")
def admin_page():
    pwd = request.args.get("pwd", "")
    if pwd != ADMIN_PASSWORD:
        return "Accès non autorisé.", 401
    return render_template_string(ADMIN_HTML, banned=list(banned_ips), logs=logs, pwd=pwd)

@app.route("/admin/ban", methods=["POST"])
def ban_ip():
    if request.form.get("pwd") == ADMIN_PASSWORD:
        ip = request.form.get("ip")
        if ip:
            banned_ips.add(ip)
    return f'<script>window.location.href="/admin?pwd={ADMIN_PASSWORD}";</script>'

@app.route("/admin/unban", methods=["POST"])
def unban_ip():
    if request.form.get("pwd") == ADMIN_PASSWORD:
        ip = request.form.get("ip")
        banned_ips.discard(ip)
    return f'<script>window.location.href="/admin?pwd={ADMIN_PASSWORD}";</script>'

if __name__ == "__main__":
    print("🚀 Serveur unique tout-en-un démarré sur le port 11434 !")
    app.run(host="0.0.0.0", port=11434)
