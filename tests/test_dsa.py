import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dsa.parse_xml import load_transactions
from dsa.search_compare import linear_search, dictionary_lookup, binary_search

# test
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
        for wanted in [1, 20, 845, 1691]:
            found = linear_search(self.records, wanted)
            self.assertIs(found, dictionary_lookup(self.lookup, wanted))
            self.assertIs(found, binary_search(self.records, wanted))

    def test_missing_id(self):
        self.assertIsNone(linear_search(self.records, 0))
        self.assertIsNone(dictionary_lookup(self.lookup, 99999))
        self.assertIsNone(binary_search(self.records, 99999))


if __name__ == "__main__":
    unittest.main()

