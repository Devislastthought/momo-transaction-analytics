# Compares linear search and dictionary lookup for finding a transaction by id.
# Binary search is included as an extra data structure idea for the reflection.

import os
import sys
import json
import time
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dsa.parse_xml import load_transactions


def linear_search(transactions, wanted_id):
    # look at every transaction one by one until the id matches -> O(n)
    for t in transactions:
        if t["id"] == wanted_id:
            return t
    return None


def dictionary_lookup(transaction_dict, wanted_id):
    # the id is the key so python jumps straight to the record -> O(1)
    return transaction_dict.get(wanted_id)


def binary_search(sorted_transactions, wanted_id):
    # only works if the list is sorted by id. Cut the search area in half each time -> O(log n)
    low = 0
    high = len(sorted_transactions) - 1
    while low <= high:
        middle = (low + high) // 2
        middle_id = sorted_transactions[middle]["id"]
        if middle_id == wanted_id:
            return sorted_transactions[middle]
        elif middle_id < wanted_id:
            low = middle + 1
        else:
            high = middle - 1
    return None


def time_it(search_function, data, ids_to_find, rounds):
    """Run the search for every id, 'rounds' times, and return the average microseconds per search."""
    start = time.perf_counter()
    for r in range(rounds):
        for wanted_id in ids_to_find:
            search_function(data, wanted_id)
    end = time.perf_counter()
    total_searches = rounds * len(ids_to_find)
    return (end - start) / total_searches * 1000000


def compare(records, name):
    transaction_dict = {}
    for t in records:
        transaction_dict[t["id"]] = t

    # choose up to 200 random ids to look for
    all_ids = list(transaction_dict.keys())
    if len(all_ids) > 200:
        ids_to_find = random.sample(all_ids, 200)
    else:
        ids_to_find = all_ids

    # check that all 3 methods really find the right record
    for wanted_id in ids_to_find:
        a = linear_search(records, wanted_id)
        b = dictionary_lookup(transaction_dict, wanted_id)
        c = binary_search(records, wanted_id)
        if not (a is b and b is c):
            print("ERROR: methods gave different results for id", wanted_id)

    # big lists take longer so use fewer rounds
    if len(records) >= 10000:
        rounds = 2
    else:
        rounds = 20

    linear_time = time_it(linear_search, records, ids_to_find, rounds)
    dict_time = time_it(dictionary_lookup, transaction_dict, ids_to_find, rounds)
    binary_time = time_it(binary_search, records, ids_to_find, rounds)

    return {
        "dataset": name,
        "n": len(records),
        "linear_us": linear_time,
        "dict_us": dict_time,
        "binary_us": binary_time,
    }


if __name__ == "__main__":
    random.seed(1)
    real = load_transactions()          # the real 1691 records from the XML file

    results = []
    results.append(compare(real[:20], "first 20 records"))
    results.append(compare(real[:100], "first 100 records"))
    results.append(compare(real, "all XML records"))

    # bigger fake lists to see what happens when the data grows
    for size in [10000, 100000]:
        fake = []
        for i in range(1, size + 1):
            fake.append({"id": i, "amount": i})
        results.append(compare(fake, "fake data"))

    print("Average time for one search (in microseconds)")
    print("-" * 78)
    print("%-20s %8s %12s %12s %12s %10s" % ("Dataset", "Records", "Linear", "Dictionary", "Binary", "Linear/Dict"))
    for r in results:
        speed = r["linear_us"] / r["dict_us"]
        print("%-20s %8d %12.3f %12.3f %12.3f %9.1fx" % (r["dataset"], r["n"], r["linear_us"], r["dict_us"], r["binary_us"], speed))

    out_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "dsa_results.json")
    with open(out_path, "w") as out_file:
        json.dump(results, out_file, indent=2)
    print("\nResults saved to docs/dsa_results.json")
