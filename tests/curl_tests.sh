#!/bin/bash
# Start api/server.py first, then export the same API_USER and API_PASSWORD here.
# Run: bash tests/curl_tests.sh
set -euo pipefail
: "${API_USER:?Export API_USER first}"
: "${API_PASSWORD:?Export API_PASSWORD first}"
URL="${API_URL:-http://127.0.0.1:8000}"
work_dir=$(mktemp -d)
trap 'rm -rf "$work_dir"' EXIT

request() {
    local title="$1" expected="$2" method="$3" path="$4" auth="$5" payload="${6:-}"
    local login="$API_USER:$API_PASSWORD"
    local args=(-sS --max-time 10)
    echo "### $title"
    echo "Expected HTTP status: $expected"
    printf 'curl -i -X %s ' "$method"
    if [ "$auth" = wrong ]; then
        login="$API_USER:wrong-password"
        printf '%s ' '-u "$API_USER:wrong-password"'
    elif [ "$auth" = valid ]; then
        printf '%s ' '-u "$API_USER:$API_PASSWORD"'
    fi
    if [ "$auth" != none ]; then args+=(-u "$login"); fi
    if [ -n "$payload" ]; then
        args+=(-H 'Content-Type: application/json' -d "$payload")
        printf -- "-H 'Content-Type: application/json' -d '%s' " "$payload"
    fi
    printf '%s%s\n\n' "$URL" "$path"
    status=$(curl -D "$work_dir/headers" -o "$work_dir/body" \
        -w '%{http_code}' -X "$method" "${args[@]}" "$URL$path")
    cat "$work_dir/headers"
    if [ "$path" = /transactions ] && [ "$method" = GET ] && [ "$status" = 200 ]; then
        python3 -c 'import json,sys; print("Response contains", len(json.load(open(sys.argv[1]))), "transactions (body omitted here).")' "$work_dir/body"
    else
        cat "$work_dir/body"
    fi
    echo
    if [ "$status" != "$expected" ]; then
        echo "FAIL: expected $expected, received $status"
        exit 1
    fi
    echo "PASS: HTTP $status"
    echo
}

request '1. Authenticated GET one transaction' 200 GET /transactions/1 valid
request '2. Authenticated GET all transactions' 200 GET /transactions valid
request '3. Wrong password' 401 GET /transactions wrong
request '4. Missing credentials' 401 GET /transactions none
request '5. Create transaction' 201 POST /transactions valid \
    '{"type":"transfer","amount":3000,"sender":"You","receiver":"Grace Uwase","timestamp":"2025-02-01 10:15:00","balance":47000}'
new_id=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["id"])' "$work_dir/body")
request '6. Update the created transaction' 200 PUT "/transactions/$new_id" valid \
    '{"amount":3500,"balance":46500}'
python3 -c 'import json,sys; row=json.load(open(sys.argv[1])); assert row["amount"] == 3500 and row["balance"] == 46500' "$work_dir/body"
request '7. Delete the created transaction' 200 DELETE "/transactions/$new_id" valid
request '8. Confirm deletion' 404 GET "/transactions/$new_id" valid
request '9. Reject missing required fields' 400 POST /transactions valid '{"amount":"abc"}'
request '10. Reject invalid timestamp' 400 POST /transactions valid \
    '{"type":"transfer","amount":100,"sender":"You","receiver":"Test","timestamp":"garbage"}'
echo 'All 10 curl checks passed.'
