# API test screenshots

Captured on 29 September 2026 using Python 3.14.3 and the local API at
`http://127.0.0.1:8765`. These are macOS Terminal window captures displaying
individual sections of the real curl run saved in
[docs/curl_test_output.txt](../docs/curl_test_output.txt). The responses were not
fabricated or edited. HTTP header line endings in the text file were normalized
to LF. The GET-all body is summarized as a record count to keep it readable.

| File | Evidence |
| --- | --- |
| 01_get_success.png | Authenticated GET by ID returns 200 and the transaction |
| 02_unauthorized.png | Wrong password returns 401 and WWW-Authenticate |
| 03_post_success.png | POST returns 201 and a new ID |
| 04_put_success.png | PUT returns 200 with amount 3500 and balance 46500 |
| 05_delete_success.png | DELETE returns 200 |
| 06_deleted_record_404.png | GET after deletion returns 404 |
| 07_invalid_timestamp.png | Invalid timestamp returns 400 |
| 08_get_all.png | Authenticated GET list returns 200 and 1691 records |

All 10 curl checks passed. A second run against the same server also passed,
using the next generated ID. The original automated run passed 12 tests. After the 30 September regression
updates, the expanded suite passes 25 tests without the earlier cleanup warnings;
its current output is in [api-tests.txt](../docs/test-results/api-tests.txt).
The screenshots retain the original 29 September curl run.

## Repeat the tests

Open Terminal in the repository root. No packages need installing.

Terminal 1 — start the server (these are disposable local demo credentials):

```bash
export API_USER=demo
export API_PASSWORD=demo-local-only
export API_PORT=8765
python3 -B api/server.py
```

Leave Terminal 1 running. In Terminal 2, also open the repository root:

```bash
export API_USER=demo
export API_PASSWORD=demo-local-only
export API_URL=http://127.0.0.1:8765
bash tests/curl_tests.sh
```

Expected ending: `All 10 curl checks passed.` The script reads the ID returned by
POST, uses it for PUT and DELETE, and stops if a status differs from expectations.
It also checks the updated amount and balance. It only changes the record it creates.

Automated tests start their own temporary server; they do not need Terminal 1:

```bash
python3 -B -m unittest discover -s tests -p 'test_*.py' -v
```

Expected ending: `Ran 25 tests` and `OK`.

## Try each request yourself

In Terminal 2, after exporting the variables above:

```bash
# GET: 200 OK
curl -i -u "$API_USER:$API_PASSWORD" "$API_URL/transactions/1"

# Wrong credentials: 401 Unauthorized
curl -i -u "$API_USER:wrong-password" "$API_URL/transactions"

# POST: 201 Created; read the returned id
curl -i -u "$API_USER:$API_PASSWORD" -X POST "$API_URL/transactions" \
  -H 'Content-Type: application/json' \
  -d '{"type":"transfer","amount":3000,"sender":"You","receiver":"Grace Uwase","timestamp":"2025-02-01 10:15:00","balance":47000}'
```

Set `NEW_ID` to the ID your POST actually returned. For example, use
`NEW_ID=1692` only if the returned ID was 1692. Then:

```bash
# PUT: 200 OK; amount and balance should change
curl -i -u "$API_USER:$API_PASSWORD" -X PUT "$API_URL/transactions/$NEW_ID" \
  -H 'Content-Type: application/json' -d '{"amount":3500,"balance":46500}'

# DELETE: 200 OK
curl -i -u "$API_USER:$API_PASSWORD" -X DELETE "$API_URL/transactions/$NEW_ID"

# Verify deletion: 404 Not Found
curl -i -u "$API_USER:$API_PASSWORD" "$API_URL/transactions/$NEW_ID"
```

`-i` shows HTTP headers, `-u` supplies Basic Auth, `-X` selects the method,
`-H` sets a request header, and `-d` sends JSON. A 400 or 401 is a passing test
when deliberately sending invalid input or credentials.

To take your own screenshots, show the command and its complete response in
Terminal, press Shift-Command-4 then Space, and select the Terminal window.
Save the images in this folder. Stop the server with Control-C in Terminal 1.

Optional DSA rerun: `python3 -B dsa/search_compare.py`. This overwrites
`docs/dsa_results.json` with new timings. The README/PDF currently show the
previous recorded run; timings naturally vary between machines and runs.
