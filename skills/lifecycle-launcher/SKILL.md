---
name: mcp-09-lifecycle-launcher
description: Serveur MCP Dev Lifecycle Launcher : Supervision des ports (8000, 3000), élimination des orphelins et synchro multi-OS.
---

# 🧬 SKILL ADN : MCP-09-LIFECYCLE-LAUNCHER
> **Classification :** Noyau Opérationnel Standardisé Snorbik AI (Directive Master V2.0)  
> **Mission :** Serveur MCP Dev Lifecycle Launcher : Supervision des ports (8000, 3000), élimination des orphelins et synchro multi-OS.

---

## 1. Identité & Mission Critique

- **Nom officiel du Skill :** `mcp-09-lifecycle-launcher`
- **Rôle Fonctionnel :** Ce skill encapsule l'ADN technique, les règles de décision et les invariants opérationnels pour le sous-système `mcp-09-lifecycle-launcher`.
- **Déclencheur d'Activation :** Ce skill est activé dès qu'une IA ou un développeur intervient sur le périmètre correspondant ou traite des tâches de cette compétence.

---

## 2. Invariants Absolus & Interdictions (Vaccins)

Les règles suivantes sont formellement obligatoires et ne souffrent aucune dérogation :

- **INV-01 :** Compatibilité garantie Windows 11 et Ubuntu Linux / WSL.
- **INV-02 :** Arrêt propre (SIGTERM) avant terminaison forcée (SIGKILL) des processus fantômes.
- **INV-03 :** Garantie de ports toujours disponibles pour les serveurs de développement.

---

## 3. Protocole d'Exécution Pas-à-Pas

Pour accomplir les missions de ce skill avec 100% de réussite :

1. Vérifier la disponibilité des ports 8000 et 3000 (mcp_check_dev_environment).
2. Tuer les processus orphelins si nécessaire (mcp_kill_orphan_processes).
3. Démarrer les services FastAPI et Vite avec logs unifiés.

---

## 4. Cartographie des Outils MCP & Scripts

Ce skill pilote et s'appuie sur les outils d'ingénierie suivants :

- `mcp_check_dev_environment`
- `mcp_kill_orphan_processes`
- `mcp_start_dev_services`

---

## 5. Résilience, Erreurs Fréquentes & Fallback

- Si socket bloquée au niveau de l'OS, forcer le recyclage du pool réseau local.

---

## 6. Procédure de Mutation (Enrichissement de l'ADN)

Prise en charge de nouveaux ports applicatifs lors de l'extension de l'architecture.

---
*Scellé et certifié conforme par la Gouvernance Génomique Snorbik AI © 2026.*
