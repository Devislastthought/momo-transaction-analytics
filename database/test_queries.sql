
USE momo_sms_db;


SELECT VERSION() AS server_version, @@version_comment AS server_type;
SHOW TABLES;
SELECT 'users' AS table_name, COUNT(*) AS row_count FROM users
UNION ALL SELECT 'transaction_categories', COUNT(*) FROM transaction_categories
UNION ALL SELECT 'transactions', COUNT(*) FROM transactions
UNION ALL SELECT 'tags', COUNT(*) FROM tags
UNION ALL SELECT 'transaction_tags', COUNT(*) FROM transaction_tags
UNION ALL SELECT 'system_logs', COUNT(*) FROM system_logs;


SELECT t.transaction_id, t.amount, t.currency, c.category_name,
       s.full_name AS sender, r.full_name AS receiver,
       GROUP_CONCAT(g.tag_name ORDER BY g.tag_name SEPARATOR ', ') AS tags
FROM transactions t
JOIN transaction_categories c ON c.category_id = t.category_id
LEFT JOIN users s ON s.user_id = t.sender_id
LEFT JOIN users r ON r.user_id = t.receiver_id
LEFT JOIN transaction_tags tt ON tt.transaction_id = t.transaction_id
LEFT JOIN tags g ON g.tag_id = tt.tag_id
GROUP BY t.transaction_id, t.amount, t.currency, c.category_name,
         s.full_name, r.full_name
ORDER BY t.transaction_id;


SELECT c.category_name, COUNT(t.transaction_id) AS transaction_count,
       COALESCE(SUM(t.amount), 0) AS total_amount
FROM transaction_categories c
LEFT JOIN transactions t ON t.category_id = c.category_id
GROUP BY c.category_id, c.category_name
ORDER BY c.category_id;


START TRANSACTION;
INSERT INTO transactions
    (financial_transaction_id, category_id, sender_id, receiver_id,
     amount, fee, new_balance, transaction_date)
VALUES ('TEST-CRUD-001', 1, 2, 1, 5000.00, 0.00, 7000.00, '2026-09-15 12:00:00');
SET @test_transaction_id = LAST_INSERT_ID();
SELECT transaction_id, financial_transaction_id, amount, status
FROM transactions WHERE transaction_id = @test_transaction_id;

UPDATE transactions SET status = 'REVERSED'
WHERE transaction_id = @test_transaction_id;
SELECT transaction_id, amount, status
FROM transactions WHERE transaction_id = @test_transaction_id;

DELETE FROM transactions WHERE transaction_id = @test_transaction_id;
SELECT COUNT(*) AS remaining_rows
FROM transactions WHERE transaction_id = @test_transaction_id;
ROLLBACK;


START TRANSACTION;
SELECT * FROM transaction_tags WHERE transaction_id = 1;
SELECT log_id, transaction_id FROM system_logs WHERE log_id = 1;
DELETE FROM transactions WHERE transaction_id = 1;
SELECT COUNT(*) AS remaining_links
FROM transaction_tags WHERE transaction_id = 1;
SELECT log_id, transaction_id FROM system_logs WHERE log_id = 1;
ROLLBACK;
SELECT * FROM transaction_tags WHERE transaction_id = 1;
SELECT log_id, transaction_id FROM system_logs WHERE log_id = 1;


SHOW CREATE TABLE transactions;
SHOW FULL COLUMNS FROM transactions;
SHOW INDEX FROM transactions;


SELECT COUNT(*) AS transaction_count, SUM(amount) AS total_amount,
       SUM(fee) AS total_fees FROM transactions;
SELECT COUNT(*) AS leftover_test_rows
FROM transactions WHERE financial_transaction_id = 'TEST-CRUD-001';
