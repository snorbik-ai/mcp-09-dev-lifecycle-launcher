#!/usr/bin/env python3
import sys, os, json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
print("[*] Installation autonome de mcp-09-dev-lifecycle-launcher...")
if (ROOT / "requirements.txt").exists():
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], cwd=str(ROOT), check=False)
elif (ROOT / "package.json").exists():
    subprocess.run(["npm", "install"], cwd=str(ROOT), check=False)

print("[+] Prêt à l'emploi.")
