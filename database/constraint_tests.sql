
USE momo_sms_db;

START TRANSACTION;
UPDATE transactions SET amount = -1 WHERE transaction_id = 1;
ROLLBACK;

START TRANSACTION;
UPDATE transactions SET fee = -1 WHERE transaction_id = 1;
ROLLBACK;

START TRANSACTION;
UPDATE transactions SET financial_transaction_id = '76662021700'
WHERE transaction_id = 2;
ROLLBACK;

START TRANSACTION;
UPDATE transactions SET category_id = -1 WHERE transaction_id = 1;
ROLLBACK;

START TRANSACTION;
INSERT INTO transaction_tags (transaction_id, tag_id) VALUES (1, 1);
ROLLBACK;

START TRANSACTION;
DELETE FROM transaction_categories WHERE category_id = 1;
ROLLBACK;

START TRANSACTION;
UPDATE transactions SET amount = NULL WHERE transaction_id = 1;
ROLLBACK;

SELECT transaction_id, financial_transaction_id, category_id, amount, fee
FROM transactions WHERE transaction_id IN (1, 2) ORDER BY transaction_id;
