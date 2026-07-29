from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REQUIREMENTS = ROOT / "requirements.txt"
REQUIRED_MODULES = ("uvicorn", "fastapi", "openai", "anthropic", "google.genai", "yaml", "requests")


def missing_modules() -> list[str]:
    missing: list[str] = []
    for name in REQUIRED_MODULES:
        try:
            available = importlib.util.find_spec(name) is not None
        except ModuleNotFoundError:
            available = False
        if not available:
            missing.append(name)
    return missing


def bootstrap() -> None:
    missing = missing_modules()
    if not missing:
        return
    print(f"[API bootstrap] Missing Python modules: {', '.join(missing)}", flush=True)
    print(f"[API bootstrap] Repairing pip in {sys.executable}...", flush=True)
    subprocess.run([sys.executable, "-m", "ensurepip", "--upgrade"], check=True)
    print(f"[API bootstrap] Installing {REQUIREMENTS}...", flush=True)
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS)], check=True)
    remaining = missing_modules()
    if remaining:
        raise RuntimeError(f"Dependency bootstrap incomplete: {', '.join(remaining)}")


def main() -> None:
    bootstrap()
    os.chdir(ROOT)
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    import uvicorn
    from web.backend.main import app
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
