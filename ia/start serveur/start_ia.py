import os
import subprocess
import time

print("🚀 Démarrage du serveur Ollama...")

# 1. Préparer l'environnement avec OLLAMA_HOST=0.0.0.0
env = os.environ.copy()
env["OLLAMA_HOST"] = "0.0.0.0"

# Ajout du dossier ~/.local/bin au PATH pour trouver Ngrok si besoin
env["PATH"] = f"{os.path.expanduser('~/.local/bin')}:{env.get('PATH', '')}"

try:
    # 2. Lancer Ollama en arrière-plan
    ollama_process = subprocess.Popen(["ollama", "serve"], env=env)
    
    # Pause de 3 secondes pour laisser le temps à Ollama de démarrer
    time.sleep(3)
    
    print("\n🌐 Démarrage du tunnel Ngrok...")
    # 3. Lancer Ngrok (cela va bloquer l'affichage dans la console et montrer ton URL)
    ngrok_process = subprocess.Popen(["ngrok", "http", "11434"], env=env)
    
    # Attendre que l'un des deux processus s'arrête
    ngrok_process.wait()

except KeyboardInterrupt:
    print("\n\n🛑 Arrêt du serveur et du tunnel...")
    ollama_process.terminate()
    ngrok_process.terminate()
    print("✅ Tout est bien fermé !")