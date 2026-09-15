# ERD Design Justification — MoMo SMS Data Processing System

Our ERD has six entities: USERS, TRANSACTION_CATEGORIES, TRANSACTIONS, TAGS,
TRANSACTION_TAGS, and SYSTEM_LOGS. Each one traces back to something we
actually found while going through `modified_sms_v2.xml`.

We pulled USERS out on its own because the same people keep showing up
across many SMS messages — the same sender, the same agent, the same
merchant. Instead of repeating a name and phone number on every transaction
row, we store each person once and reference them by ID. `user_type`
separates customers from agents and merchants, since the messages clearly
distinguish agent withdrawals from merchant payments.

TRANSACTION_CATEGORIES exists because the SMS bodies fall into distinct,
repeating patterns — we counted at least eight: incoming money, payments to
a code holder, bank deposits, airtime, bundle purchases, MTN Cash Power,
agent withdrawals, and third-party payments through ONAFRIQ. Keeping these
as rows rather than hardcoded text means new categories can be added without
touching the schema.

TRANSACTIONS is our central table. `sender_id` and `receiver_id` are two
separate foreign keys back to USERS, since a person can appear as either
depending on the message. We kept `financial_transaction_id` because the
SMS TxId is a natural identifier separate from our own surrogate key, and
`raw_message` so we can always trace a row back to its source SMS.

TAGS and TRANSACTION_TAGS resolve our required many-to-many relationship: a
transaction can carry several free-form labels, and a label can apply to
many transactions. The junction table stores just the two foreign keys plus
a timestamp, following the standard pattern for resolving M:N relationships.

SYSTEM_LOGS mirrors the ETL pipeline's own logging/dead-letter behavior, so
parsing failures and processing steps stay traceable even when no clean
transaction record was produced.
