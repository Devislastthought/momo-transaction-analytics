# AI assistance log

This records assistance in this workspace. It does not establish who originally
wrote the team's existing parser, server or search algorithms.

## 29 September 2026

Sam requested a rubric review, test evidence and terminal instructions. Codex
reviewed the supplied rubric, Trello CSV, participation workbook and repository;
updated the curl script to check statuses and use the returned POST ID; ran the
API tests; and captured Terminal screenshots of the real recorded curl output.
Codex also helped investigate the HTTP timeout during the push. The resulting
commit was `6b559ea` under Sam's configured Git identity.

## 30 September 2026

Sam requested another assessment and meaningful improvements matching his tasks.
Codex generated and ran the additional API, parser and search tests, reproduced
validation/parsing failures, implemented the fixes, restored ignore rules and
removed generated files from tracking. Codex created the commits using Sam's
configured Git identity. These changes are AI-assisted, not evidence that Sam
independently authored every line.

Verified results: 25 automated tests passed, 10 curl checks passed, and search
comparisons ran on 20 and 1,691 real records. Full outputs are under
`docs/test-results/`. No teammate messages, Trello changes or participation-sheet
edits were made by Codex.

## Human review still required

Sam should run the tests, review the changes and explain the validation and parser
rules. Record what he actually reviewed or changed and link the final commits on
his Trello cards. Do not mark these steps completed until they have happened.
The team lead should reconcile task ownership in the participation sheet with
actual work and disclose AI assistance according to the course rules.
