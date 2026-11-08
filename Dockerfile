FROM python:3.12-alpine AS builder


# builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# runtime

FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONBUFFERED=1 \
    APP_PORT=5000

RUN apk add --no-cache tzdata \
    && adduser -D -u 1000 appuser

WORKDIR /app

COPY --from=builder /install /usr/local
COPY . .

USER appuser

EXPOSE 5000

CMD ["python", "app.py"]