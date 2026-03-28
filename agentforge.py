#!/usr/bin/env python
import os

os.environ["PYTHONUTF8"] = "1"

from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    from src.main import app

    app()
