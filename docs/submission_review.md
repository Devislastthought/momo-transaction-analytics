# Rubric review — 30 September 2026

This is a provisional technical assessment, not an instructor grade. Before the
latest fixes the estimate was 24/25. After them, the implementation appears capable
of 24–25/25, conditional on complete submission and individual verification.

| Criterion | Evidence | Remaining check |
| --- | --- | --- |
| Data parsing /5 | 1,691 records; checks for all 12 types, original bodies, JSON serialization, null OTP fields and timestamps; named withdrawal agents retained | Sam reviews the actual extraction rules and source samples |
| CRUD /5 | GET list/item, POST, PUT and DELETE exercised through HTTP and curl | None found in required flows |
| Authentication /5 | Environment credentials; all CRUD routes reject invalid/missing login; strict Base64 parsing; PDF explains limitations and alternatives | Basic Auth remains local HTTP for this exercise |
| Documentation /5 | docs/api_docs.md covers all endpoints, request/response examples and errors; PDF contains required sections | Final submitted copies/links must be accessible |
| DSA/testing /5 | Linear/dictionary/binary methods; at least 20 real records benchmarked; 25 tests; 10 curl checks; required screenshots | Commit/push current results and confirm submitted revision |

The PDF and docs/dsa_results.json retain their original benchmark run. A fresh
20/1,691-record run is separately recorded in docs/test-results/dsa-regression.json;
timings are expected to differ. The screenshot transcript also retains its original
run; docs/test-results/curl-regression.txt verifies the updated implementation.

## Sam's task mapping

Based on the supplied Trello CSV, not a live board read:

- [API Testing](https://trello.com/c/YPgnIl1Z/54-api-testing): tests/test_api.py now checks all protected CRUD routes, malformed auth/JSON, invalid numbers and unchanged data after rejected writes. The tests exposed bugs fixed in api/server.py.
- [Create CURL Integration Tests](https://trello.com/c/vtg8SknW/55-create-curl-integration-tests): commit 6b559ea already added repeatable ID handling and status checks in tests/curl_tests.sh. The latest run still passes.
- [Run Automated Tests](https://trello.com/c/0rIiNNLi/56-run-automated-tests): 25 tests pass; results in docs/test-results/api-tests.txt, with fresh curl and DSA results alongside them.
- [Screenshots & Evidence](https://trello.com/c/2QLb89AF/57-screenshots-evidence): eight real screenshots already committed; required GET, 401, POST, PUT and DELETE cases are included.
- Participation-sheet parsing/JSON role: new tests/test_parse_xml.py checks extracted values and JSON conversion; dsa/parse_xml.py now preserves withdrawal agent names.

Repository cleanup is useful maintenance. It should not be presented as equivalent
to implementing a parser or API. Commit quantity alone is not a rubric criterion.

## Submission and individual-effort requirements

- Include the completed team participation sheet. Confirm team name, roles, actual
  participation, meetings and notes. The lead edits; other members have comment
  permission. Local files do not establish the live sharing permissions.
- Reconcile the Trello roles, workbook claims and Git history honestly. Existing
  implementation commits are under teammates' identities; new assisted fixes do
  not establish authorship of that earlier code.
- Review docs/ai_usage_log.md and add truthful evidence of Sam's own review,
  understanding and changes. Do not claim unperformed meetings or independent work.
- Update the relevant Trello cards with the final commit links and verified results.
- Confirm the submitted repository revision includes all required deliverables,
  including the PDF and participation sheet. No submission has been performed here.
- The brief says due 29 September at 23:59 and available until 30 September at 23:59.
  Availability is not proof of a deadline extension; check the course submission status.

The individual multiplier cannot be determined from commit count. Full verified
contribution gives team score ×1.0; partial gives ×0.5; no verified contribution
gives ×0.0. Missing the required team sheet can result in zero independently.
