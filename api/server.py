# REST API for the MoMo SMS transactions (plain http.server + Basic Auth).
# Run with:  API_USER=... API_PASSWORD=... python3 api/server.py

import os
import sys
import json
import base64
import hmac
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

# so python can find the dsa folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dsa.parse_xml import load_transactions

USERNAME = os.environ.get("API_USER")
PASSWORD = os.environ.get("API_PASSWORD")
HOST = os.environ.get("API_HOST", "127.0.0.1")
PORT = int(os.environ.get("API_PORT", "8000"))

# The transactions are stored in a dictionary (id -> transaction)
# so finding one by id is fast.

transactions = {}
for t in load_transactions():
    transactions[t["id"]] = t

# the next id we will give to a new transaction
next_id = max(transactions) + 1

# fields a client is allowed to send
TEXT_FIELDS = ["type", "sender", "receiver", "timestamp", "transaction_id", "raw_body"]
NUMBER_FIELDS = ["amount", "balance"]
REQUIRED_FIELDS = ["type", "amount", "sender", "receiver", "timestamp"]

# biggest request body we accept (bytes); stops a client from sending huge or fake sizes
MAX_BODY_SIZE = 1_000_000


def parse_id(id_text):
    """Turn the id from the url into an int, or None if it is not a plain number like 5."""
    # isascii() matters: characters such as the superscript two pass isdigit() but crash int()
    if id_text.isascii() and id_text.isdigit():
        return int(id_text)
    return None


def check_data(data, need_all_fields):
    """Check the JSON the client sent. Returns an error message, or None if it is fine."""
    if not isinstance(data, dict):
        return "Body must be a JSON object"

    if need_all_fields:
        for field in REQUIRED_FIELDS:
            if field not in data:
                return "Missing field: " + field

    for field in data:
        if field not in TEXT_FIELDS and field not in NUMBER_FIELDS:
            return "Unknown field: " + field

    for field in REQUIRED_FIELDS:
        if field in data and data[field] is None:
            return "Field '" + field + "' cannot be null"

    for field in TEXT_FIELDS:
        if field in data and data[field] is not None and not isinstance(data[field], str):
            return "Field '" + field + "' must be text"

    for field in NUMBER_FIELDS:
        if field in data and data[field] is not None:
            value = data[field]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                return "Field '" + field + "' must be a number"

    if "timestamp" in data:
        try:
            datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            return "Field 'timestamp' must look like YYYY-MM-DD HH:MM:SS"

    if "amount" in data and (data["amount"] is None or data["amount"] < 0):
        return "Field 'amount' must be a number that is 0 or more"

    return None


