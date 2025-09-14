ARG PYTHON_VER="3.12"

######## LAYER0
FROM python:${PYTHON_VER}-slim AS layer0

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wget curl \
    pkg-config && \
    apt-get clean -y && apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

######## BUILDER OF PYTHON APP
FROM layer0 AS builder

RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements*.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt --no-cache-dir && \
    pip install -r requirements-dev.txt --no-cache-dir

######## Main application stage

FROM layer0

ARG _USER=appuser
ARG _GROUP=appgroup
ARG _MEDIA_DIR="/app/src/media /app/src/static /app/data /app/.ruff_cache /var/log/celery /var/run/celery"


RUN groupadd ${_GROUP} && useradd --no-log-init -r --no-create-home -G ${_GROUP} ${_USER}  && \
    mkdir -p ${_MEDIA_DIR} && chown -R ${_USER}:${_GROUP} ${_MEDIA_DIR}

# Copy venv from previous stage "builder"
COPY --from=builder /opt/venv /opt/venv

WORKDIR /app


# copy src
COPY --chown=${_USER}:${_GROUP} ./dockers/commands/ commands/
COPY --chown=${_USER}:${_GROUP} ./project_1444 project_1444/

# swicth to runtime user
USER ${_USER}

ENV PATH="/opt/venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=./src

# CMD ["/bin/bash", "-c", "/app/commands/entrypoint.sh"]
# ENTRYPOINT = ["/bin/bash"]
CMD ["/bin/bash", "-c", "/app/commands/entrypoint.sh"]
