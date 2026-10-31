# 🧭 01. CARTOGRAPHIE DES 7 ROUTES OFFICIELLES & PLAN D'IMPLÉMENTATION POUR L'AGENT IA (`09_dev_lifecycle_launcher` V2.0)

> **Document d'Exécution Directe pour l'Agent IA Codeur**  
> **Objectif** : Fournir à l'Assistant IA le plan fichier par fichier, les signatures exactes des classes et méthodes à ajouter dans `outils_internes/09_dev_lifecycle_launcher`, ainsi que le catalogue des **7 Routes (3 Front + 4 Back)** et des règles de détection multi-projets / multi-OS.

---

## 📋 1. TABLEAU DE RÉFÉRENCE DES 7 ROUTES DU PROJET (À INTÉGRER DANS LE CODE DU MCP #09)

L'Agent IA doit ajouter cette table de routage canonique dans le domaine de `09_dev_lifecycle_launcher` afin que l'outil `discover_routes`, la commande `cli.py routes`, et l'action `start_services(target_route=...)` retournent et vérifient systématiquement ces **7 points d'entrée** :

```python
OFFICIAL_PROJECT_ROUTES = {
    "frontend_routes": {
        "1_projet_reel": {
            "id": "FRONT_1_REAL",
            "label": "Projet Réel E-Commerce & Configurateur 6 Étapes",
            "url_home": "http://localhost:3000/#P01_home",
            "url_configurator": "http://localhost:3000/#P04_configurateur",
            "port": 3000,
            "probe_url": "http://localhost:3000/",
            "description": "Site client AXESTEEL (P01 à P15) avec Configurateur 6 étapes à gauche (Modèle 1) et Assistant IA à droite (Modèle 2)."
        },
        "2_projet_dev_workbench": {
            "id": "FRONT_2_DEV",
            "label": "Projet Dev Workbench (Laboratoire Composants N1/N2/N3)",
            "url": "http://localhost:3000/#dev",
            "alias_url": "http://localhost:3000/#/dev-workbench",
            "port": 3000,
            "probe_url": "http://localhost:3000/",
            "description": "Banc d'essai isolé des composants atomiques, Mobile Lab et Galerie Maquettes."
        },
        "3_console_pilote_ia": {
            "id": "FRONT_3_CONSOLE",
            "label": "Console Pilote IA & Observabilité V9 (4 Parties de Logs)",
            "url": "http://localhost:3000/#console",
            "alias_url": "http://localhost:3000/#/console-pilote",
            "port": 3000,
            "probe_url": "http://localhost:3000/api/v1/copilot/console/latest",
            "description": "Cockpit Console IA V9 affichant les 6 Cartes Numérotées (01 à 06), les 17 Sous-Cartes Atomiques (STP-01.1 à STP-06.3) et le Panel Inspecteur."
        }
    },
    "backend_routes": {
        "1_projet_backend_root": {
            "id": "BACK_1_API",
            "label": "Portail Projet Backend & Sonde Health",
            "url_root": "http://127.0.0.1:8000/",
            "url_health": "http://127.0.0.1:8000/api/v1/health",
            "port": 8000,
            "probe_url": "http://127.0.0.1:8000/api/v1/health",
            "description": "Portail JSON récapitulatif des routes et état de santé du serveur FastAPI Clean 4-Layers."
        },
        "2_mcp_hub_attached": {
            "id": "BACK_2_MCP",
            "label": "Hub MCP Attaché au Backend (Registre des 9 MCP & Orchestrateur #06)",
            "url_registry": "http://127.0.0.1:8000/api/v1/mcp/registry",
            "url_turn_endpoint": "http://127.0.0.1:8000/api/copilot/turn",
            "url_latest_trace": "http://127.0.0.1:8000/api/v1/copilot/console/latest",
            "port": 8000,
            "probe_url": "http://127.0.0.1:8000/api/v1/mcp/registry",
            "description": "Registre actif des 9 outils MCP internes rattachés au backend FastAPI et trace temps réel."
        },
        "3_api_docs_openapi": {
            "id": "BACK_3_DOCS",
            "label": "Documentation API Interactive (Swagger UI & ReDoc)",
            "url_swagger": "http://127.0.0.1:8000/docs",
            "url_redoc": "http://127.0.0.1:8000/redoc",
            "port": 8000,
            "probe_url": "http://127.0.0.1:8000/docs",
            "description": "Interface OpenAPI 3.1 pour tester toutes les routes REST, MCP et schémas Pydantic."
        },
        "4_database_sqlite_inspector": {
            "id": "BACK_4_DB",
            "label": "Inspecteur Database SQLite WAL (batihome.db)",
            "url_inspector": "http://127.0.0.1:8000/api/v1/database",
            "url_turns_table": "http://127.0.0.1:8000/api/v1/database/tables/copilot_turns",
            "port": 8000,
            "probe_url": "http://127.0.0.1:8000/api/v1/database",
            "description": "Inspection directe des 8 tables SQLite WAL, compteurs de lignes et derniers enregistrements."
        }
    }
}
```

---

