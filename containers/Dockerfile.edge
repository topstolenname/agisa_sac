# syntax=docker/dockerfile:1

# -------- builder stage --------
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# -------- runtime stage --------
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /wheels /wheels
RUN pip install --no-cache /wheels/* && rm -rf /wheels

# Copy application source
COPY . /app

# non-root user for security
RUN groupadd -r agisa && useradd -r -g agisa agisa \
    && chown -R agisa:agisa /app
USER agisa

EXPOSE 8765
CMD ["python", "-m", "agisa_sac"]
