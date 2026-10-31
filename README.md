# mcp-09-dev-lifecycle-launcher

[![Pôle Stratégique](https://img.shields.io/badge/P%C3%B4le-01_POLE_CYBER_INFRA-blue.svg)](#)
[![Nature Commerciale](https://img.shields.io/badge/Nature-OUTIL-orange.svg)](#)
[![Visibilité](https://img.shields.io/badge/Visibilit%C3%A9-CODE-green.svg)](#)
[![Clean Architecture](https://img.shields.io/badge/Architecture-Clean%20Architecture%20Ports%20%26%20Adapters-teal.svg)](#)
[![Budget Lignes](https://img.shields.io/badge/R%C3%A8gle%20%235-%3C%20350%20Lignes%20Garanti-blueviolet.svg)](#)

> **OUTIL OPEN-SOURCE (Marketing Développeurs)**  
> Génération de notoriété technique et d'étoiles GitHub. Gestionnaire des ports FastAPI 8000 / Vite 3000, nettoyage des orphelins Windows & Linux.

---

## 1. Fiche d'Identité & Modèle Commercial

| Champ | Valeur Stratégique |
| :--- | :--- |
| **Composant** | `mcp-09-dev-lifecycle-launcher` |
| **Pôle d'Appartenance** | **Pôle 1 : Cybersécurité, Souveraineté & Infrastructure Cloud** |
| **Modèle Business** | **OUTIL OPEN-SOURCE (Marketing Développeurs)** |
| **Stratégie de Visibilité** | **CODE PUBLIC OPEN-SOURCE (MIT)** |
| **Potentiel Marché** | Génération de notoriété technique et d'étoiles GitHub. Gestionnaire des ports FastAPI 8000 / Vite 3000, nettoyage des orphelins Windows & Linux. |

---

## 2. Guide d'Installation 1-Clic (Développeur Humain)

```bash
git clone https://github.com/snorbik-ai/mcp-09-dev-lifecycle-launcher.git
cd mcp-09-dev-lifecycle-launcher
python install.py
```

Le script installe automatiquement les dépendances requises et résout les chemins de manière dynamique (**zéro chemin Windows absolu en dur**).

---

## 3. Configuration 1-Clic pour Agents IA (Cursor, Antigravity, Claude Code)

Ajoutez ce bloc à votre fichier `.mcp.json` ou `mcp_config.json` :

```json
{
  "mcpServers": {
    "mcp-09-dev-lifecycle-launcher": {
      "command": "python",
      "args": ["canal_mcp/mcp_classic_stdio/mcp_server.py"],
      "env": {
        "PYTHONIOENCODING": "utf-8"
      },
      "type": "stdio"
    }
  }
}
```

---

## 4. Catalogue Sémantique des Outils (`tools`)

| Outil (`name`) | Rôle & Fonction | Déclencheur d'Action (Quand l'appeler ?) | Arguments requis | Sortie Observable |
| :--- | :--- | :--- | :--- | :--- |
| `mcp_run_dev_tests` | Lance les suites de tests concurrentes et rapporte le bilan de santé du développement. | **Après toute modification fonctionnelle.** | `scope ('all'|'backend'|'frontend')` | Bilan chronométré |

---

## 5. Exemples Concrets de Prompts Utilisateur

Vous pouvez déclencher immédiatement ce composant en formulant ces requêtes dans votre IDE :

1. *« Lance la suite complète de tests de l'environnement de dev. »*
2. *« Nettoie les processus orphelins qui bloquent le port 8000. »*
3. *« Vérifie que le frontend Vite et le backend FastAPI communiquent normalement. »*

---

## 📜 Propriété & Licence
Composant officiel de l'écosystème **SNORBIK AI © 2026**.  
Tous droits réservés.
