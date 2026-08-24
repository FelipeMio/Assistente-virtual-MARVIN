#  MARVIN — Assistente Virtual

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite)
![Status](https://img.shields.io/badge/Status-Em%20desenvolvimento-orange)

> Um assistente virtual para desktop desenvolvido em Python.

##  Sobre o projeto

MARVIN é um assistente virtual para desktop desenvolvido em Python.

O projeto possui uma interface gráfica com um personagem em pixel art,
sistema de gerenciamento de tarefas, lembretes e configurações persistentes.

O objetivo do projeto é criar um assistente virtual que possa acompanhar
o usuário durante o uso do computador e futuramente receber comandos por voz
e utilizar inteligência artificial.

---

##  Funcionalidades

-  Criar tarefas
-  Editar tarefas
-  Concluir tarefas
-  Excluir tarefas
-  Sistema de lembretes
-  Tarefas recorrentes
-  Adiar lembretes
-  Notificações sonoras
-  Modo Não Perturbe
-  Configurações persistentes
-  Banco de dados SQLite
-  Personagem animado em pixel art
-  Interface gráfica com Tkinter

---

##  Tecnologias utilizadas

- Python
- Tkinter
- SQLite
- JSON
- Threading

---

##  Como executar

### 1. Clone o repositório

```bash
git clone https://github.com/FelipeMio/Assistente-virtual-MARVIN.git

## 🧩 Extensões

O MARVIN possui suporte a extensões opcionais.

As extensões adicionam funcionalidades extras sem alterar o funcionamento
principal do assistente. Quem não precisa delas pode utilizar o MARVIN
normalmente.

### 📊 Monitor GOE

O Monitor GOE é uma extensão opcional criada para acompanhar
automaticamente um monitoramento baseado em dados exportados para CSV.

Ele pode:

- avisar quando o monitoramento retorna `0`;
- manter o alerta aberto até o usuário confirmar;
- avisar quando o monitoramento volta ao normal;
- informar a cada hora que o monitoramento continua funcionando.

O MARVIN principal **não depende do GOE**.

Quem deseja utilizar apenas tarefas, lembretes e as funções normais do
MARVIN não precisa configurar nada.

➡️ [Documentação completa do Monitor GOE](extensions/goe/README.md)
