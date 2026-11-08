#!/usr/bin/env bash
set -u

if [ $# -lt 1 ]; then
    echo "Upotreba: $0 <URL>"
    echo "Primer:   $0 http://localhost:8080"
    exit 1
fi

BASE_URL="${1%/}"
MAX_ATTEMPTS=5
SLEEP_SECONDS=3

for attempt in $(seq 1 "$MAX_ATTEMPTS"); do
    status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$BASE_URL/health")
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Pokušaj $attempt-$MAX_ATTEMPTS / HTTP $status"

    if [ "$status" = "200" ]; then
        echo "Aplikacija je zdrava!"
        exit 0
    fi

    if [ "$attempt" -lt "$MAX_ATTEMPTS" ]; then
        sleep "$SLEEP_SECONDS"
    fi
done

echo "Aplikacija nije zdrava ni posle $MAX_ATTEMPTS pokušaja."
exit 1