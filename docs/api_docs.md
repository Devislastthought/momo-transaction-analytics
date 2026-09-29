# MoMo SMS Transactions API - Documentation

**Base URL:** `http://127.0.0.1:8000`
**Data format:** JSON
**Authentication:** HTTP Basic Auth on every endpoint
**Credentials:** set with the `API_USER` and `API_PASSWORD` environment variables (the examples use them)

The API holds the 1691 SMS records from `modified_sms_v2.xml` (ids 1 to 1691).

---

## Transaction Object

Each transaction has the following fields:

| Field     | Type    | Description                          |
| --------- | ------- | ------------------------------------ |
| `id`      | integer | Unique transaction ID                |
| `date`    | string  | Transaction date                     |
| `time`    | string  | Transaction time                     |
| `type`    | string  | Transaction type                     |
| `amount`  | number  | Transaction amount                   |
| `balance` | number  | Account balance after transaction    |
| `phone`   | string  | Phone number involved in transaction |
| `name`    | string  | Name of the person or merchant       |
| `message` | string  | Original SMS message                 |

---

## GET All Transactions

Returns all transactions stored by the API.

### Request

```bash
curl -u "$API_USER:$API_PASSWORD" \
  http://127.0.0.1:8000/transactions
```

### Response

```json
[
  {
    "id": 1,
    "date": "2023-01-01",
    "time": "10:30:00",
    "type": "transfer",
    "amount": 5000,
    "balance": 25000,
    "phone": "0780000000",
    "name": "John Doe",
    "message": "..."
  }
]
```

---

## GET One Transaction

Returns a single transaction using its ID.

### Request

```bash
curl -u "$API_USER:$API_PASSWORD" \
  http://127.0.0.1:8000/transactions/1
```

### Response

```json
{
  "id": 1,
  "date": "2023-01-01",
  "time": "10:30:00",
  "type": "transfer",
  "amount": 5000,
  "balance": 25000,
  "phone": "0780000000",
  "name": "John Doe",
  "message": "..."
}
```

If the transaction does not exist, the API returns:

```json
{
  "error": "Transaction not found"
}
```

---

## POST Transaction

Creates a new transaction.

### Request

```bash
curl -u "$API_USER:$API_PASSWORD" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2023-01-01",
    "time": "10:30:00",
    "type": "transfer",
    "amount": 5000,
    "balance": 25000,
    "phone": "0780000000",
    "name": "John Doe",
    "message": "Test transaction"
  }' \
  http://127.0.0.1:8000/transactions
```

The API assigns an ID to the new transaction.

---

## PUT Transaction

Updates an existing transaction.

### Request

```bash
curl -u "$API_USER:$API_PASSWORD" \
  -X PUT \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 7000,
    "balance": 23000
  }' \
  http://127.0.0.1:8000/transactions/1
```

The specified fields are updated while the transaction ID remains unchanged.

---

## DELETE Transaction

Deletes an existing transaction.

### Request

```bash
curl -u "$API_USER:$API_PASSWORD" \
  -X DELETE \
  http://127.0.0.1:8000/transactions/1
```

If successful, the API confirms that the transaction was deleted.

---

## Error Codes

| Status Code | Meaning                                        |
| ----------- | ---------------------------------------------- |
| `200`       | Request successful                             |
| `201`       | Transaction created successfully               |
| `400`       | Bad request                                    |
| `401`       | Authentication required or invalid credentials |
| `404`       | Transaction not found                          |
| `405`       | HTTP method not allowed                        |
| `500`       | Internal server error                          |

---

## Dataset Notes

The API is based on the MoMo SMS transaction dataset stored in:

```text
data/raw/modified_sms_v2.xml
```

The dataset contains **1691 SMS transaction records**, with transaction IDs ranging from **1 to 1691**.

The XML data is parsed using the project scripts and loaded into the API's in-memory transaction dictionary.

---

## Authentication

All API endpoints require HTTP Basic Authentication.

Set the credentials before running the API:

```bash
export API_USER="your_username"
export API_PASSWORD="your_password"
```

Then authenticate requests using:

```bash
curl -u "$API_USER:$API_PASSWORD" \
  http://127.0.0.1:8000/transactions
```

Requests without valid credentials return:

```json
{
  "error": "Unauthorized"
}
```
