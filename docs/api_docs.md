# MoMo SMS Transactions API - Documentation

**Base URL:** `http://127.0.0.1:8000` (change with `API_HOST` / `API_PORT`)
**Data format:** JSON (`Content-Type: application/json`)
**Authentication:** HTTP Basic Auth on every request
**Credentials:** the `API_USER` and `API_PASSWORD` environment variables the server was started with

The API loads the 1691 SMS records from `data/raw/modified_sms_v2.xml` when it starts
(ids 1 to 1691) and keeps them in memory. All examples below were run against a live server.

---

## Transaction object

| Field            | Type           | Description                                                               |
| ---------------- | -------------- | ------------------------------------------------------------------------- |
| `id`             | integer        | Unique id given by the API (never sent by the client)                     |
| `type`           | string         | Kind of SMS, e.g. `payment`, `transfer`, `bank_deposit`, `incoming_money` |
| `amount`         | number or null | Amount in RWF. `null` for messages that carry no amount (OTP messages)    |
| `sender`         | string or null | Who sent the money (`"You"` for outgoing payments)                        |
| `receiver`       | string or null | Recipient/counterparty (`"You"` for incoming money; named agent for withdrawals)                       |
| `balance`        | number or null | Balance after the transaction, when the SMS shows it                      |
| `transaction_id` | string or null | Financial transaction id printed in the SMS, when there is one            |
| `timestamp`      | string         | `YYYY-MM-DD HH:MM:SS` (Rwanda time)                                       |
| `raw_body`       | string or null | The original SMS text                                                     |

Types found in the dataset: `payment`, `transfer`, `bank_deposit`, `incoming_money`,
`third_party_payment`, `bundle_purchase`, `airtime`, `cash_power`, `otp`,
`failed_transaction`, `withdrawal`, `reversal`. Clients may send any text as `type`.

---

## GET /transactions

Returns every transaction as a JSON array.

**Request**

```bash
curl -u "$API_USER:$API_PASSWORD" http://127.0.0.1:8000/transactions
```

**Response `200 OK`** (array of 1691 objects, one shown)

```json
[
  {
    "id": 2,
    "type": "payment",
    "amount": 1000,
    "sender": "You",
    "receiver": "Jane Smith",
    "balance": 1000,
    "transaction_id": "73214484437",
    "timestamp": "2024-05-10 16:31:39",
    "raw_body": "TxId: 73214484437. Your payment of 1,000 RWF to Jane Smith 12845 has been completed at 2024-05-10 16:31:39. Your new balance: 1,000 RWF. Fee was 0 RWF...."
  }
]
```

**Errors:** `401`

---

## GET /transactions/{id}

Returns one transaction.

**Request**

```bash
curl -u "$API_USER:$API_PASSWORD" http://127.0.0.1:8000/transactions/1
```

**Response `200 OK`**

```json
{
  "id": 1,
  "type": "incoming_money",
  "amount": 2000,
  "sender": "Jane Smith",
  "receiver": "You",
  "balance": 2000,
  "transaction_id": "76662021700",
  "timestamp": "2024-05-10 16:30:51",
  "raw_body": "You have received 2000 RWF from Jane Smith (*********013) on your mobile money account at 2024-05-10 16:30:51. Message from sender: . Your new balance:2000 RWF. Financial Transaction Id: 76662021700."
}
```

**Response `404 Not Found`** (unknown id, or an id that is not a whole number)

```json
{
  "error": "Transaction 99999 not found",
  "status": 404
}
```

**Errors:** `401`, `404`

---

## POST /transactions

Creates a transaction. The API chooses the id (the next number after the highest id used so far).

**Required fields:** `type`, `amount`, `sender`, `receiver`, `timestamp` (none of them may be `null`).
**Optional fields:** `balance`, `transaction_id`, `raw_body`. Any other field is rejected.

**Request**

```bash
curl -u "$API_USER:$API_PASSWORD" -X POST \
  -H "Content-Type: application/json" \
  -d '{"type":"transfer","amount":3000,"sender":"You","receiver":"Grace Uwase","timestamp":"2025-02-01 10:15:00","balance":47000}' \
  http://127.0.0.1:8000/transactions
```

