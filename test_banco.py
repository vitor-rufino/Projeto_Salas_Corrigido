from banco import conectar, criar_banco, criar_usuarios_iniciais

criar_banco()
criar_usuarios_iniciais()
with conectar() as c:
    assert c.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] >= 2
    assert c.execute("SELECT COUNT(*) FROM professores").fetchone()[0] >= 1
    assert c.execute("SELECT COUNT(*) FROM salas").fetchone()[0] >= 1
print("OK: banco e usuários iniciais funcionando.")
