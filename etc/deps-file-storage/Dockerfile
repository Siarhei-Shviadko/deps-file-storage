ARG REPOSITORY_URL=""
FROM ${REPOSITORY_URL:+$REPOSITORY_URL/base/}python:3.12.11-slim AS python-base

ENV PIP_NO_CACHE_DIR=off \
    PYTHONUNBUFFERED=1 \
    LC_ALL=C \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_PATH=/opt/poetry \
    VENV_PATH=/app/.venv \
    PYTHONPATH="$PYTHONPATH:/app" \
    LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/lib"
ENV PATH="$VENV_PATH/bin:$POETRY_PATH/bin:$PATH"

# runtime needs this for magic python-magic
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libmagic-dev


FROM python-base as poetry

ARG USER=deps
ARG MEDIA_DIR=/media

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    # deps for installing poetry
    curl \
    # deps for building python deps
    build-essential \
    && apt-get remove unzip -y \
    # Install Poetry
    && pip install pip==21.2.4 \
    && curl -sSL https://install.python-poetry.org | POETRY_HOME=$POETRY_PATH python3 - \
    && poetry --version \
    && poetry config virtualenvs.in-project true \
    && chmod +x $POETRY_PATH/bin/poetry \
    # create new user and give him access to volumes
    && useradd -Ms /bin/bash $USER \
    && mkdir -p $MEDIA_DIR/files \
    && chown -R $USER:$USER $MEDIA_DIR \
    && mkdir -p /tmp/test_cache \
    && chown -R $USER:$USER /tmp/test_cache

FROM poetry as build

WORKDIR /app/

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./src/pyproject.toml ./src/poetry.lock* /app/

# Allow installing dev dependencies to run tests
COPY ./vendors /vendors

RUN poetry install --no-interaction --no-ansi --no-root --only main

FROM build as develop

RUN poetry install --no-interaction --no-ansi --no-root

COPY ./src /app

ARG BUILD_HASH=
ARG BUILD_TAG=
ARG BUILD_DATE=

ENV SERVICE_INFO_HASH=$BUILD_HASH
ENV SERVICE_INFO_TAG=$BUILD_TAG
ENV SERVICE_INFO_DATE=$BUILD_DATE

CMD ["python", "-m", "deps_file_storage", "serve"]

FROM python-base as runtime

COPY --from=build $VENV_PATH $VENV_PATH
COPY ./vendors /vendors
COPY ./src /app

ARG BUILD_HASH=
ARG BUILD_TAG=
ARG BUILD_DATE=

ENV SERVICE_INFO_HASH=$BUILD_HASH
ENV SERVICE_INFO_TAG=$BUILD_TAG
ENV SERVICE_INFO_DATE=$BUILD_DATE

USER $USER

CMD ["python", "-m", "deps_file_storage", "serve"]