## 🛠️ 2. PLAN D'IMPLÉMENTATION FICHIER PAR FICHIER POUR L'ASSISTANT IA

L'Assistant IA doit suivre cet ordre strict (Clean Architecture) pour mettre à niveau `outils_internes/09_dev_lifecycle_launcher` :

### Étape 1 — Enrichir `core/domain/entities_and_ports.py`
Ajouter les nouvelles entités et ports abstraits suivants :
1. **`OsPlatformProfile`** (`dataclass`) :
   - `os_family`: `"WINDOWS" | "LINUX_DEBIAN" | "LINUX_OTHER" | "MACOS"`
   - `platform_release`: `str`
   - `python_executable`: `str` (`sys.executable`)
   - `python_version`: `str`
   - `available_runtimes`: `Dict[str, Optional[str]]` (chemins résolus via `shutil.which` pour `node`, `npm`, `pnpm`, `yarn`, `go`, `cargo`, `docker`)
2. **`DetectedServiceConfig`** (`dataclass`) :
   - `service_id`: `str` (ex: `"backend"`, `"frontend"`)
   - `language`: `str` (ex: `"python"`, `"typescript"`, `"go"`, `"rust"`)
   - `framework`: `str` (ex: `"fastapi"`, `"django"`, `"flask"`, `"vite_express"`, `"nextjs"`)
   - `working_dir`: `str`
   - `start_command`: `List[str]`
   - `port`: `int`
   - `health_url`: `str`
   - `dependencies_ok`: `bool`
   - `missing_dependencies_hint`: `Optional[str]`
3. **`ProjectBlueprintReport`** (`dataclass`) :
   - `project_root`: `str`
   - `os_profile`: `OsPlatformProfile`
   - `detected_services`: `List[DetectedServiceConfig]`
   - `routes_catalog`: `Dict[str, Any]` (contenant les **3 Routes Front** et **4 Routes Back**)
4. **Nouveaux Ports Abstraits** :
   - `IStackDetectorPort` : `detect_project_blueprint(project_root: str) -> ProjectBlueprintReport`
   - `IDependencyManagerPort` : `verify_and_install(service: DetectedServiceConfig, auto_install: bool = True) -> Dict[str, Any]`

---

### Étape 2 — Créer `core/infrastructure/stack_detector.py` (NOUVEAU FICHIER)
Implémenter `PolyglotStackDetectorAdapter(IStackDetectorPort)` et `UniversalDependencyManagerAdapter(IDependencyManagerPort)` en **100 % Python standard** :

1. **Détection Multi-OS sans dépendance externe** :
   - Utilise `os.name`, `platform.system()`, `platform.release()`.
   - Sur Linux, lit `/etc/os-release` s'il existe pour identifier `Ubuntu`, `Debian`, `Alpine`, etc.
   - Sur Windows, résout automatiquement `npm.cmd`, `npx.cmd`, `pnpm.cmd` pour éviter l'erreur classique `FileNotFoundError: [WinError 2]` de `subprocess.Popen` quand `shell=False`.
2. **Détection Polyglotte de N'importe Quel Projet** :
   - **Règle Python** :
     - Cherche un interpréteur local `.venv/Scripts/python.exe` (Windows) ou `.venv/bin/python` (Linux/macOS), sinon replie sur `sys.executable`.
     - Scanne `backend/entrypoints/api/main.py`, `backend/main.py`, `main.py`, `app.py`, `manage.py`.
     - Identifie `FastAPI` (commande `python -m uvicorn ...`), `Django` (`python manage.py runserver`), `Flask` (`python -m flask run`), `Streamlit` (`python -m streamlit run`).
   - **Règle Frontend / Node.js** :
     - Scanne `frontend/package.json` ou `package.json` à la racine.
     - Inspecte `scripts.dev` et `dependencies` (`vite`, `express`, `tsx`, `next`, `nuxt`, `react`, `vue`, `@angular/core`).
     - Construit la commande multiplateforme `[npm_bin, "--prefix", "frontend", "run", "dev"]`.
   - **Règle Go / Rust / Docker** :
     - Si `go.mod` ➔ `["go", "run", "."]`
     - Si `Cargo.toml` ➔ `["cargo", "run"]`
     - Si `docker-compose.yml` (et aucun runtime natif) ➔ `["docker", "compose", "up", "-d"]`
3. **Vérification & Auto-Installation des Dépendances (`verify_and_install`)** :
   - Pour Python : teste `[python_bin, "-c", "import fastapi, uvicorn, pydantic"]`. Si `returncode != 0` et `auto_install=True`, lance `[python_bin, "-m", "pip", "install", "-r", "requirements.txt"]`.
   - Pour Node.js : vérifie `(Path(working_dir) / "node_modules").exists()`. Si absent et `auto_install=True`, lance `[npm_bin, "--prefix", working_dir, "install"]`.

---