**Response `201 Created`** (with header `Location: /transactions/1692`)

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

**Response `400 Bad Request`** (example: a required field is missing)

```json
{
  "error": "Missing field: type",
  "status": 400
}
```

**Errors:** `400`, `401`, `404`, `405` (POST on `/transactions/{id}`)

---

## PUT /transactions/{id}

Updates an existing transaction. Send only the fields you want to change; the other fields and
the `id` stay as they are. The same validation rules as POST apply to the fields you send.

**Request**

```bash
curl -u "$API_USER:$API_PASSWORD" -X PUT \
  -H "Content-Type: application/json" \
  -d '{"amount":3500,"balance":46500}' \
  http://127.0.0.1:8000/transactions/1692
```

**Response `200 OK`** (the updated transaction)

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

**Errors:** `400`, `401`, `404`, `405` (PUT on `/transactions` without an id)

---

## DELETE /transactions/{id}

Deletes a transaction. Ids are not reused: after deleting 1692 the next POST still gets a higher id.

**Request**

```bash
curl -u "$API_USER:$API_PASSWORD" -X DELETE http://127.0.0.1:8000/transactions/1692
```

**Response `200 OK`**

```json
{
  "message": "Transaction 1692 deleted"
}
```

**Errors:** `401`, `404`, `405` (DELETE on `/transactions` without an id)

---

## Authentication

Every endpoint needs an `Authorization: Basic base64(user:password)` header. `curl -u` builds it for you.
Authentication is checked first, before the route or the body, so a request without valid
credentials always gets `401`, even for a route that does not exist.

```bash
curl -i -u "$API_USER:wrong-password" http://127.0.0.1:8000/transactions
```

```text
HTTP/1.0 401 Unauthorized
WWW-Authenticate: Basic realm="MoMo API"
Content-Type: application/json

{
  "error": "Unauthorized: invalid or missing credentials",
  "status": 401
}
```

The server refuses to start unless both `API_USER` and `API_PASSWORD` are set.
Basic Auth only Base64-encodes the password (it is not encrypted), so use HTTPS in real deployments.

---

## Error codes

Every error has the same shape: `{"error": "<message>", "status": <code>}`.

| Status | Meaning            | When it happens                                                                                                  |
| ------ | ------------------ | ---------------------------------------------------------------------------------------------------------------- |
| `200`  | OK                 | GET, PUT and DELETE succeeded                                                                                    |
| `201`  | Created            | POST succeeded                                                                                                   |
| `400`  | Bad Request        | Body missing, larger than 1 MB, or not valid JSON; body is not a JSON object; a field is missing, unknown, null or has the wrong type; negative amount; non-finite number (NaN or infinity); bad timestamp |
| `401`  | Unauthorized       | Missing, malformed or wrong credentials                                                                          |
| `404`  | Not Found          | `Route not found`, or `Transaction {id} not found`                                                               |
| `405`  | Method Not Allowed | `POST` with an id, or `PUT` / `DELETE` without an id                                                             |

Exact `400` messages: `Body is missing or is not valid JSON`, `Body must be a JSON object`,
`Missing field: x`, `Unknown field: x`, `Field 'x' cannot be null`, `Field 'x' must be text`,
`Field 'x' must be a number`, `Field 'x' must be finite`, `Field 'amount' must be a number that is 0 or more`,
`Field 'timestamp' must look like YYYY-MM-DD HH:MM:SS`.

Other methods (`HEAD`, `PATCH`, `OPTIONS`) are not implemented; Python's `http.server` answers them with `501`.

---

## Notes and limits

* Data lives in memory. POST, PUT and DELETE changes are lost when the server restarts, and the XML is re-read.
* The XML header says 1693 messages but the file holds 1691; the API serves the 1691 that exist.
* OTP messages (8 of them) have no amount, sender, receiver or balance, so those fields are `null`.
* One shared login, no roles, no rate limiting and no HTTPS. See the PDF report for stronger options (JWT, OAuth 2.0).
