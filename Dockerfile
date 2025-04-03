ARG PYTHON_VERSION

FROM python:${PYTHON_VERSION}-slim AS builder
ENV PATH="/opt/venv/bin:$PATH"
COPY ./requirements.txt .
RUN python3 -m venv /opt/venv && pip3 install --no-cache-dir -r ./requirements.txt

FROM python:${PYTHON_VERSION}-slim AS app
WORKDIR /app
ENV PATH="/opt/venv/bin:$PATH"
COPY --from=builder /opt/venv /opt/venv
COPY ./src /app
ENTRYPOINT ["python3", "/app/main.py"]
