#!/usr/bin/env python
import os
import sys
from pathlib import Path

# Ensure `src/` is on PYTHONPATH
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

def main():
    default_settings = "config.settings.prod" if (os.environ.get("RENDER") or os.environ.get("DJANGO_ENV") == "production") else "config.settings.dev"
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", default_settings)
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()
