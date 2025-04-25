USE `latency-recorder`;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS settings;
CREATE TABLE IF NOT EXISTS settings (
    name VARCHAR(255) NOT NULL PRIMARY KEY COMMENT 'Setting name',
    value TEXT NOT NULL COMMENT 'Setting value',
    description TEXT NOT NULL COMMENT 'Setting description',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp'
);

REPLACE INTO settings (name, value, description) VALUES
('app_name', 'Latency Recorder', 'The name of the application'),
('app_version', '0.1.0', 'The current version of the application'),
('app_description', 'This is a simple latency test application, aimed at measuring the latency of a network connection and providing a user-friendly interface for testing and displaying results.', 'The description of the application'),
('app_author', 'Baptiste P.', 'The author of the application'),
('app_license', 'GNU GPL v3', 'The license under which the application is distributed');

CREATE TABLE IF NOT EXISTS remote_servers (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Server ID',
    server_name VARCHAR(255) NOT NULL COMMENT 'Server name',
    server_hostname VARCHAR(255) NOT NULL COMMENT 'Server hostname or IP address',
    test_interval INT NOT NULL COMMENT 'Interval between tests in seconds',
    test_max_retries INT NOT NULL COMMENT 'Maximum number of retries for the test',
    test_timeout INT NOT NULL COMMENT 'Timeout for the test in seconds',
    test_active BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'Activation status of the test'
);

CREATE TABLE IF NOT EXISTS latency_tests (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Test ID',
    server_id INT NOT NULL COMMENT 'Server ID',
    result FLOAT NOT NULL COMMENT 'Test result in milliseconds',
    success BOOLEAN NOT NULL COMMENT 'Test success status',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
    FOREIGN KEY (server_id) REFERENCES remote_servers(id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- view summary of latency tests
CREATE VIEW latency_summary AS
SELECT
    r.id AS server_id,
    r.server_name,
    r.server_hostname,
    CONCAT(ROUND(AVG(CASE WHEN l.result <> 0 THEN l.result END), 2), ' ms') AS average_latency,
    CONCAT(MAX(CASE WHEN l.result <> 0 THEN l.result END), ' ms') AS max_latency,
    CONCAT(MIN(CASE WHEN l.result <> 0 THEN l.result END), ' ms') AS min_latency,
    COUNT(l.id) AS test_count,
    CASE 
        WHEN COUNT(l.id) > 0 THEN CONCAT(ROUND(100 * SUM(CASE WHEN l.success = 0 THEN 1 ELSE 0 END) / COUNT(l.id), 2), '%')
        ELSE '0%'
    END AS fail_rate
FROM
    remote_servers r
LEFT JOIN
    latency_tests l ON r.id = l.server_id
GROUP BY
    r.id;


SET FOREIGN_KEY_CHECKS = 1;
