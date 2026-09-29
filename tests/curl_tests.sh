#!/bin/bash
# Test script for the API.
# 1) export API_USER and API_PASSWORD, then start the server: python3 api/server.py
# 2) in another terminal export the same two variables
# 3) run this file:                         bash tests/curl_tests.sh
# (a fresh server has 1691 transactions, so the new one from POST gets id 1692)

URL="http://127.0.0.1:8000"
LOGIN="$API_USER:$API_PASSWORD"

echo "### 1. GET /transactions/1 with correct login"
curl -i -u $LOGIN $URL/transactions/1
echo
echo
echo "### 2. GET /transactions with correct login (only the first lines are shown)"
curl -s -i -u $LOGIN $URL/transactions | head -15
echo
echo "### 3. GET /transactions with WRONG password"
curl -i -u "$API_USER:wrong-password" $URL/transactions
echo
echo
echo "### 4. GET /transactions with no login at all"
curl -i $URL/transactions
echo
echo
echo "### 5. POST /transactions (add a new one)"
curl -i -u $LOGIN -X POST $URL/transactions \
  -H "Content-Type: application/json" \
  -d '{"type":"transfer","amount":3000,"sender":"You","receiver":"Grace Uwase","timestamp":"2025-02-01 10:15:00","balance":47000}'
echo
echo
echo "### 6. PUT /transactions/1692 (change amount and balance)"
curl -i -u $LOGIN -X PUT $URL/transactions/1692 \
  -H "Content-Type: application/json" \
  -d '{"amount":3500,"balance":46500}'
echo
echo
echo "### 7. DELETE /transactions/1692"
curl -i -u $LOGIN -X DELETE $URL/transactions/1692
echo
echo
echo "### 8. GET /transactions/1692 again (should be 404 now)"
curl -i -u $LOGIN $URL/transactions/1692
echo
echo
echo "### 9. POST with bad data (should be 400)"
curl -i -u $LOGIN -X POST $URL/transactions \
  -H "Content-Type: application/json" \
  -d '{"amount":"abc"}'
echo
echo "### 10. POST with a bad timestamp (should be 400)"
curl -i -u $LOGIN -X POST $URL/transactions \
  -H "Content-Type: application/json" \
  -d '{"type":"transfer","amount":100,"sender":"You","receiver":"Test","timestamp":"garbage"}'
echo
