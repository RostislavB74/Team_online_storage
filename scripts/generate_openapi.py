import subprocess
import sys

# Run spectacular
python_exe = sys.executable  # ensures same venv is used

result = subprocess.run(
    [python_exe, "project_1444/manage.py", "spectacular", "--file", "openapi.yaml"], capture_output=True, text=True
)

# Print stdout/stderr if needed
print(result.stdout)
# Ignore warnings in stderr by not printing them, or filter lines
# For example, ignore lines containing "Warning: enum naming"
for line in result.stderr.splitlines():
    if "Warning:" not in line:
        print(line, file=sys.stderr)

# Exit if there was a real error
if result.returncode != 0:
    sys.exit(result.returncode)


# stage the file automatically
subprocess.run(["git", "add", "openapi.yaml"])
