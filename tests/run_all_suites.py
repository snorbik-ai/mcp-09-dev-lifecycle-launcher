#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import unittest
from pathlib import Path

_TOOL_ROOT = Path(__file__).resolve().parent.parent
if str(_TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(_TOOL_ROOT))


def run_all():
    loader = unittest.TestLoader()
    suite = loader.discover(str(_TOOL_ROOT / "tests"), pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    run_all()
