# JSON examples

These are proposed API response examples based on the sample inserts in
`database/database_setup.sql`. The API is not implemented yet.

`json_schemas.json` collects examples for all six tables and one nested
transaction. It contains example data, not formal JSON Schema validation rules.
The individual files provide smaller examples for reading and review.

| File or section | SQL source | Representation |
|---|---|---|
| `user.json` / `users` | `users` | User 1, with a nullable merchant/agent code |
| `transaction_category.json` / `transaction_categories` | `transaction_categories` | Category 1 |
| `transactions` | `transactions` | Transaction 1 with its category, sender and receiver IDs |
| `tags` | `tags` | Tags 1 and 4, attached to transaction 1 |
| `transaction_tags` | `transaction_tags` | The two transaction/tag key pairs |
| `system_log.json` / `system_logs` | `system_logs` | Log 3 has no transaction; the combined file also includes log 1 |
| `transaction_full.json` / `transaction_full` | All six tables | Transaction 1 with nested sender, category, tags and logs |

## Mapping rules

- SQL integer IDs become JSON numbers. Phone numbers and financial transaction
  references remain strings.
- Amounts, fees and balances are JSON numbers. Trailing decimal zeros are not
  significant in JSON; `2000.0` and `2000.00` represent the same numeric value.
- SQL NULL becomes JSON `null`. Transaction 1 has no recorded receiver, so its
  nested `receiver` is `null`, matching `receiver_id` in the flat example.
- ENUM values become strings using the labels defined in SQL.
- `transaction_date` uses `YYYY-MM-DDTHH:MM:SS`. The seed DATETIME has no timezone
  information, so the example does not claim UTC by adding `Z`.
- Database-generated `created_at` and `tagged_at` values are intentionally omitted
  from these selected-field examples. Their values depend on when setup runs.
  An implemented API could return the actual stored values with a documented
  timezone convention.
- In the nested transaction, the category and sender objects replace their IDs;
  tags and logs are arrays. The combined file also shows the flat foreign keys
  and junction key pairs so their SQL mapping is visible.

These examples describe the existing seed records. They do not resolve the
separate sample-data questions about transaction 5's merchant and transaction 6's
refunded tag, neither of which is used in the nested example.

## Check syntax

From the project root:

```bash
python3 -m json.tool examples/json_schemas.json > /dev/null
python3 -m json.tool examples/transaction_full.json > /dev/null
```

These commands check JSON syntax, not agreement with the database. Review IDs,
values and relationships against the SQL after changing sample data.
