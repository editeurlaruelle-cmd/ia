# 🤖 Veyros AI - Serveur Proxy, Panel Admin & Intercepteur

Bienvenue dans le dépôt du serveur **Veyros AI**. Ce projet est une infrastructure serveur Python basée sur **Flask** et **Ollama (Llama 3)**, permettant de gérer et de modérer les requêtes d'une application Chatbot via une adresse publique **Ngrok**.

---

## 🌟 Fonctionnalités

- **💬 Support Llama 3 local** : Réponses générées rapidement par le modèle Llama 3 via Ollama.
- **🇫🇷 Restriction linguistique** : Forçage des réponses exclusivement en français.
- **⚡ Optimisation de réponse** : Limite de tokens et réglage de la température pour des réponses ultra-rapides.
- **👑 Détection personnalisée (Mots-clés)** : Réponse prioritaire instantanée pour les requêtes sur *Voltek / Volteck*.
- **🛡️ Panel Admin Web** :
  - Historique complet des conversations (Heure, IP, Question, Réponse) mis à jour en direct.
  - Système de **Ban / Déban d'adresses IP** à la volée.
- **🎭 Mode Manuel / Maintenance** : Possibilité d'intercepter les requêtes et de répondre soi-même à la place de l'IA.

---

## 📂 Structure des Fichiers

```text
serveur/
│
├── serveur_admin.py     # Serveur principal (Proxy Ollama + Panel Admin + Ban IP)
├── manuel_api.py        # Script optionnel pour répondre manuellement aux requêtes
├── log_ia.py            # Script simple de sauvegarde dans un fichier texte (historique.txt)
└── README.md            # Documentation du projet

🛠️ Prérequis

Assure-toi d'avoir installé sur ton système :

    Python 3.10+

    Ollama avec le modèle llama3 téléchargé (ollama pull llama3)

    Ngrok pour l'exposition sur Internet

Installation des dépendances Python

Dans ton terminal, exécute :
Bash

pip install flask requests

🚀 Démarrage Rapide

Pour faire tourner l'ensemble du système, tu dois ouvrir 3 terminaux :
1. Démarrer le moteur Ollama (Port Interne 11435)
Bash

OLLAMA_HOST=127.0.0.1:11435 ollama serve

2. Démarrer le Serveur Python (Port 11434)
Bash

python3 serveur_admin.py

3. Activer le tunnel Ngrok
Bash

ngrok http 11434

🌐 Utilisation & Navigation
📡 API Endpoint (pour le site web)

Renseigne l'URL Ngrok dans ton fichier JavaScript client :
JavaScript

const API_URL = "https://<votre-sous-domaine>.ngrok-free.dev/api/generate";

🛡️ Accès au Panel Admin

Ouvre ton navigateur et accède à la route /admin avec le mot de passe configuré :
Plaintext

https://<votre-sous-domaine>.ngrok-free.dev/admin?pwd=secret_hihi

Depuis cette interface, tu peux :

    Consulter les questions/réponses en direct.

    Saisir une IP pour la bannir immédiatement.

⚙️ Personnalisation

    Changer le mot de passe Admin : Dans serveur_admin.py, modifie la variable ADMIN_PASSWORD.

    Ajouter des mots-clés d'interception : Dans la fonction handle_api(), ajoute tes conditions personnalisées au niveau de la section DÉTECTION DIRECTE.

    Règles de l'IA : Modifie la variable system_prompt pour ajuster la personnalité du chatbot.
