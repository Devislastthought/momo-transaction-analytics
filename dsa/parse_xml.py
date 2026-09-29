# Reads the SMS XML backup and turns every SMS into a transaction dictionary.
# Running this file saves the whole list as JSON in data/processed/.

import os
import re
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

# path to the xml file (data/raw/modified_sms_v2.xml)
BASE_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XML_FILE = os.environ.get("MOMO_XML_PATH", os.path.join(BASE_FOLDER, "data", "raw", "modified_sms_v2.xml"))
JSON_FILE = os.path.join(BASE_FOLDER, "data", "processed", "transactions.json")


def to_number(text):
    # "1,000" -> 1000
    return int(text.replace(",", ""))


def read_message(body):
    """Look at the text of one SMS and find the type, amount, sender and receivers."""
    msg_type = "other"
    amount = None
    sender = None
    receiver = None

    if "one-time password" in body:
        msg_type = "otp"

    elif "You have received" in body:
        m = re.search(r"received ([\d,]+) RWF from (.+?) \(", body)
        msg_type = "incoming_money"
        if m:
            amount = to_number(m.group(1))
            sender = m.group(2)
            receiver = "You"

    elif "withdrawn" in body:
        m = re.search(r"withdrawn ([\d,]+) RWF", body)
        msg_type = "withdrawal"
        if m:
            amount = to_number(m.group(1))
            sender = "You"
            receiver = "Agent"

    elif "bank deposit of" in body:
        m = re.search(r"bank deposit of ([\d,]+) RWF", body)
        msg_type = "bank_deposit"
        if m:
            amount = to_number(m.group(1))
            sender = "Bank"
            receiver = "You"

    elif "DEPOSIT RWF" in body:
        m = re.search(r"DEPOSIT RWF ([\d,]+)", body)
        msg_type = "bank_deposit"
        if m:
            amount = to_number(m.group(1))
            sender = "Bank"
            receiver = "You"

    elif "reversal" in body or "has been reversed" in body:
        m = re.search(r"transaction to (.+?) \(.*?\) with ([\d,]+) RWF", body)
        msg_type = "reversal"
        if m:
            amount = to_number(m.group(2))
            sender = m.group(1)
            receiver = "You"

    elif "failed at" in body or "has failed" in body:
        m = re.search(r"amount ([\d,]+) RWF for (.+?) with message", body)
        if m is None:
            m = re.search(r"payment of ([\d,]+) RWF to (.+?) with token", body)
        msg_type = "failed_transaction"
        if m:
            amount = to_number(m.group(1))
            sender = "You"
            receiver = m.group(2)

    elif "payment of" in body and "to Airtime" in body:
        m = re.search(r"payment of ([\d,]+) RWF", body)
        msg_type = "airtime"
        if m:
            amount = to_number(m.group(1))
            sender = "You"
            receiver = "Airtime"

    elif "Cash Power" in body:
        m = re.search(r"payment of ([\d,]+) RWF", body)
        msg_type = "cash_power"
        if m:
            amount = to_number(m.group(1))
            sender = "You"
            receiver = "MTN Cash Power"

    elif "A transaction of" in body:
        m = re.search(r"A transaction of ([\d,]+) RWF by (.+?) on your", body)
        msg_type = "third_party_payment"
        if m:
            amount = to_number(m.group(1))
            sender = "You"
            receiver = m.group(2).strip()

    elif "payment of" in body:
        m = re.search(r"payment of ([\d,]+) RWF to (.+?) [\d(]", body)
        msg_type = "payment"
        if m:
            amount = to_number(m.group(1))
            sender = "You"
            receiver = m.group(2)

    elif "transferred" in body:
        m = re.search(r"transferred ([\d,]+) RWF to (.+?) \(", body)   # "You have transferred 500 RWF to ..."
        if m is None:
            m = re.search(r"([\d,]+) RWF transferred to (.+?) \(", body)   # "*165*S*500 RWF transferred to ..."
        msg_type = "transfer"
        if m:
            amount = to_number(m.group(1))
            sender = "You"
            receiver = m.group(2)

    elif "Umaze kugura" in body:
        m = re.search(r"igura ([\d,]+) RWF", body)
        msg_type = "bundle_purchase"
        if m:
            amount = to_number(m.group(1))
            sender = "You"
            receiver = "MTN Bundle"

    return msg_type, amount, sender, receiver


def find_balance(body):
    m = re.search(r"new balance\s*(?:is)?\s*:?\s*([\d,]+)", body, re.IGNORECASE)
    if m:
        return to_number(m.group(1))
    return None


def find_transaction_id(body):
    m = re.search(r"Financial Transaction Id:\s*(\d+)", body)
    if m is None:
        m = re.search(r"TxId:\s*(\d+)", body)
    if m:
        return m.group(1)
    return None


def find_timestamp(body, date_attribute):
    # most messages have the time inside the text
    m = re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", body)
    if m:
        return m.group(0)
    # if not, use the "date" attribute (milliseconds), Rwanda time is UTC+2
    if date_attribute is not None and date_attribute.isdigit():
        rwanda = timezone(timedelta(hours=2))
        time = datetime.fromtimestamp(int(date_attribute) / 1000, rwanda)
        return time.strftime("%Y-%m-%d %H:%M:%S")
    return None


def load_transactions(xml_path=XML_FILE):
    """Read the xml file and return a list of dictionaries."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    transactions = []
    id_number = 1
    for sms in root.iter("sms"):
        body = sms.get("body", "")
        msg_type, amount, sender, receiver = read_message(body)

        transaction = {
            "id": id_number,
            "type": msg_type,
            "amount": amount,
            "sender": sender,
            "receiver": receiver,
            "balance": find_balance(body),
            "transaction_id": find_transaction_id(body),
            "timestamp": find_timestamp(body, sms.get("date")),
            "raw_body": body,
        }
        transactions.append(transaction)
        id_number = id_number + 1

    return transactions


if __name__ == "__main__":
    data = load_transactions()

    with open(JSON_FILE, "w") as file:
        json.dump(data, file, indent=2)

    print("Parsed", len(data), "records and saved them to", JSON_FILE)

    # count how many of each type we found
    counts = {}
    for t in data:
        counts[t["type"]] = counts.get(t["type"], 0) + 1
    print("Types found:")
    for name in counts:
        print("  ", name, ":", counts[name])

    print("First record:")
    print(json.dumps(data[0], indent=2))
