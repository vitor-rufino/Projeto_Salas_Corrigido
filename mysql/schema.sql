CREATE DATABASE IF NOT EXISTS sistema_reserva_salas
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE sistema_reserva_salas;

CREATE TABLE IF NOT EXISTS usuarios (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nome VARCHAR(120) NOT NULL,
    email VARCHAR(160) NOT NULL,
    senha VARCHAR(255) NOT NULL,
    tipo ENUM('Administrador','Professor') NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_usuarios_email (email)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS professores (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nome VARCHAR(120) NOT NULL,
    email VARCHAR(160) NOT NULL,
    departamento VARCHAR(160) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_professores_email (email)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS salas (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nome VARCHAR(120) NOT NULL,
    capacidade INT UNSIGNED NOT NULL,
    localizacao VARCHAR(160) NOT NULL,
    projetor ENUM('Sim','Não') NOT NULL DEFAULT 'Não',
    computadores INT UNSIGNED NOT NULL DEFAULT 0,
    status ENUM('Disponível','Indisponível') NOT NULL DEFAULT 'Disponível',
    PRIMARY KEY (id),
    UNIQUE KEY uq_salas_nome (nome)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS reservas (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    professor_id INT UNSIGNED NOT NULL,
    sala_id INT UNSIGNED NOT NULL,
    data DATE NOT NULL,
    horario_inicio TIME NOT NULL,
    horario_fim TIME NOT NULL,
    finalidade VARCHAR(500) NOT NULL,
    status ENUM('Pendente','Aprovada','Recusada','Cancelada') NOT NULL DEFAULT 'Pendente',
    PRIMARY KEY (id),
    KEY idx_reservas_professor (professor_id),
    KEY idx_reservas_sala_data (sala_id, data),
    CONSTRAINT fk_reservas_professor FOREIGN KEY (professor_id) REFERENCES professores(id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_reservas_sala FOREIGN KEY (sala_id) REFERENCES salas(id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

INSERT INTO usuarios (nome,email,senha,tipo) VALUES
('Administrador','admin@faculdade.com','1234','Administrador'),
('João da Silva','joao@faculdade.com','1234','Professor')
ON DUPLICATE KEY UPDATE nome=VALUES(nome), tipo=VALUES(tipo);

INSERT INTO professores (nome,email,departamento) VALUES
('João da Silva','joao@faculdade.com','Curso: Engenharia da Computação')
ON DUPLICATE KEY UPDATE nome=VALUES(nome), departamento=VALUES(departamento);

INSERT INTO salas (nome,capacidade,localizacao,projetor,computadores,status) VALUES
('laboratorio 01',30,'Bloco A','Sim',30,'Disponível')
ON DUPLICATE KEY UPDATE capacidade=VALUES(capacidade), localizacao=VALUES(localizacao), projetor=VALUES(projetor), computadores=VALUES(computadores), status=VALUES(status);
