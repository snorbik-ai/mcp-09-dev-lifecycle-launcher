# mcp-09-dev-lifecycle-launcher

[![Pôle Stratégique](https://img.shields.io/badge/P%C3%B4le-01_POLE_CYBER_INFRA-blue.svg)](#)
[![Nature](https://img.shields.io/badge/Nature-OUTIL-orange.svg)](#)
[![Visibilité](https://img.shields.io/badge/Visibilit%C3%A9-CODE-green.svg)](#)
[![Version](https://img.shields.io/badge/Version-1.0.0-purple.svg)](#)
[![Standard](https://img.shields.io/badge/Standard-V14.1%20Clean%20Architecture-teal.svg)](#)

> **OUTIL OPEN-SOURCE (Marketing Développeurs)**  
> Superviseur de cycle de vie de développement local qui gère les processus orphelins, surveille les ports (FastAPI 8000 et Vite 3000) et synchronise l'environnement sous Windows et Ubuntu Linux.

---

## 1. Carte d'Identité & Rôle Métier

| Champ Stratégique | Valeur Officielle |
| :--- | :--- |
| **Composant Officiel** | `mcp-09-dev-lifecycle-launcher` |
| **Pôle d'Appartenance** | **Pôle 1 : Cybersécurité, Souveraineté & Infrastructure Cloud** |
| **Modèle Business** | **OUTIL OPEN-SOURCE (Marketing Développeurs)** |
| **Politique de Visibilité** | **CODE PUBLIC OPEN-SOURCE (MIT)** |
| **Mission Principale** | Superviseur de cycle de vie de développement local qui gère les processus orphelins, surveille les ports (FastAPI 8000 et Vite 3000) et synchronise l'environnement sous Windows et Ubuntu Linux. |
| **Architecture** | Clean Architecture Tri-Canal (STDIO / CLI / SDK In-Process) |

---

## 2. Guide d'Installation 1-Clic

### Option A : Installation Automatisée 1-Clic (Recommandée)
Exécutez simplement le script `install.py` à la racine du dépôt :

```bash
python install.py
```

Ce script effectue automatiquement :
1. La vérification de votre environnement Python (>= 3.10).
2. L'installation des dépendances requises en mode éditable (`pip install -e .` ou `npm install`).
3. La détection et l'injection automatique du serveur dans la configuration de Cursor (`%USERPROFILE%/.cursor/mcp.json`) sans écraser vos autres outils.

### Option B : Installation Manuelle Développeur
```bash
pip install -e .
```

---

## 3. Configuration Manuelle (Cursor, Antigravity, Claude Desktop)

Si vous préférez déclarer manuellement ce serveur dans votre fichier `.cursor/mcp.json` ou `mcp_config.json`, ajoutez le bloc suivant :

```json
{
  "mcpServers": {
    "mcp-09-dev-lifecycle-launcher": {
      "command": "python",
      "args": ["canal_mcp/mcp_classic_stdio/mcp_server.py"],
      "env": { "PYTHONIOENCODING": "utf-8" },
      "type": "stdio"
    }
  }
}
```

---

## 4. Catalogue Sémantique des Outils (`tools`)

Ce composant expose des outils déterministes prêts à être invoqués par un modèle de langage (LLM) :

| Nom de l'Outil (`tool`) | Rôle & Fonction Technique | Déclencheur d'Action (*Quand l'IA DOIT-ELLE l'appeler ?*) | Paramètres Requis | Sortie Retournée |
| :--- | :--- | :--- | :--- | :--- |
| `mcp_check_dev_environment` | Vérifie les ports occupés (8000, 3000, 5432) et la cohérence de l'environnement Python/Node sous Windows et WSL/Linux. | **Au démarrage d'une session de dev ou quand un port est signalé comme déjà utilisé.** | `aucun` | Tableau de bord des ports, PIDs des processus associés et compatibilité OS. |
| `mcp_kill_orphan_processes` | Termine proprement les processus fantômes (node.exe, python.exe) qui bloquent les ports de dev. | **Dès qu'un serveur de développement ne peut pas démarrer suite à un crash précédent.** | `ports (list[int], optionnel)` | Liste des PIDs tués et confirmation de libération des sockets réseau. |
| `mcp_start_dev_services` | Démarre en tâche de fond le serveur FastAPI backend et le serveur Vite frontend avec logs unifiés. | **Quand l'utilisateur demande de lancer l'environnement de développement local.** | `reload (bool, optionnel)` | Statut de démarrage et URLs locales d'accès. |

---

## 5. Exemples Concrets de Prompts Utilisateur

Voici 3 exemples réels de requêtes que vous pouvez poser directement dans le chat de Cursor ou Claude Code pour faire travailler cet outil :

1. *« Vérifie si les ports 8000 et 3000 sont libres pour lancer mon application. »*
2. *« Tue tous les processus Node et Python orphelins qui bloquent mes serveurs de dev. »*
3. *« Démarre le backend FastAPI et le frontend Vite en mode développement avec surveillance des ports. »*

---

## 🛡️ Propriété Intellectuelle & Sécurité
- **Éditeur :** SNORBIK AI © 2026.
- **Classification :** Conforme à la Directive Maîtresse V14.1 (Recettes d'architecture sanctuarisées dans le Pôle 06).
- **Zéro Régression :** Respect strict des budgets de lignes et des normes de sécurité.


## 🤖 Prompt d'Installation Agent-Native (Copier-Coller pour votre Agent IA)

```markdown
Je souhaite installer et activer le serveur MCP `mcp-09-dev-lifecycle-launcher` dans mon environnement de travail.

1. Détecte mon client de code (Cursor, VS Code, Claude Code, ou Claude Desktop).
2. Lance l'installateur multi-clients :
   python install.py --client all
3. Vérifie que le serveur est bien enregistré et exécute un test de connexion stdio :
   python -m pytest tests/test_mcp_integration.py
```
