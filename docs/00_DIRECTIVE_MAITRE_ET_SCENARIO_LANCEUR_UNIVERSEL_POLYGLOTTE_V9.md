# 🏛️ 00. DIRECTIVE MAÎTRE & SCÉNARIO SYSTÈME V9 : LANCEUR UNIVERSEL POLYGLOTTE MULTI-OS & MULTI-ROUTES (`09_dev_lifecycle_launcher` V2.0)

> **Identifiant du Scénario** : `SCN-MCP09-UNIVERSAL-POLYGLOT-LAUNCHER-V9`  
> **Cible d'Implémentation** : `outils_internes/09_dev_lifecycle_launcher/`  
> **Architecture Imposée** : Clean Architecture 4 Couches (`core/domain` $\leftarrow$ `core/application` $\leftarrow$ `core/infrastructure` $\leftarrow$ `canal_mcp` / `canal_sdk_cli`)  
> **Règle d'Or d'Indépendance OS** : **100 % Python Standard Library First (`sys`, `os`, `platform`, `subprocess`, `shutil`, `socket`, `urllib.request`, `pathlib`)**. Dès que Python est présent sur la machine, le MCP fonctionne de manière identique sous **Windows 10/11**, **Linux (Ubuntu/Debian/Alpine)** et **macOS** sans dépendre de scripts shell fragiles.

---

## 🎯 1. DIAGNOSTIC DE L'EXISTANT : QU'EST-CE QUI MANQUE DANS `09_dev_lifecycle_launcher` V1.0 ?

L'audit du code actuel de [`outils_internes/09_dev_lifecycle_launcher`](file:///C:/Users/ntpar/Dev_IT/Projet_depo/Projet_IA/ia-pilote-e_commerce_saas/01_e-commerce%20mat%C3%A9riel%20construction%20mvp/batihome-ecommerce-garde-corps/outils_internes/09_dev_lifecycle_launcher/core/application/use_cases.py) révèle **4 limitations critiques** que l'Assistant IA doit corriger et compléter :

