# MoMo SMS Transactions API - Documentation

**Base URL:** `http://127.0.0.1:8000`
**Data format:** JSON
**Authentication:** HTTP Basic Auth on every endpoint
**Credentialss:** set with the `API_USER` and `API_PASSWORD` environment variables (the examples use them)

The API holds the 1691 SMS records from `modified_sms_v2.xml` (ids 1 to 1691).

## Transaction object

| Field | Type | Needed for POST? | Notes |
|---|---|---|---|
| `id` | integer | no | given by the server, cannot be sent or changed |
| `type` | string | yes | see the list of types below |
| `amount` | number | yes | 0 or more, in RWF (can be `null` for OTP messages) |
| `sender` | string | yes | who the money came from (`You` = the account owner) |
| `receiver` | string | yes | who the money went to |
| `timestamp` | string | yes | must be `YYYY-MM-DD HH:MM:SS`, otherwise 400 |
| `balance` | number or null | no | balance after the transaction |
| `transaction_id` | string or null | no | the MoMo transaction id |
| `raw_body` | string or null | no | the original SMS text |

Types found in the XML file: `incoming_money`, `payment`, `transfer`, `bank_deposit`, `withdrawal`, `airtime`, `cash_power`, `bundle_purchase`, `third_party_payment`, `reversal`, `failed_transaction`, `otp`.

---

## 1. Get all transactions

**`GET /transactions`**

Request:
```bash
curl -u $API_USER:$API_PASSWORD http://127.0.0.1:8000/transactions
```

Response `200 OK` (a list, shortened here):
```json
[
  {
    "id": 1,
    "type": "incoming_money",
    "amount": 2000,
    "sender": "Jane Smith",
    "receiver": "You",
    "balance": 2000,
    "transaction_id": "76662021700",
    "timestamp": "2024-05-10 16:30:51",
    "raw_body": "You have received 2000 RWF from Jane Smith (*********013) on your mobile money account at 2024-05-10 16:30:51. ..."
  }
]
```
Errors: `401`

---

## 2. Get one transaction

**`GET /transactions/{id}`**

Request:
```bash
curl -u $API_USER:$API_PASSWORD http://127.0.0.1:8000/transactions/1
```

Response `200 OK`: one transaction object (same as above).

Errors: `401`, `404` (id does not exist)

---

## 3. Add a transaction

**`POST /transactions`**

Request:
```bash
curl -u $API_USER:$API_PASSWORD -X POST http://127.0.0.1:8000/transactions \
  -H "Content-Type: application/json" \
  -d '{"type":"transfer","amount":3000,"sender":"You","receiver":"Grace Uwase","timestamp":"2025-02-01 10:15:00","balance":47000}'
```

Response `201 Created` (the new record gets the next free id):
```json
{
  "id": 1692,
  "type": "transfer",
  "amount": 3000,
  "sender": "You",
  "receiver": "Grace Uwase",
  "balance": 47000,
  "transaction_id": null,
  "timestamp": "2025-02-01 10:15:00",
  "raw_body": null
}
```
Errors: `400` (body is not valid JSON, a required field is missing, wrong data type, unknown field, bad timestamp, negative amount), `401`

---

## 4. Update a transaction

**`PUT /transactions/{id}`**

Partial update: only the fields you send are changed, the others stay the same (send any subset of the fields above).

Request:
```bash
curl -u $API_USER:$API_PASSWORD -X PUT http://127.0.0.1:8000/transactions/1692 \
  -H "Content-Type: application/json" \
  -d '{"amount":3500,"balance":46500}'
```

Response `200 OK`: the full updated transaction.
```json
{
  "id": 1692,
  "type": "transfer",
  "amount": 3500,
  "sender": "You",
  "receiver": "Grace Uwase",
  "balance": 46500,
  "transaction_id": null,
  "timestamp": "2025-02-01 10:15:00",
  "raw_body": null
}
```
Errors: `400`, `401`, `404`, `405` (if no id is given)

---

## 5. Delete a transaction

**`DELETE /transactions/{id}`**

Request:
```bash
curl -u $API_USER:$API_PASSWORD -X DELETE http://127.0.0.1:8000/transactions/1692
```

Response `200 OK`:
```json
{
  "message": "Transaction 1692 deleted"
}
```
Errors: `401`, `404`, `405` (if no id is given)

---

## Error codes

| Code | Name | When it happens |
|---|---|---|
| 200 | OK | GET, PUT or DELETE worked |
| 201 | Created | POST worked |
| 400 | Bad Request | invalid JSON, missing or wrong field, unknown field, bad timestamp, negative amount |
| 401 | Unauthorized | no login or wrong username/password |
| 404 | Not Found | the route or the transaction id does not exist |
| 405 | Method Not Allowed | for example `POST /transactions/5` or `PUT /transactions` |

Every error looks like this:
```json
{
  "error": "Unauthorized: invalid or missing credentials",
  "status": 401
}
```

---

## About the dataset

- The XML header says `count="1693"` but the file holds 1691 `<sms>` records, so ids run from 1 to 1691.
- 8 records are OTP messages with no money movement, so their `amount`, `sender` and `receiver` are `null`.
