FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .
COPY alembic.ini ./
COPY migrations ./migrations

ENV LICITAGOIAS_ENV=production
EXPOSE 8000
CMD ["uvicorn", "licitagoias.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
