# 🤖 Prompt d'Installation Automatique pour Agent IA — Outil #09 — Superviseur & Lanceur de Cycle de Vie Dev Multi-OS

> Ce fichier est destiné à être copié-collé directement dans le chat de votre assistant IA (Devin, Claude Code, Cursor, Windsurf, Antigravity IDE) pour installer, configurer et vérifier l'Outil #09 en un seul message.

---

`	ext
Tu es un agent d'ingénierie logicielle autonome chargé d'installer et de valider l'Outil #09 — Superviseur & Lanceur de Cycle de Vie Dev Multi-OS.

RÉPERTOIRE CIBLE : outils_internes/09_dev_lifecycle_launcher/
MOTEUR TECHNIQUE : Python 3.10+
RÔLE MÉTIER : Démarrage, arrêt et surveillance en temps réel des serveurs locaux BatiHome (FastAPI 8000 + Vite 3000) sous Windows et Linux avec diagnostics prêts pour LLM.

INSTRUCTIONS D'INSTALLATION ET DE PRISE EN MAIN :
1. Positionne-toi dans 'outils_internes/09_dev_lifecycle_launcher'.
2. Vérifie la présence des dépendances nécessaires ('requirements.txt' ou 'package.json') et installe-les si nécessaire.
3. Exécute la suite de tests officielle :
   run_tests.bat
   Vérifie que 100 % des tests passent sans aucune erreur.
4. Pour enregistrer ce serveur MCP dans mon environnement :
   - Commande d'installation automatique :
     python ../install_mcp.py --tool 09
   - Ou ajoute manuellement dans la configuration MCP de l'IDE :
     Serveur : '09-dev-lifecycle-launcher'
     Commande : 'python'
     Args : ['outils_internes/09_dev_lifecycle_launcher/canal_mcp/mcp_classic_stdio/mcp_server.py']
5. Effectue un appel test JSON-RPC 'tools/list' pour confirmer que les outils sont bien exposés.
6. Résume en 3 points : statut des tests, outils MCP disponibles, et validation fonctionnelle.

RÈGLE DE SÉCURITÉ : N'effectue aucune opération destructive et n'expose aucun secret.
`
