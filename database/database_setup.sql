DROP DATABASE IF EXISTS momo_sms_db;
CREATE DATABASE momo_sms_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE momo_sms_db;

CREATE TABLE users (
    user_id        INT AUTO_INCREMENT PRIMARY KEY,
    full_name      VARCHAR(150) NOT NULL,
    phone_number   VARCHAR(20)  NULL,
    momo_code      VARCHAR(20)  NULL,
    user_type      ENUM('CUSTOMER','AGENT','MERCHANT','SYSTEM') NOT NULL DEFAULT 'CUSTOMER',
    created_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_users_phone UNIQUE (phone_number)
) ENGINE=InnoDB;

CREATE INDEX idx_users_name ON users (full_name);

CREATE TABLE transaction_categories (
    category_id    INT AUTO_INCREMENT PRIMARY KEY,
    category_code  VARCHAR(30)  NOT NULL,
    category_name  VARCHAR(100) NOT NULL,
    description    VARCHAR(255) NULL,
    CONSTRAINT uq_category_code UNIQUE (category_code)
) ENGINE=InnoDB;

CREATE TABLE transactions (
    transaction_id            INT AUTO_INCREMENT PRIMARY KEY,
    financial_transaction_id  VARCHAR(50)  NULL,
    category_id               INT NOT NULL,
    sender_id                 INT NULL,
    receiver_id                INT NULL,
    amount                     DECIMAL(12,2) NOT NULL,
    fee                        DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    new_balance                DECIMAL(12,2) NULL,
    currency                   CHAR(3) NOT NULL DEFAULT 'RWF',
    transaction_date           DATETIME NOT NULL,
    status                     ENUM('COMPLETED','FAILED','PENDING','REVERSED') NOT NULL DEFAULT 'COMPLETED',
    raw_message                TEXT NULL,
    created_at                 DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_transactions_fin_id UNIQUE (financial_transaction_id),
    CONSTRAINT fk_tx_category FOREIGN KEY (category_id) REFERENCES transaction_categories(category_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_tx_sender   FOREIGN KEY (sender_id)   REFERENCES users(user_id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_tx_receiver FOREIGN KEY (receiver_id) REFERENCES users(user_id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT chk_amount_nonneg CHECK (amount >= 0),
    CONSTRAINT chk_fee_nonneg    CHECK (fee >= 0)
) ENGINE=InnoDB;

CREATE INDEX idx_tx_date       ON transactions (transaction_date);
CREATE INDEX idx_tx_category   ON transactions (category_id);
CREATE INDEX idx_tx_sender     ON transactions (sender_id);
CREATE INDEX idx_tx_receiver   ON transactions (receiver_id);
CREATE INDEX idx_tx_status     ON transactions (status);

CREATE TABLE tags (
    tag_id    INT AUTO_INCREMENT PRIMARY KEY,
    tag_name  VARCHAR(50) NOT NULL,
    CONSTRAINT uq_tag_name UNIQUE (tag_name)
) ENGINE=InnoDB;


CREATE TABLE transaction_tags (
    transaction_id  INT NOT NULL,
    tag_id          INT NOT NULL,
    tagged_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (transaction_id, tag_id),
    CONSTRAINT fk_tt_transaction FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_tt_tag FOREIGN KEY (tag_id) REFERENCES tags(tag_id)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;


CREATE TABLE system_logs (
    log_id          INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id  INT NULL,
    log_level       ENUM('INFO','WARNING','ERROR','DEBUG') NOT NULL DEFAULT 'INFO',
    process_stage   VARCHAR(50) NOT NULL,
    message         TEXT NOT NULL,
    source_file     VARCHAR(255) NULL,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_log_transaction FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id)
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE INDEX idx_logs_level ON system_logs (log_level);
CREATE INDEX idx_logs_stage ON system_logs (process_stage);



INSERT INTO users (full_name, phone_number, momo_code, user_type) VALUES
('Jane Smith',        '250788000013', NULL,     'CUSTOMER'),
('Samuel Carter',     '250788000095', NULL,     'CUSTOMER'),
('Agent John',        '250788999999', 'AGT1001', 'AGENT'),
('Agent Sophia',      '250790777777', 'AGT1002', 'AGENT'),
('ONAFRIQ Merchant',  NULL,           'MER2050', 'MERCHANT'),
('Abebe Chala Chebudie', '250788000036', NULL,   'CUSTOMER');



INSERT INTO transaction_categories (category_code, category_name, description) VALUES
('RECEIVE_MONEY',   'Incoming Money',        'Money received from another MoMo user'),
('SEND_MONEY',       'Payment to Code Holder','Payment sent to a person or code holder'),
('BANK_DEPOSIT',     'Bank Deposit',          'Cash deposited into MoMo account from a bank'),
('AIRTIME',          'Airtime Purchase',      'Airtime top-up payment'),
('BUNDLE',           'Bundle Purchase',       'Data or voice bundle purchase'),
('CASH_POWER',       'Cash Power Payment',    'Utility/electricity token purchase'),
('WITHDRAWAL',       'Agent Withdrawal',      'Cash withdrawal via an agent'),
('THIRD_PARTY',      'Third-Party Transaction','Payment processed via a third-party merchant (e.g. ONAFRIQ)');



INSERT INTO transactions
    (financial_transaction_id, category_id, sender_id, receiver_id, amount, fee, new_balance, currency, transaction_date, status, raw_message)
VALUES
('76662021700', 1, 1, NULL, 2000.00, 0.00, 2000.00, 'RWF', '2024-05-10 16:30:51', 'COMPLETED',
 'You have received 2000 RWF from Jane Smith on your mobile money account.'),
('73214484437', 2, NULL, 1, 1000.00, 0.00, 1000.00, 'RWF', '2024-05-10 16:31:39', 'COMPLETED',
 'Your payment of 1,000 RWF to Jane Smith has been completed.'),
('51732411227', 2, NULL, 2, 600.00, 0.00, 400.00, 'RWF', '2024-05-10 21:32:32', 'COMPLETED',
 'Your payment of 600 RWF to Samuel Carter has been completed.'),
(NULL,          3, NULL, NULL, 40000.00, 0.00, 40400.00, 'RWF', '2024-05-11 18:43:49', 'COMPLETED',
 'A bank deposit of 40000 RWF has been added to your mobile money account.'),
('14103506143', 6, NULL, 5, 4000.00, 0.00, NULL, 'RWF', '2024-05-12 09:12:00', 'COMPLETED',
 'Your payment of 4000 RWF to MTN Cash Power with token.'),
(NULL,          7, 6, 3, 24000.00, 200.00, NULL, 'RWF', '2024-05-13 10:05:00', 'COMPLETED',
 'You have via agent: Agent John, withdrawn 24000 RWF.');



INSERT INTO tags (tag_name) VALUES
('promotion'), ('cross-border'), ('refunded'), ('high-value'), ('utility');



INSERT INTO transaction_tags (transaction_id, tag_id) VALUES
(1, 1), (1, 4), (4, 4), (5, 5), (6, 3);




INSERT INTO system_logs (transaction_id, log_level, process_stage, message, source_file) VALUES
(1, 'INFO',  'parse_xml',       'Successfully parsed SMS into transaction record', 'data/raw/momo.xml'),
(2, 'INFO',  'categorize',      'Categorized as SEND_MONEY', 'data/raw/momo.xml'),
(NULL, 'ERROR', 'parse_xml',    'Unable to parse malformed SMS body, moved to dead letter', 'data/raw/momo.xml'),
(4, 'INFO',  'load_db',         'Inserted bank deposit transaction into SQLite/MySQL', 'data/raw/momo.xml'),
(6, 'WARNING','clean_normalize','Agent phone number partially masked; matched by name+agent code', 'data/raw/momo.xml');
