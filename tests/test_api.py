import os
import sys
import json
import base64
import socket
import copy
import http.client
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
        with urllib.request.urlopen(request, timeout=3) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as error:
        with error:
            return error.code, json.loads(error.read())


def raw_request(port, request_bytes):
    """Send raw bytes (for requests urllib refuses to build) and return the status line."""
    with socket.create_connection(("127.0.0.1", port), timeout=3) as sock:
        sock.sendall(request_bytes)
        return sock.recv(200).split(b"\r\n")[0].decode()


def auth_header():
    return b"Authorization: Basic " + base64.b64encode(b"test_user:test_password") + b"\r\n"


class ApiTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.httpd = HTTPServer(("127.0.0.1", 0), server.MoMoHandler)
        cls.port = cls.httpd.server_address[1]
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.thread.join()
        cls.httpd.server_close()

    def setUp(self):
        # Give every test its own copy so rejected writes cannot hide later failures.
        self.original = copy.deepcopy(server.transactions)
        self.original_next_id = server.next_id

    def tearDown(self):
        server.transactions = self.original
        server.next_id = self.original_next_id

    def send_raw_body(self, body, authorization=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=3)
        token = base64.b64encode(b"test_user:test_password").decode()
        headers = {"Content-Type": "application/json",
                   "Authorization": authorization if authorization is not None else "Basic " + token}
        try:
            connection.request("POST", "/transactions", body, headers)
            response = connection.getresponse()
            return response.status, json.loads(response.read()), dict(response.getheaders())
        finally:
            connection.close()

    def test_authentication_protects_all_crud_routes(self):
        routes = [("GET", "/transactions"), ("GET", "/transactions/2"),
                  ("POST", "/transactions"), ("PUT", "/transactions/2"),
                  ("DELETE", "/transactions/2")]
        before = copy.deepcopy(server.transactions)
        for method, path in routes:
            for user, password in [(None, ""), ("test_user", "wrong")]:
                with self.subTest(method=method, user=user):
                    status, body = call(self.port, method, path, user=user, password=password)
                    self.assertEqual(status, 401)
                    self.assertEqual(body["status"], 401)
        self.assertEqual(server.transactions, before)
        self.assertEqual(server.next_id, self.original_next_id)

    def test_malformed_authentication_returns_challenge(self):
        token = base64.b64encode(b"test_user:test_password").decode()
        for header in ["Bearer token", "Basic !!!", "Basic !!!" + token]:
            with self.subTest(header=header):
                status, body, headers = self.send_raw_body("{}", header)
                self.assertEqual(status, 401)
                self.assertIn("Basic", headers["WWW-Authenticate"])
        self.assertEqual(server.transactions, self.original)

    def test_malformed_json_and_wrong_shapes(self):
        for body in ['{"amount":', '[]', '"text"', 'null']:
            with self.subTest(body=body):
                status, result, headers = self.send_raw_body(body)
                self.assertEqual(status, 400)
                self.assertEqual(result["status"], 400)
        self.assertEqual(server.transactions, self.original)

    def test_invalid_numbers_do_not_change_transactions(self):
        for field in ["amount", "balance"]:
            for value in [True, "100", float("nan"), float("inf"), float("-inf")]:
                with self.subTest(field=field, value=value):
                    status, result = call(self.port, "PUT", "/transactions/2", {field: value})
                    self.assertEqual(status, 400)
                    self.assertEqual(result["status"], 400)
                    self.assertEqual(call(self.port, "GET", "/transactions/2")[1], self.original[2])

    def test_failed_update_is_atomic(self):
        status, result = call(self.port, "PUT", "/transactions/2",
                              {"amount": 1234, "timestamp": "invalid"})
        self.assertEqual(status, 400)
        self.assertEqual(call(self.port, "GET", "/transactions/2")[1], self.original[2])

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
        self.assertEqual(call(self.port, "GET", f"/transactions/{new_id}")[1], created)

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

    def test_required_fields_cannot_be_null(self):
        nulls = {"type": None, "amount": 1, "sender": None, "receiver": None,
                 "timestamp": "2025-02-01 10:15:00"}
        self.assertEqual(call(self.port, "POST", "/transactions", nulls)[0], 400)
        self.assertEqual(call(self.port, "PUT", "/transactions/2", {"sender": None})[0], 400)
        # the record must not have been changed by the rejected update
        self.assertIsNotNone(call(self.port, "GET", "/transactions/2")[1]["sender"])

    def test_negative_content_length_does_not_hang(self):
        request = (b"POST /transactions HTTP/1.1\r\nHost: x\r\n" + auth_header()
                   + b"Content-Length: -1\r\n\r\n")
        self.assertIn("400", raw_request(self.port, request))

    def test_odd_id_characters_give_404_not_a_crash(self):
        # byte 0xB2 is read as the superscript two, which isdigit() accepts but int() rejects
        request = b"GET /transactions/\xb2 HTTP/1.1\r\nHost: x\r\n" + auth_header() + b"\r\n"
        self.assertIn("404", raw_request(self.port, request))

    def test_wrong_method_on_route(self):
        self.assertEqual(call(self.port, "POST", "/transactions/1", {})[0], 405)
        self.assertEqual(call(self.port, "DELETE", "/transactions")[0], 405)


if __name__ == "__main__":
    unittest.main()
