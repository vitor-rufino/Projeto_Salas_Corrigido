# Sistema de Reserva de Salas — versão corrigida

## Como executar

1. Instale Python 3.11+.
2. Abra esta pasta no VS Code.
3. No terminal, execute:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

4. Abra o endereço mostrado pelo Streamlit, normalmente `http://localhost:8501`.

**Não use o Live Server do VS Code para executar o `app.py`.**

## Login de teste

Administrador:
- E-mail: `admin@faculdade.com`
- Senha: `1234`

Professor:
- E-mail: `joao@faculdade.com`
- Senha: `1234`

## Correções incluídas

- Login inicializado automaticamente.
- Usuários iniciais criados sem duplicação.
- Caminho do `reservas.db` fixado na pasta do projeto.
- `PRAGMA foreign_keys = ON` ativado.
- Menu lateral com **uma única chave** (`menu_principal`), evitando `StreamlitDuplicateElementId`.
- Chaves únicas nos campos e botões dinâmicos.
- Formulários reorganizados para evitar widgets duplicados.
- Cadastro, edição e exclusão de salas.
- Cadastro, edição e exclusão de professores.
- Solicitação e cancelamento de reservas.
- Aprovação/recusa de reservas pelo administrador.
- Revalidação de conflito no momento da aprovação.
- Data de reserva não pode ser anterior ao dia atual.

## Banco MySQL

A pasta `mysql/` contém o modelo equivalente para MySQL, incluindo `schema.sql` e o diagrama relacional.

O aplicativo desta versão usa SQLite por padrão para funcionar imediatamente. O schema MySQL pode ser importado no MySQL Workbench ou pelo cliente `mysql`.
