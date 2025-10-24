import os
import sys
import django
from django.core.wsgi import get_wsgi_application

try:
    import yaml
except ImportError as e:
    print(f"ImportError: {e}. Please install PyYAML using 'pip install pyyaml'.")
    sys.exit(1)
from dotenv import load_dotenv

# Додаємо корінь проєкту до sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "project_1444")))

# Завантажуємо .env
load_dotenv()

# Встановлюємо DJANGO_SETTINGS_MODULE
os.environ["DJANGO_SETTINGS_MODULE"] = "project_1444.settings"

# Ініціалізуємо Django
try:
    django.setup()
    application = get_wsgi_application()
except Exception as e:
    print(f"Failed to initialize Django: {e}. Ensure all INSTALLED_APPS modules are installed.")
    sys.exit(1)

# Імпортуємо drf_spectacular
try:
    from drf_spectacular.openapi import AutoSchema
    from drf_spectacular.generators import SchemaGenerator
except ImportError as e:
    print(f"ImportError: {e}. Ensure drf-spectacular is installed.")
    sys.exit(1)


def generate_openapi_schema():
    if os.getenv("GENERATE_OPENAPI", "True").lower() != "true":
        print("Not generating openapi by env settings")
        return

    generator = SchemaGenerator(
        title="Jewelry Store API",
        description="API for jewelry store with products, categories, and more",
        version="1.0.0",
        url=None,  # Базовий URL береться з SPECTACULAR_SETTINGS["SERVERS"]
    )
    schema = generator.get_schema(request=None, public=True)
    output_path = os.path.join(os.path.dirname(__file__), "../schema.yaml")
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(schema, f, allow_unicode=True, sort_keys=False)
    print(f"OpenAPI schema generated at {output_path}")

    # Додаємо schema.yaml до git
    import subprocess

    subprocess.run(["git", "add", output_path])


if __name__ == "__main__":
    generate_openapi_schema()
# import os
# import subprocess
# import sys

# import dotenv

# # Run spectacular
# load_dotenv = dotenv.load_dotenv()

# if os.environ.get("GENERATE_OPENAPI", "false").lower() != "true":
#     print("Not generating openapi by env settings")
#     sys.exit(0)

# python_exe = sys.executable  # ensures same venv is used

# PROJECT_NAME = "project_1444"
# OPENAPI_FILE = os.environ.get("OPENAPI_FILE", f"{PROJECT_NAME}/schema.yaml")

# result = subprocess.run(
#     [python_exe, f"{PROJECT_NAME}/manage.py", "spectacular", "--file", OPENAPI_FILE],
#     capture_output=True,
#     text=True,
# )

# # Print stdout/stderr if needed
# print(result.stdout)
# # Ignore warnings in stderr by not printing them, or filter lines
# # For example, ignore lines containing "Warning: enum naming"
# for line in result.stderr.splitlines():
#     if "Warning:" not in line:
#         print(line, file=sys.stderr)

# # Exit if there was a real error
# if result.returncode != 0:
#     sys.exit(result.returncode)


# # stage the file automatically
# subprocess.run(["git", "add", OPENAPI_FILE])
