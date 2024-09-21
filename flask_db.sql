create database flask_db;
use flask_db;
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE Category (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE Task (
    id INT AUTO_INCREMENT PRIMARY KEY,
    users_id INT,
    category_id INT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (users_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES Category(id)
);

INSERT INTO Category (name) VALUES ('Trabalho');
INSERT INTO Category (name) VALUES ('Pessoal');
INSERT INTO Category (name) VALUES ('Estudo');




