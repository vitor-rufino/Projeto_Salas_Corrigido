CREATE DATABASE IF NOT EXISTS sistema_reserva_salas;

USE sistema_reserva_salas;

CREATE TABLE usuarios (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    email VARCHAR(160) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    tipo ENUM('Administrador', 'Professor') NOT NULL
);

CREATE TABLE salas (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(120) NOT NULL UNIQUE,
    capacidade INT UNSIGNED NOT NULL,
    localizacao VARCHAR(160),
    projetor ENUM('Sim', 'Não') DEFAULT 'Não',
    computadores INT UNSIGNED DEFAULT 0,
    status ENUM('Disponível', 'Indisponível')
        DEFAULT 'Disponível'
);

CREATE TABLE professores (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    email VARCHAR(160) NOT NULL UNIQUE,
    departamento VARCHAR(160)
);

CREATE TABLE reservas (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    professor_id INT UNSIGNED NOT NULL,
    sala_id INT UNSIGNED NOT NULL,

    data DATE NOT NULL,
    horario_inicio TIME NOT NULL,
    horario_fim TIME NOT NULL,

    finalidade VARCHAR(500),

    status ENUM(
        'Pendente',
        'Aprovada',
        'Recusada',
        'Cancelada'
    ) DEFAULT 'Pendente',

    FOREIGN KEY (professor_id)
        REFERENCES professores(id),

    FOREIGN KEY (sala_id)
        REFERENCES salas(id)

);