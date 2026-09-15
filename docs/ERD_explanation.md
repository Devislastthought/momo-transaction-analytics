# ERD Design Justification — MoMo SMS Data Processing System

## Overview
The ERD models six entities derived directly from the structure of the MTN MoMo
SMS export (`modified_sms_v2.xml`): **USERS**, **TRANSACTION_CATEGORIES**,
**TRANSACTIONS**, **TAGS**, **TRANSACTION_TAGS** (junction), and **SYSTEM_LOGS**.

## Design Decisions

**USERS** was separated from TRANSACTIONS because the same counterparty
(e.g. "Jane Smith", an agent, or a merchant code) appears across many SMS
messages. Normalizing them into their own table avoids repeating a person's
name/phone number on every row and lets us later analyze behavior per user
(e.g. total sent/received). `user_type` distinguishes customers, agents, and
merchants, since MoMo messages reference all three (agent withdrawals,
merchant "Bundles"/"Cash Power" payments, etc.).

**TRANSACTION_CATEGORIES** was extracted because the raw SMS bodies encode at
least eight distinct transaction types (Incoming Money, Payment to Code
Holder, Bank Deposit, Airtime, Bundle Purchase, Cash Power, Agent Withdrawal,
Third-Party/ONAFRIQ Transaction). Storing these as rows rather than a hard-
coded string keeps the category list extensible and queryable, and matches
the ETL pipeline's existing "Categorize Transactions" stage.

**TRANSACTIONS** is the central fact table. `sender_id`/`receiver_id` are two
separate foreign keys into USERS, modeling the natural 1:M relationship where
one user can be the sender or receiver of many transactions. The
`financial_transaction_id` column preserves the SMS's own `TxId`, giving a
natural dedupe key distinct from the surrogate primary key. `raw_message` is
kept for traceability/audit back to the source SMS.

**TAGS / TRANSACTION_TAGS** resolves the one required **many-to-many**
relationship: a single transaction can carry multiple free-form labels (e.g.
`promotion`, `cross-border`, `refunded`), and a tag can apply to many
transactions. The junction table stores only the two foreign keys plus a
timestamp, which is the standard resolution pattern for M:N relationships.

**SYSTEM_LOGS** supports the ETL pipeline's dead-letter/logging component
shown in the architecture diagram (`data/logs/etl.log`,
`data/logs/dead_letter/`). Each log row optionally references the transaction
it relates to (nullable FK, since parsing failures may occur before a
transaction record exists), preserving processing history for debugging.

## Cardinality Summary
- USERS (1) —— (M) TRANSACTIONS *(as sender)*
- USERS (1) —— (M) TRANSACTIONS *(as receiver)*
- TRANSACTION_CATEGORIES (1) —— (M) TRANSACTIONS
- TRANSACTIONS (1) —— (M) SYSTEM_LOGS
- TRANSACTIONS (M) —— (N) TAGS, resolved via TRANSACTION_TAGS
