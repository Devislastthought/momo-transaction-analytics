import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dsa.parse_xml import load_transactions
from dsa.search_compare import linear_search, dictionary_lookup, binary_search

class SearchTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.records = load_transactions()
        cls.lookup = {t["id"]: t for t in cls.records}

    def test_parser_keeps_every_sms(self):
        self.assertEqual(len(self.records), 1691)
        for field in ["id", "type", "amount", "sender", "receiver", "balance",
                      "transaction_id", "timestamp", "raw_body"]:
            self.assertIn(field, self.records[0])

    def test_three_searches_agree(self):
        for wanted in list(range(1, 21)) + [845, 1691]:
            found = linear_search(self.records, wanted)
            self.assertIsNotNone(found)
            self.assertEqual(found["id"], wanted)
            self.assertIs(found, dictionary_lookup(self.lookup, wanted))
            self.assertIs(found, binary_search(self.records, wanted))

    def test_empty_single_record_and_gaps(self):
        for records in [[], [{"id": 4}], [{"id": 2}, {"id": 4}, {"id": 9}]]:
            lookup = {row["id"]: row for row in records}
            for wanted in [0, 2, 3, 4, 9, 10]:
                with self.subTest(records=records, wanted=wanted):
                    expected = lookup.get(wanted)
                    self.assertIs(linear_search(records, wanted), expected)
                    self.assertIs(dictionary_lookup(lookup, wanted), expected)
                    self.assertIs(binary_search(records, wanted), expected)

    def test_missing_id(self):
        self.assertIsNone(linear_search(self.records, 0))
        self.assertIsNone(dictionary_lookup(self.lookup, 99999))
        self.assertIsNone(binary_search(self.records, 99999))


if __name__ == "__main__":
    unittest.main()

