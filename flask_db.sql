create database flask_db;
use flask_db;
CREATE TABLE tb_users (
    use_id INT AUTO_INCREMENT PRIMARY KEY,
    use_username VARCHAR(150) NOT NULL,
    use_email VARCHAR(150) UNIQUE NOT NULL,
    use_password VARCHAR(255) NOT NULL
);

CREATE TABLE tb_category (
    cat_id INT AUTO_INCREMENT PRIMARY KEY,
    cat_name VARCHAR(100) NOT NULL
);

CREATE TABLE tb_task (
    tas_id INT AUTO_INCREMENT PRIMARY KEY,
    tas_use_id INT,
    tas_cat_id INT,
    tas_title VARCHAR(255) NOT NULL,
    tas_description TEXT,
    tas_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tas_use_id) REFERENCES tb_users(use_id) ON DELETE CASCADE,
    FOREIGN KEY (tas_cat_id) REFERENCES tb_category(cat_id)
);

INSERT INTO tb_category (cat_name) VALUES ('Trabalho');
INSERT INTO tb_category (cat_name) VALUES ('Pessoal');
INSERT INTO tb_category (cat_name) VALUES ('Estudo');
