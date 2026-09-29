# Screenshots

Take these after starting the server (see the main README). Each screenshot must show the command and its output.

1. `01_get_success.png`: `curl -i -u "$API_USER:$API_PASSWORD" http://127.0.0.1:8000/transactions/1`
2. `02_unauthorized.png`: `curl -i -u "$API_USER:wrong-password" http://127.0.0.1:8000/transactions`
3. `03_post_success.png`: test 5 in `tests/curl_tests.sh`
4. `04_put_success.png`: test 6
5. `05_delete_success.png`: test 7
6. `06_bad_timestamp.png` (optional): test 10

Run POST, PUT and DELETE in order on one fresh server so the new record gets id 1692.
