#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
OUTIL INTERNE #09 — GESTION DE L'ÉTAT RUNTIME (PERSISTANCE PIDS & SERVICES)
========================================================================================
Permet de persister et de recharger les PIDs des processus lancés pour un arrêt garanti.
========================================================================================
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, Optional

from ..domain.entities_and_ports import IRuntimeStatePort


class JsonRuntimeStateAdapter(IRuntimeStatePort):
    def __init__(self, state_dir: Optional[Path] = None):
        if state_dir is None:
            self.state_dir = Path(__file__).resolve().parents[2] / "state"
        else:
            self.state_dir = state_dir
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.state_dir / "dev_runtime_state.json"

    def save_state(self, state: Dict[str, Any]) -> None:
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

    def load_state(self) -> Dict[str, Any]:
        if not self.state_file.exists():
            return {}
        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def clear_state(self) -> None:
        if self.state_file.exists():
            try:
                self.state_file.unlink()
            except Exception:
                pass