class MoMoHandler(BaseHTTPRequestHandler):

    # ---------- small helper functions ----------

    def send_json(self, status, data, extra_header=None):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        if extra_header:
            self.send_header(extra_header[0], extra_header[1])
        self.end_headers()
        self.wfile.write(body)

    def send_error_json(self, status, message):
        self.send_json(status, {"error": message, "status": status})

    def is_authorized(self):
        # the header looks like:  Authorization: Basic YWRtaW46cGFzc3dvcmQxMjM=
        header = self.headers.get("Authorization")
        if header is None or not header.startswith("Basic "):
            return False
        try:
            decoded = base64.b64decode(header[6:]).decode("utf-8")
        except Exception:
            return False
        expected = f"{USERNAME}:{PASSWORD}"
        return hmac.compare_digest(decoded.encode("utf-8"), expected.encode("utf-8"))

    def send_unauthorized(self):
        self.send_json(401,
                       {"error": "Unauthorized: invalid or missing credentials", "status": 401},
                       ("WWW-Authenticate", 'Basic realm="MoMo API"'))

    def get_route(self):
        """Split the url. Returns (ok, id_text).
        /transactions -> (True, None)     /transactions/5 -> (True, "5")"""
        path = self.path.split("?")[0].rstrip("/")
        parts = path.split("/")          # "/transactions/5" -> ["", "transactions", "5"]
        if len(parts) == 2 and parts[1] == "transactions":
            return True, None
        if len(parts) == 3 and parts[1] == "transactions":
            return True, parts[2]
        return False, None

    def read_body(self):
        """Read the JSON body of a POST/PUT. Returns None if it is not valid JSON."""
        try:
            length = int(self.headers.get("Content-Length", 0))
            if length <= 0 or length > MAX_BODY_SIZE:      # a negative size would make read() wait forever
                return None
            raw = self.rfile.read(length)
            return json.loads(raw)
        except Exception:
            return None

    # ---------- GET ----------

    def do_GET(self):
        if not self.is_authorized():
            self.send_unauthorized()
            return

        ok, id_text = self.get_route()
        if not ok:
            self.send_error_json(404, "Route not found")
            return

        # GET /transactions
        if id_text is None:
            self.send_json(200, list(transactions.values()))
            return

        # GET /transactions/{id}
        transaction_id = parse_id(id_text)
        if transaction_id is None or transaction_id not in transactions:
            self.send_error_json(404, f"Transaction {id_text} not found")
            return
        self.send_json(200, transactions[transaction_id])

    # ---------- POST ----------

    def do_POST(self):
        global next_id

        if not self.is_authorized():
            self.send_unauthorized()
            return

        ok, id_text = self.get_route()
        if not ok:
            self.send_error_json(404, "Route not found")
            return
        if id_text is not None:
            self.send_error_json(405, "POST is only allowed on /transactions")
            return

        data = self.read_body()
        if data is None:
            self.send_error_json(400, "Body is missing or is not valid JSON")
            return
        error = check_data(data, True)
        if error:
            self.send_error_json(400, error)
            return

        new_transaction = {
            "id": next_id,
            "type": data["type"],
            "amount": data["amount"],
            "sender": data["sender"],
            "receiver": data["receiver"],
            "balance": data.get("balance"),
            "transaction_id": data.get("transaction_id"),
            "timestamp": data["timestamp"],
            "raw_body": data.get("raw_body"),
        }
        transactions[next_id] = new_transaction
        next_id = next_id + 1

        self.send_json(201, new_transaction, ("Location", f"/transactions/{new_transaction['id']}"))

    # ---------- PUT ----------

    def do_PUT(self):
        if not self.is_authorized():
            self.send_unauthorized()
            return

        ok, id_text = self.get_route()
        if not ok:
            self.send_error_json(404, "Route not found")
            return
        if id_text is None:
            self.send_error_json(405, "PUT needs an id, use /transactions/{id}")
            return
        transaction_id = parse_id(id_text)
        if transaction_id is None or transaction_id not in transactions:
            self.send_error_json(404, f"Transaction {id_text} not found")
            return

        data = self.read_body()
        if data is None:
            self.send_error_json(400, "Body is missing or is not valid JSON")
            return
        error = check_data(data, False)
        if error:
            self.send_error_json(400, error)
            return

        transaction = transactions[transaction_id]
        for field in data:
            transaction[field] = data[field]       # only the fields that were sent are changed
        self.send_json(200, transaction)

    # ---------- DELETE ----------

    def do_DELETE(self):
        if not self.is_authorized():
            self.send_unauthorized()
            return

        ok, id_text = self.get_route()
        if not ok:
            self.send_error_json(404, "Route not found")
            return
        if id_text is None:
            self.send_error_json(405, "DELETE needs an id, use /transactions/{id}")
            return
        transaction_id = parse_id(id_text)
        if transaction_id is None or transaction_id not in transactions:
            self.send_error_json(404, f"Transaction {id_text} not found")
            return

        del transactions[transaction_id]
        self.send_json(200, {"message": f"Transaction {id_text} deleted"})


if __name__ == "__main__":
    if not USERNAME or not PASSWORD:
        sys.exit("Set API_USER and API_PASSWORD before starting the server (see README).")
    print(f"Loaded {len(transactions)} transactions")
    print(f"Server running on http://{HOST}:{PORT}")
    server = HTTPServer((HOST, PORT), MoMoHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
