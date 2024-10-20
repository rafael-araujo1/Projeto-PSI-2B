create database db_flask;
use db_flask;
CREATE TABLE tb_users (
    use_id INT AUTO_INCREMENT PRIMARY KEY,
    use_username VARCHAR(150) NOT NULL,
    use_email VARCHAR(150) UNIQUE NOT NULL,
    use_password VARCHAR(255) NOT NULL
);

CREATE TABLE tb_task (
    tas_id INT AUTO_INCREMENT PRIMARY KEY,
    tas_use_id INT,
    tas_title VARCHAR(255) NOT NULL,
    tas_description TEXT,
    tas_categoria ENUM("Trabalho", "Pessoal", "Estudo") NOT NULL,
    tas_status ENUM("Concluída", "Em andamento", "Pendente") NOT NULL,
    tas_prioridade ENUM("baixa", "média", "alta") NOT NULL,
    tas_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tas_data_limite DATETIME,
    FOREIGN KEY (tas_use_id) REFERENCES tb_users(use_id) ON DELETE CASCADE
);
