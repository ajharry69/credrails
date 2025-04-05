FROM python:3.10-slim
LABEL org.opencontainers.image.source="https://github.com/ajharry69/credrails"
LABEL org.opencontainers.image.licenses="Apache-2.0"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /.venv
ENV PATH="/.venv/bin:$PATH"

COPY requirements*.txt ./
ARG REQUIREMENTS_FILE=requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r $REQUIREMENTS_FILE

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]