### Étape 3 — Mettre à jour `core/application/use_cases.py`
1. Mettre à jour `StartDevServicesUseCase.execute()` :
   - Utiliser `stack_detector.detect_project_blueprint(project_root)` au lieu de coder les commandes uniquement en dur.
   - Appeler `dependency_mgr.verify_and_install(...)` avant le démarrage si `verify_deps=True`.
   - Permettre de choisir quelle route ouvrir dans le navigateur via `target_route: str = "real"` :
     - `"real"` ➔ `http://localhost:3000/#P01_home`
     - `"configurator"` ➔ `http://localhost:3000/#P04_configurateur`
     - `"dev"` ➔ `http://localhost:3000/#dev`
     - `"console"` ➔ `http://localhost:3000/#console`
     - `"api_docs"` ➔ `http://127.0.0.1:8000/docs`
     - `"database"` ➔ `http://127.0.0.1:8000/api/v1/database`
     - `"mcp"` ➔ `http://127.0.0.1:8000/api/v1/mcp/registry`
   - Retourner dans la réponse JSON la clé `"routes": OFFICIAL_PROJECT_ROUTES` pour que l'agent IA ou l'utilisateur voie immédiatement les **7 routes disponibles**.
2. Mettre à jour `AuditHealthUseCase.execute()` :
   - Sonder non seulement `/api/v1/health` et `http://localhost:3000/`, mais également vérifier l'état des **4 Routes Backend** (`/`, `/api/v1/mcp/registry`, `/docs`, `/api/v1/database`) et retourner le statut détaillé des **7 routes**.
3. Ajouter `DetectProjectStackAndRoutesUseCase` :
   - Nouveau Use Case permettant à un agent IA d'inspecter n'importe quel dépôt (`detect_stack_and_routes`) pour connaître son OS, ses langages, l'état de ses dépendances et ses 7 routes avant même de démarrer.

---

### Étape 4 — Mettre à jour `canal_sdk_cli/sdk.py`, `canal_sdk_cli/cli.py` et `canal_mcp/mcp_classic_stdio/mcp_server.py`
1. Dans [`mcp_server.py`](file:///C:/Users/ntpar/Dev_IT/Projet_depo/Projet_IA/ia-pilote-e_commerce_saas/01_e-commerce%20mat%C3%A9riel%20construction%20mvp/batihome-ecommerce-garde-corps/outils_internes/09_dev_lifecycle_launcher/canal_mcp/mcp_classic_stdio/mcp_server.py) :
   - Ajouter les actions `"detect_stack_and_routes"` et `"verify_dependencies"` dans `run_agent_lifecycle`.
   - Ajouter le paramètre optionnel `"target_route"` (`"real" | "configurator" | "dev" | "console" | "api_docs" | "database" | "mcp"`).
2. Dans [`cli.py`](file:///C:/Users/ntpar/Dev_IT/Projet_depo/Projet_IA/ia-pilote-e_commerce_saas/01_e-commerce%20mat%C3%A9riel%20construction%20mvp/batihome-ecommerce-garde-corps/outils_internes/09_dev_lifecycle_launcher/canal_sdk_cli/cli.py) :
   - Ajouter les sous-commandes :
     - `python cli.py routes` : affiche clairement les **3 Routes Front** et les **4 Routes Back/MCP/DB**.
     - `python cli.py detect` : affiche l'auto-détection OS + Frameworks + Dépendances.
     - `python cli.py start --route console` : démarre tout et ouvre directement la route choisie.

---

## 💬 3. PROMPT DIRECTIVE PRÊT À COPIER-COLLER POUR VOTRE ASSISTANT IA

Si vous souhaitez demander à votre assistant IA d'exécuter ou d'étendre ce module, donnez-lui simplement cette instruction :

```markdown
Tu dois implémenter et maintenir le 9e outil MCP `outils_internes/09_dev_lifecycle_launcher` en suivant strictement les 2 documents de spécification :
1. `outils_internes/09_dev_lifecycle_launcher/docs/00_DIRECTIVE_MAITRE_ET_SCENARIO_LANCEUR_UNIVERSEL_POLYGLOTTE_V9.md`
2. `outils_internes/09_dev_lifecycle_launcher/docs/01_CARTOGRAPHIE_7_ROUTES_ET_PLAN_IMPLEMENTATION_AGENT_IA.md`

Règles impératives :
- 100 % Python Standard Library First : utilise Python comme socle universel multi-OS (Windows 10/11, Linux Debian/Ubuntu, macOS).
- Auto-détecte les langages, frameworks (FastAPI, Django, Flask, Vite, Express, Next.js, Go, Rust) et vérifie/installe les dépendances manquantes avant de lancer les serveurs.
- Expose et sonde systématiquement les 7 Routes Officielles :
  - 3 Routes Front : `1_projet_reel` (`/#P01_home`, `/#P04_configurateur`), `2_projet_dev_workbench` (`/#dev`), `3_console_pilote_ia` (`/#console`).
  - 4 Routes Back : `1_projet_backend_root` (`/`, `/api/v1/health`), `2_mcp_hub_attached` (`/api/v1/mcp/registry`), `3_api_docs_openapi` (`/docs`), `4_database_sqlite_inspector` (`/api/v1/database`).
- Vérifie que tous les tests unitaires dans `outils_internes/09_dev_lifecycle_launcher/tests/` passent à 100 %.
```
