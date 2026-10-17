FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 SISP_DB_PATH=/app/data/sisp.sqlite3
WORKDIR /app
COPY . /app
RUN apt-get update \
    && apt-get install -y --no-install-recommends gosu \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt \
    && mkdir -p /app/data \
    && useradd --system --uid 10001 sisp \
    && chown -R sisp:sisp /app
ENTRYPOINT ["/app/docker-entrypoint.sh"]
EXPOSE 8000
CMD ["gunicorn"]
