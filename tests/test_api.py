import os
import sys
import json
import base64
import threading
import unittest
import urllib.request
import urllib.error

os.environ["API_USER"] = "test_user"
os.environ["API_PASSWORD"] = "test_password"

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from http.server import HTTPServer
from api import server


def call(port, method, path, body=None, user="test_user", password="test_password"):
    request = urllib.request.Request(f"http://127.0.0.1:{port}{path}", method=method)
    if user is not None:
        token = base64.b64encode(f"{user}:{password}".encode()).decode()
        request.add_header("Authorization", "Basic " + token)
    if body is not None:
        request.data = json.dumps(body).encode()
        request.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(request) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read())


class ApiTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.httpd = HTTPServer(("127.0.0.1", 0), server.MoMoHandler)
        cls.port = cls.httpd.server_address[1]
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()

    def test_list_and_get_one(self):
        status, data = call(self.port, "GET", "/transactions")
        self.assertEqual(status, 200)
        self.assertGreater(len(data), 1000)
        status, one = call(self.port, "GET", "/transactions/1")
        self.assertEqual(status, 200)
        self.assertEqual(one["id"], 1)

    def test_wrong_and_missing_credentials(self):
        self.assertEqual(call(self.port, "GET", "/transactions", user="test_user", password="nope")[0], 401)
        self.assertEqual(call(self.port, "GET", "/transactions", user=None)[0], 401)

    def test_not_found(self):
        self.assertEqual(call(self.port, "GET", "/transactions/999999")[0], 404)
        self.assertEqual(call(self.port, "GET", "/transactions/abc")[0], 404)

    def test_create_update_delete(self):
        new = {"type": "transfer", "amount": 3000, "sender": "You",
               "receiver": "Grace Uwase", "timestamp": "2025-02-01 10:15:00"}
        status, created = call(self.port, "POST", "/transactions", new)
        self.assertEqual(status, 201)
        new_id = created["id"]

        status, updated = call(self.port, "PUT", f"/transactions/{new_id}", {"amount": 3500})
        self.assertEqual(status, 200)
        self.assertEqual(updated["amount"], 3500)
        self.assertEqual(updated["receiver"], "Grace Uwase")

        self.assertEqual(call(self.port, "DELETE", f"/transactions/{new_id}")[0], 200)
        self.assertEqual(call(self.port, "GET", f"/transactions/{new_id}")[0], 404)

    def test_validation_errors(self):
        good = {"type": "transfer", "amount": 1, "sender": "a", "receiver": "b",
                "timestamp": "2025-02-01 10:15:00"}
        self.assertEqual(call(self.port, "POST", "/transactions", {"amount": "abc"})[0], 400)
        self.assertEqual(call(self.port, "POST", "/transactions", dict(good, amount=-5))[0], 400)
        self.assertEqual(call(self.port, "POST", "/transactions", dict(good, timestamp="garbage"))[0], 400)
        self.assertEqual(call(self.port, "POST", "/transactions", dict(good, hacker="x"))[0], 400)

    def test_wrong_method_on_route(self):
        self.assertEqual(call(self.port, "POST", "/transactions/1", {})[0], 405)
        self.assertEqual(call(self.port, "DELETE", "/transactions")[0], 405)


if __name__ == "__main__":
    unittest.main()
