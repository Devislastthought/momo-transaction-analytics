import json
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dsa.parse_xml import XML_FILE, load_transactions, read_message, find_timestamp


class ParserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = load_transactions()

    def test_representative_values_for_each_message_type(self):
        # Expected values checked against the supplied XML, not the parser output.
        examples = [
            (1, "incoming_money", 2000, "Jane Smith", "You"),
            (2, "payment", 1000, "You", "Jane Smith"),
            (4, "bank_deposit", 40000, "Bank", "You"),
            (6, "transfer", 10000, "You", "Samuel Carter"),
            (8, "airtime", 2000, "You", "Airtime"),
            (22, "third_party_payment", 25000, "You", "DIRECT PAYMENT LTD"),
            (70, "withdrawal", 20000, "You", "Agent Sophia"),
            (72, "otp", None, None, None),
            (75, "cash_power", 4000, "You", "MTN Cash Power"),
            (161, "bundle_purchase", 2000, "You", "MTN Bundle"),
            (532, "reversal", 3000, "Mediatrice UWAYISENGA", "You"),
            (935, "failed_transaction", 14200, "You", "ESICIA LTD"),
        ]
        for record_id, kind, amount, sender, receiver in examples:
            with self.subTest(record_id=record_id):
                row = self.records[record_id - 1]
                self.assertEqual((row["type"], row["amount"], row["sender"], row["receiver"]),
                                 (kind, amount, sender, receiver))

    def test_incoming_balance_reference_and_time(self):
        first = self.records[0]
        self.assertEqual(first["balance"], 2000)
        self.assertEqual(first["transaction_id"], "76662021700")
        self.assertEqual(first["timestamp"], "2024-05-10 16:30:51")

    def test_every_source_sms_is_preserved_and_json_serializable(self):
        messages = list(ET.parse(XML_FILE).getroot().iter("sms"))
        self.assertEqual(len(self.records), len(messages))
        self.assertEqual([r["id"] for r in self.records], list(range(1, len(messages) + 1)))
        for message, row in zip(messages, self.records):
            self.assertEqual(row["raw_body"], message.get("body", ""))
        self.assertEqual(json.loads(json.dumps(self.records, allow_nan=False)), self.records)

    def test_otp_does_not_invent_financial_values(self):
        otps = [row for row in self.records if row["type"] == "otp"]
        self.assertEqual(len(otps), 8)
        for row in otps:
            for key in ["amount", "sender", "receiver", "balance", "transaction_id"]:
                self.assertIsNone(row[key])
            self.assertIsNotNone(row["timestamp"])

    def test_timestamp_uses_message_then_rwanda_sms_time(self):
        self.assertEqual(find_timestamp("at 2024-05-10 16:30:51", "0"), "2024-05-10 16:30:51")
        self.assertEqual(find_timestamp("no date here", "0"), "1970-01-01 02:00:00")
        self.assertIsNone(find_timestamp("no date here", None))

    def test_alternative_transfer_format_and_missing_agent(self):
        self.assertEqual(read_message("You have transferred 1,500 RWF to Test Person (123)"),
                         ("transfer", 1500, "You", "Test Person"))
        self.assertEqual(read_message("You have withdrawn 500 RWF"),
                         ("withdrawal", 500, "You", None))

    def test_unknown_messages_are_kept(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "messages.xml"
            path.write_text('<smses><sms body="Unrecognized notice" date="0"/></smses>')
            rows = load_transactions(path)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["type"], "other")
        self.assertEqual(rows[0]["raw_body"], "Unrecognized notice")
        self.assertIsNone(rows[0]["amount"])


if __name__ == "__main__":
    unittest.main()
