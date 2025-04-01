ARG DOCKER_REGISTRY_MIRROR
ARG PYTHON_VERSION

FROM ${DOCKER_REGISTRY_MIRROR}/python:${PYTHON_VERSION}-alpine AS builder
ENV PATH="/opt/venv/bin:$PATH"
COPY ./requirements.txt .
RUN --mount=type=secret,id=pip_index_url \
    --mount=type=secret,id=pip_proxy \
    --mount=type=secret,id=pip_trusted_host \
    export PIP_INDEX_URL=$(cat /run/secrets/pip_index_url) && \
    export PIP_PROXY=$(cat /run/secrets/pip_proxy) && \
    export PIP_TRUSTED_HOST=$(cat /run/secrets/pip_trusted_host) && \
    python3 -m venv /opt/venv && \
    pip3 install --no-cache-dir -r ./requirements.txt

FROM ${DOCKER_REGISTRY_MIRROR}/python:${PYTHON_VERSION}-alpine AS app
WORKDIR /app
ENV PATH="/opt/venv/bin:$PATH"
COPY --from=builder /opt/venv /opt/venv
COPY ./src /app
ENTRYPOINT ["python3", "/app/main.py"]
