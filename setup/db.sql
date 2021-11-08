CREATE DATABASE chat;
CREATE TABLE chat.channels (sid INT NOT NULL PRIMARY KEY,channel_name VARCHAR(128) NOT NULL UNIQUE,create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,is_active BOOLEAN DEFAULT true);
-- INSERT INTO chat.channels (sid, channel_name) VALUES (1, 'test_channel_name');
CREATE TABLE chat.configurations ( var_name VARCHAR(64) PRIMARY KEY, var_value TEXT );
-- keys replaced for security.
INSERT INTO chat.configurations (var_name, var_value) VALUES ('service_keys', 'pubplaceholderkey:subplaceholderkey');
-- development password
CREATE USER 'chatmanager'@'localhost' IDENTIFIED BY 'chatpassword';
GRANT SELECT ON chat.* TO 'chatmanager'@'localhost';
GRANT INSERT ON chat.* TO 'chatmanager'@'localhost';
GRANT DELETE ON chat.* TO 'chatmanager'@'localhost';

CREATE DATABASE game;
CREATE TABLE game.sessions (id INT AUTO_INCREMENT PRIMARY KEY, session_name VARCHAR(128) UNIQUE NOT NULL);
-- INSERT INTO game.sessions (session_name) VALUES ('test_session_name');
GRANT SELECT ON game.* TO 'chatmanager'@'localhost';