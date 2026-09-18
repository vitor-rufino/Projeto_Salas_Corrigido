from pathlib import Path
import sqlite3


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "reservas.db"



def conectar():
    conexao = sqlite3.connect(DB_PATH)
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def criar_banco():
    with conectar() as conexao:
        cursor = conexao.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS salas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                capacidade INTEGER NOT NULL CHECK(capacidade > 0),
                localizacao TEXT NOT NULL,
                projetor TEXT NOT NULL DEFAULT 'Não' CHECK(projetor IN ('Sim','Não')),
                computadores INTEGER NOT NULL DEFAULT 0 CHECK(computadores >= 0),
                status TEXT NOT NULL DEFAULT 'Disponível' CHECK(status IN ('Disponível','Indisponível'))
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS professores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                departamento TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                senha TEXT NOT NULL,
                tipo TEXT NOT NULL CHECK(tipo IN ('Administrador','Professor'))
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reservas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                professor_id INTEGER NOT NULL,
                sala_id INTEGER NOT NULL,
                data TEXT NOT NULL,
                horario_inicio TEXT NOT NULL,
                horario_fim TEXT NOT NULL,
                finalidade TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pendente' CHECK(status IN ('Pendente','Aprovada','Recusada','Cancelada')),
                FOREIGN KEY (professor_id) REFERENCES professores(id) ON UPDATE CASCADE ON DELETE RESTRICT,
                FOREIGN KEY (sala_id) REFERENCES salas(id) ON UPDATE CASCADE ON DELETE RESTRICT
            )
        """)
        conexao.commit()



def criar_usuarios_iniciais():
    criar_banco()
    with conectar() as conexao:
        usuarios = [
            ("Administrador", "admin@faculdade.com", "1234", "Administrador"),
            ("João da Silva", "joao@faculdade.com", "1234", "Professor"),
        ]
        for usuario in usuarios:
            conexao.execute(
                "INSERT OR IGNORE INTO usuarios (nome,email,senha,tipo) VALUES (?,?,?,?)",
                usuario,
            )
        conexao.execute(
            """
            INSERT OR IGNORE INTO professores (nome,email,departamento)
            VALUES ('João da Silva','joao@faculdade.com','Curso: Engenharia da Computação')
            """
        )
        conexao.commit()


if __name__ == "__main__":
    criar_banco()
    criar_usuarios_iniciais()
    print(f"Banco criado/atualizado em: {DB_PATH}")
