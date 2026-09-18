# Banco MySQL — Sistema de Reserva de Salas

## Estrutura

- `usuarios`: contas de acesso.
- `professores`: professores que podem solicitar reservas.
- `salas`: salas disponíveis para reserva.
- `reservas`: relacionamento entre professor e sala, com data, horário e status.

## Importar no MySQL Workbench

1. Abra o MySQL Workbench e conecte ao seu servidor.
2. Abra `schema.sql`.
3. Execute o script inteiro.
4. Use **Database > Reverse Engineer** para gerar o diagrama visual das tabelas e relacionamentos.

## Credenciais de teste

- `admin@faculdade.com` / `1234`
- `joao@faculdade.com` / `1234`

Para um sistema real, troque as senhas por hashes e não mantenha senhas em texto puro.
