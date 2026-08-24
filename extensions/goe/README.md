# 📊 MARVIN — Monitor GOE

O Monitor GOE é uma extensão opcional do MARVIN criada para acompanhar
automaticamente um monitoramento horário.

A extensão não acessa diretamente o banco de dados.

Em vez disso, ela observa um arquivo CSV que pode ser atualizado por
Navicat, outro cliente SQL ou qualquer processo capaz de gerar o arquivo
no formato esperado.

---

## Como funciona

O fluxo é:

SQL / Navicat
      ↓
gera um CSV
      ↓
MARVIN detecta a atualização
      ↓
verifica a última hora completa
      ↓
QTDE > 0 → monitoramento normal
QTDE = 0 → alerta persistente

Por exemplo:

Às `15:05`, o sistema deve gerar os dados referentes ao período:

`14:00:00 → 14:59:59`

O MARVIN recebe o resultado da hora `14`.

Se:

`QTDE > 0`

o MARVIN pode informar:

> Por enquanto, GOE tudo certo! 14h: 125430 registros.

Se:

`QTDE = 0`

o MARVIN mostra:

> Ei, o GOE parou! A hora das 14h retornou 0.

Também é aberta uma janela persistente.

O alerta permanece até o usuário clicar em `OK`.

---

# Requisitos

É necessário:

- MARVIN funcionando;
- Python configurado;
- um arquivo CSV atualizado automaticamente;
- Windows para os recursos atuais de notificação;
- Navicat apenas se ele for utilizado para gerar o CSV.

O MARVIN não precisa conhecer usuário, senha ou endereço do banco.

---

# Estrutura da extensão

```text
extensions/
└── goe/
    ├── __init__.py
    ├── monitor.py
    ├── config.example.json
    └── README.md