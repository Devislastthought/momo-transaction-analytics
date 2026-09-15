# JSON ↔ SQL Mapping

| JSON file | Source table(s) | Notes |
|---|---|---|
| `user.json` | `users` | Direct 1:1 field mapping; `created_at` rendered as ISO-8601. |
| `transaction_category.json` | `transaction_categories` | Direct 1:1 field mapping. |
| `system_log.json` | `system_logs` | `transaction_id: null` mirrors a nullable FK (log created before a transaction row exists, e.g. a parse failure). |
| `transaction_full.json` | `transactions` + `transaction_categories` + `users` (×2, sender/receiver) + `tags`/`transaction_tags` + `system_logs` | Represents the FastAPI `/transactions/{id}` response shape: the flat `transactions` row is enriched by joining its category, both related users, its many-to-many tags (via `transaction_tags`), and any associated log rows. This is the object the frontend dashboard would consume for a transaction detail view. |

## Mapping conventions
- SQL `INT` primary/foreign keys → JSON integer fields with the same name.
- SQL `DECIMAL(p,s)` → JSON number (no currency symbol; `currency` is a separate field).
- SQL `DATETIME` → JSON string in ISO-8601 (`YYYY-MM-DDTHH:MM:SSZ`).
- SQL `ENUM` → JSON string using the exact enum label (e.g. `"COMPLETED"`).
- Nullable FK columns (e.g. `transactions.sender_id`, `system_logs.transaction_id`) → JSON `null` when absent, or an embedded object when the API resolves the join.
- The `transaction_tags` junction table never appears directly in JSON — it is flattened into a `tags: [...]` array on the transaction object, which is the standard way relational M:N junctions are serialized for API consumers.
