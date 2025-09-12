from pathlib import Path
import environ
# from .settings_base import env  # якщо ти вже користуєшся django-environ
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(BASE_DIR.parent / ".env")