1. **Commandes codées en dur (Non-Universel)** :
   - Dans [`use_cases.py`](file:///C:/Users/ntpar/Dev_IT/Projet_depo/Projet_IA/ia-pilote-e_commerce_saas/01_e-commerce%20mat%C3%A9riel%20construction%20mvp/batihome-ecommerce-garde-corps/outils_internes/09_dev_lifecycle_launcher/core/application/use_cases.py#L66-L70), les commandes `uvicorn backend.entrypoints.api.main:app` et `npm --prefix frontend run dev` ainsi que les ports `[8000, 3000]` sont écrits en dur. L'outil ne sait pas encore scanner et autodétecter un autre projet (Django, Flask, Next.js, Vue, Go, Rust, Docker...).
2. **Absence de Vérificateur et d'Auto-Installateur de Dépendances (`DependencyVerifier`)** :
   - Avant de démarrer un projet, l'outil ne vérifie pas si `node_modules/` est présent, si le `.venv` Python existe, ou si les paquets de `requirements.txt` / `pyproject.toml` / `package.json` sont installés.
3. **Ignorance des 7 Routes Officielles du Projet (3 Routes Front + 4 Routes Back/MCP/DB)** :
   - L'outil actuel ne sonde que 2 URLs (`http://127.0.0.1:8000/api/v1/health` et `http://localhost:3000/`). Il ignore l'existence des **3 Routes Front** (`#P01_home` / `#P04_configurateur`, `#dev`, `#console`) et des **4 Routes Back** (`/` & `/api/v1/health`, `/api/v1/mcp/registry`, `/docs`, `/api/v1/database`).
4. **Dossier `docs/` vide** :
   - Aucun scénario système ni contrat d'exécution n'était présent dans `outils_internes/09_dev_lifecycle_launcher/docs/`.

---

## 🧭 2. LES 7 ROUTES OFFICIELLES QUE LE MCP #09 DOIT CONNAÎTRE, SONDER ET OUVRIR

Lors du démarrage ou de l'audit (`audit_health` / `discover_routes`), le MCP `#09` doit exposer et vérifier **l'ensemble des 7 routes** (3 Front + 4 Back) :

### A. Les 3 Routes Côté Frontend (`http://localhost:3000`)

| ID Route | Nom de la Route Front | URL Exacte | Rôle Métier & Technique |
| :--- | :--- | :--- | :--- |
| **`FRONT_1_REAL`** | **Projet Réel E-Commerce & Configurateur 6 Étapes** | `http://localhost:3000/#P01_home` <br> `http://localhost:3000/#P04_configurateur` | Application cliente réelle AXESTEEL (`P01` à `P15`) avec le Configurateur en 6 étapes à gauche (`Modèle 1`) et l'Assistant IA à droite (`Modèle 2`). |
| **`FRONT_2_DEV`** | **Projet Dev Workbench (Laboratoire UI N1/N2/N3)** | `http://localhost:3000/#dev` <br> `http://localhost:3000/#/dev-workbench` | Laboratoire de composants UI isolés (`PrimitivesStory`, `ConfiguratorStory`, `MobileLabStory`, `MaquettesGalleryStory`). |
| **`FRONT_3_CONSOLE`** | **Console Pilote IA & Observabilité V9** | `http://localhost:3000/#console` <br> `http://localhost:3000/#/console-pilote` | Cockpit d'Observabilité V9 ([`CopilotCockpitStory.tsx`](file:///C:/Users/ntpar/Dev_IT/Projet_depo/Projet_IA/ia-pilote-e_commerce_saas/01_e-commerce%20mat%C3%A9riel%20construction%20mvp/batihome-ecommerce-garde-corps/frontend/src/workbench/stories/CopilotCockpitStory.tsx)) : affiche chronologiquement les **4 Parties de Logs**, les **6 Cartes Numérotées (`01` à `06`)**, les **17 Sous-Cartes Atomiques (`STP-01.1` à `STP-06.3`)** et le Panel Inspecteur (User Story + Code + JSON + Logs). |

### B. Les 4 Routes Côté Backend, MCP & Database (`http://127.0.0.1:8000`)

| ID Route | Nom de la Route Backend | URL Exacte | Rôle Métier & Technique |
| :--- | :--- | :--- | :--- |
| **`BACK_1_API`** | **Route Projet Backend (Portail & Santé)** | `http://127.0.0.1:8000/` <br> `http://127.0.0.1:8000/api/v1/health` | Portail racine JSON répertoriant toutes les routes actives + sonde de santé Clean Architecture 4 couches. |
| **`BACK_2_MCP`** | **Route MCP Attachée au Backend (Registre des 9 MCP & Traces)** | `http://127.0.0.1:8000/api/v1/mcp/registry` <br> `http://127.0.0.1:8000/api/v1/copilot/console/latest` | Liste les **9 outils MCP internes** (`01` à `09`), orchestre le MCP `#06` en direct sur `POST /api/copilot/turn` et expose la dernière trace V9 (`reponseconsole.json`). |
| **`BACK_3_DOCS`** | **Route API Doc (Swagger UI & ReDoc)** | `http://127.0.0.1:8000/docs` <br> `http://127.0.0.1:8000/redoc` | Documentation interactive OpenAPI 3.1 pour tester toutes les routes REST et contrats Pydantic. |
| **`BACK_4_DB`** | **Route Database (Inspecteur SQLite WAL `batihome.db`)** | `http://127.0.0.1:8000/api/v1/database` <br> `http://127.0.0.1:8000/api/v1/database/tables/copilot_turns` | Inspecteur temps réel de la base SQLite WAL : liste les 8 tables (`systemes`, `profils_vi_tree`, `devis`, `copilot_sessions`, `copilot_turns`, `copilot_step_traces`, `demandes_etude`, `contacts_sav`), le nombre de lignes et les derniers enregistrements. |

---

## 🧠 3. MOTEUR D'AUTO-DÉTECTION UNIVERSEL (LANGAGES, FRAMEWORKS, DÉPENDANCES & OS)

Pour que le MCP `#09` puisse démarrer **n'importe quel projet** (et pas seulement BatiHome), l'Assistant IA doit implémenter les 3 moteurs suivants en **Python pur** :

### Moteur 1 : `OsEnvironmentDetector` (Détection OS & Runtimes par Python)
Utilise uniquement `platform.system()`, `os.name`, `sys.executable` et `shutil.which()` :
- **Détection OS** :
  - `WINDOWS` (`os.name == 'nt'`) : résolution automatique des exécutables `.cmd` / `.exe` (`npm.cmd`, `pnpm.cmd`, `yarn.cmd`, `.venv/Scripts/python.exe`), libération des ports via `netstat -ano` + `taskkill /F /T /PID`.
  - `LINUX_DEBIAN_UBUNTU` / `LINUX_ALPINE` / `MACOS` (`os.name == 'posix'`) : résolution des binaires POSIX (`.venv/bin/python`, `npm`, `pnpm`), libération des ports via `fuser -k` ou `lsof -ti :PORT | xargs kill -9`.
- **Inventaire des Runtimes installés** : vérifie la disponibilité et la version de `python`, `node`, `npm`, `pnpm`, `yarn`, `bun`, `go`, `cargo`, `dotnet`, `java`, `docker`.

### Moteur 2 : `ProjectStackDetector` (Auto-Détection Polyglotte des Projets & Frameworks)
Scanne le dossier racine `project_root` et ses sous-dossiers (`backend/`, `frontend/`, `api/`, `web/`, `app/`, `src/`) pour détecter automatiquement :

| Famille | Fichiers Marqueurs Détectés | Frameworks Identifiés | Commande de Démarrage Standardisée (via Python `subprocess`) |
| :--- | :--- | :--- | :--- |
| **Python Backend / IA** | `requirements.txt`, `pyproject.toml`, `Pipfile`, `manage.py` | **FastAPI / Uvicorn**, **Django**, **Flask**, **Streamlit**, **FastMCP** | `[sys.executable, "-m", "uvicorn", "<entrypoint>:app", "--host", "127.0.0.1", "--port", "<port>", "--reload"]` (ou `manage.py runserver`, `streamlit run`) |
| **Frontend JS / TS** | `package.json` (`dependencies` / `scripts`) | **Vite + React/Vue**, **Express + TSX** (`server.ts`), **Next.js**, **Nuxt**, **Angular**, **Astro** | `[npm_bin, "--prefix", "<dir>", "run", "dev"]` |
| **Go / Rust / .NET / Java** | `go.mod`, `Cargo.toml`, `*.csproj`, `pom.xml` | **Go Gin/Fiber**, **Rust Actix/Axum**, **ASP.NET Core**, **Spring Boot** | `["go", "run", "."]`, `["cargo", "run"]`, `["dotnet", "run"]`, `["mvn", "spring-boot:run"]` |
| **Conteneurs** | `docker-compose.yml`, `compose.yaml` | **Docker Compose** | `["docker", "compose", "up", "-d"]` |

### Moteur 3 : `DependencyVerifierAndInstaller` (Vérification & Installation Automatique des Dépendances)
Avant chaque `spawn_service`, le moteur vérifie l'intégrité des dépendances :
1. **Côté Python** :
   - Détecte s'il existe un environnement virtuel local (`.venv`, `venv`) ou utilise `sys.executable`.
   - Vérifie si les modules clés du projet (`fastapi`, `uvicorn`, `pydantic`, etc.) sont importables via `[python_bin, "-c", "import fastapi, uvicorn"]`.
   - Si manquant et `auto_install_deps=True` : exécute `[python_bin, "-m", "pip", "install", "-r", "requirements.txt"]`.
2. **Côté Node.js / Frontend** :
   - Vérifie si le dossier `frontend/node_modules` existe et contient les binaires (`tsx`, `vite`).
   - Si `node_modules` est absent et `auto_install_deps=True` : exécute automatiquement `[npm_bin, "--prefix", "frontend", "install"]` avant de lancer le serveur.

---

## 🔄 4. SCÉNARIO SYSTÈME CHRONOLOGIQUE EN 6 ÉTAPES (AVEC USER STORIES)

```text
[Agent IA / Développeur]
       │
       ▼ (Appel MCP `run_agent_lifecycle` ou CLI `python cli.py start --target console`)
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ÉTAPE 01 (STP-L01) : AUTO-DÉTECTION OS, RUNTIMES & STACK POLYGLOTTE (`detect_project_stack`)    │
│ • Détecte l'OS (Windows / Linux Debian-Ubuntu / macOS) via Python pur.                          │
│ • Scanne le projet et identifie : Backend Python FastAPI (:8000) + Frontend Express/Vite (:3000)│
│ • Recense les 7 Routes Officielles (3 Front + 4 Back/MCP/DB).                                   │
└──────────────────────────────────────────────────┬──────────────────────────────────────────────┘
                                                   ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ÉTAPE 02 (STP-L02) : AUDIT & INSTALLATION DES DÉPENDANCES (`verify_and_install_dependencies`)   │
│ • Vérifie les paquets Python (`requirements.txt`) et Node (`frontend/node_modules`).            │
│ • Installe automatiquement ce qui manque si `auto_install_deps=True`.                           │
└──────────────────────────────────────────────────┬──────────────────────────────────────────────┘
                                                   ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ÉTAPE 03 (STP-L03) : NETTOYAGE MULTI-OS DES PORTS ORPHELINS (`clean_ports`)                     │
│ • Libère proprement les ports cibles (8000, 3000) sans tuer les processus système.              │
└──────────────────────────────────────────────────┬──────────────────────────────────────────────┘
                                                   ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ÉTAPE 04 (STP-L04) : DÉMARRAGE SUPERVISÉ PAR MOTEUR PYTHON COMMUN (`spawn_services`)            │
│ • Démarre chaque service détecté via `subprocess.Popen` avec draineur de logs asynchrone.       │
│ • Enregistre les PIDs, commandes et routes dans `state/dev_runtime_state.json`.                 │
└──────────────────────────────────────────────────┬──────────────────────────────────────────────┘
                                                   ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ÉTAPE 05 (STP-L05) : SONDES DE SANTÉ SUR LES 7 ROUTES (`poll_all_routes_health`)                │
│ • Vérifie la disponibilité des 4 Routes Backend (`/`, `/api/v1/mcp/registry`, `/docs`,          │
│   `/api/v1/database`) et des 3 Routes Frontend (`/#P01_home`, `/#dev`, `/#console`).            │
└──────────────────────────────────────────────────┬──────────────────────────────────────────────┘
                                                   ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ÉTAPE 06 (STP-L06) : ROUTAGE CIBLÉ NAVIGATEUR OU DIGEST D'ERREUR LLM-READY                      │
│ • Si HEALTHY : retourne la carte complète des 7 Routes et ouvre la route demandée               │
│   (`target_route = "real" | "dev" | "console" | "api_docs" | "database" | "mcp"`).              │
│ • Si CRASHED : génère `output/last_error_diagnostic.json` avec cause racine et remède exact.    │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```
