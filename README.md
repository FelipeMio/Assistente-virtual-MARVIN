# MARVIN — Assistente Virtual

<p align="center">
  <img src="assets/marvin/app_icon_preview.png" alt="MARVIN" width="128">
</p>

![Testes](https://github.com/FelipeMio/Assistente-virtual-MARVIN/actions/workflows/tests.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Windows](https://img.shields.io/badge/Windows-Desktop-0078D4?logo=windows)
![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite)
![Version](https://img.shields.io/badge/version-0.1.0-D97757)
![Status](https://img.shields.io/badge/status-em%20desenvolvimento-orange)

> Um assistente virtual para desktop que vive na tela, organiza tarefas e ajuda a acompanhar o dia sem precisar abrir um aplicativo o tempo todo.

---

## Sobre o MARVIN

O **MARVIN** é um assistente virtual para Windows desenvolvido em Python.

Em vez de funcionar apenas como uma lista de tarefas tradicional, o MARVIN permanece na área de trabalho como um pequeno personagem animado e interativo.

Ele combina:

- gerenciamento de tarefas;
- lembretes;
- tarefas recorrentes;
- checklist diário;
- resumo do dia;
- prioridades e filtros;
- configurações persistentes;
- personagem animado em pixel art;
- suporte a extensões opcionais.

O projeto ainda está em desenvolvimento e novas funções serão adicionadas gradualmente.

---

## Criação do personagem

O personagem MARVIN foi criado em pixel art utilizando o editor online [Pixel Art App](https://pixelartapp.com/editor).

A identidade visual do personagem foi desenvolvida especificamente para o projeto.

---

## Funcionalidades

### Tarefas

- Criar, editar, concluir, reabrir e excluir tarefas
- Adicionar descrição
- Definir data e horário
- Definir prioridade: Alta, Média, Baixa ou Nenhuma
- Pesquisar tarefas
- Filtrar por status e por prioridade

### Captura rápida

Pressione **`Ctrl+Alt+M`** em qualquer programa (ou use o menu da bandeja) e escreva a tarefa como você falaria:

| Você escreve | O MARVIN cria |
| --- | --- |
| `reunião com o time amanhã 15h` | Reunião com o time — amanhã, 15:00 |
| `pagar boleto dia 20 prioridade alta` | Pagar boleto — dia 20, 09:00, prioridade alta |
| `beber água todo dia 10h` | Beber água — todo dia, 10:00 |
| `ligar pro cliente sexta 9h30` | Ligar pro cliente — sexta, 09:30 |
| `revisar relatório em 2 horas` | Revisar relatório — daqui a 2 horas |

Uma prévia mostra o que foi entendido antes de salvar. Tudo é interpretado localmente, sem internet.

Se o atalho não responder (algum outro programa pode estar usando a mesma combinação), troque-o em **Configurações → Atalhos**: clique no botão, pressione a nova combinação e ela passa a valer na hora.

### Enquanto você estava fora

Quando o computador fica parado por 10 minutos ou mais (inclusive com a tela bloqueada), o MARVIN percebe a ausência. Na volta, ele mostra um resumo único do período:

- avisos recebidos, separados por origem (ex.: B2B, GOE);
- lembretes que venceram enquanto você não estava;
- itens do checklist ainda pendentes;
- o próximo compromisso.

Cada item tem um atalho para a tela correspondente. O resumo não toma o foco do teclado e pode ser desligado em **Configurações → Comportamento → Resumo ao voltar**.

### Recorrência

O MARVIN suporta tarefas:

- únicas;
- todos os dias;
- toda semana;
- segunda, quarta e sexta;
- segunda a sexta;
- fins de semana.

### Lembretes

Quando chega o horário de uma tarefa, o MARVIN exibe um alerta diretamente ao lado do personagem.

O lembrete permite concluir a tarefa ou adiá-la por 5 minutos, 15 minutos, 30 minutos ou 1 hora.

### Central do MARVIN

O menu principal, aberto com o **botão direito** no personagem, reúne:

- tarefas;
- criação de nova tarefa;
- checklist diário;
- resumo do dia;
- extensões;
- configurações.

### Checklist diário

Além das tarefas tradicionais, o MARVIN possui um checklist para atividades recorrentes do dia a dia.

### Resumo do dia

A Central apresenta informações do dia e permite acompanhar o andamento das tarefas.

### Personagem

O MARVIN permanece na área de trabalho com animações em pixel art e diferentes estados visuais (parado, esperando, feliz, alerta, bocejando).

Também existe um **modo compacto** para ocupar menos espaço na tela.

### Configurações

As preferências, as tarefas e os logs ficam salvos localmente em `%USERPROFILE%\.marvin` e são preservados entre as execuções.

---

## Instalação

### Para usuários

Baixe o instalador `MARVIN-Setup.exe` na página de [Releases](https://github.com/FelipeMio/Assistente-virtual-MARVIN/releases) e siga as etapas.

### Para desenvolvedores

Requisitos: Windows e Python 3.10 ou mais recente.

```powershell
git clone https://github.com/FelipeMio/Assistente-virtual-MARVIN.git
cd Assistente-virtual-MARVIN

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
python run_marvin.py
```

---

## Testes

```powershell
pip install -r requirements-dev.txt
python -m pytest
```

Os testes também rodam automaticamente no GitHub Actions a cada push e pull request.

---

## Gerando o executável e o instalador

```powershell
pip install -r requirements-build.txt

# Apenas o executável (dist\MARVIN\MARVIN.exe)
.\build_marvin.ps1

# Executável + instalador (release\MARVIN-Setup.exe) — requer Inno Setup 6 ou 7
.\build_installer.ps1
```

---

## Extensões

O MARVIN carrega automaticamente as extensões da pasta `extensions/`.

Cada extensão é uma pasta com um `__init__.py` que expõe a função:

```python
def iniciar_extensao(marvin):
    ...
```

A extensão recebe uma `ExtensionAPI` (`marvin/extension_api.py`), que dá acesso à janela principal, às notificações e ao estado do personagem sem depender dos detalhes internos do aplicativo.

Extensões incluídas:

| Extensão | Descrição |
| --- | --- |
| [`goe`](extensions/goe/README.md) | Monitora um CSV atualizado periodicamente e avisa quando a contagem de uma hora vem zerada. |
| `b2b_telegram` | Lê mensagens de um bot do Telegram e mostra alertas de novos arquivos recebidos. |

As configurações das extensões ficam fora do repositório (por exemplo, `extensions/goe/config.json` ou `%USERPROFILE%\.marvin\extensions\...`) e **nunca devem ser enviadas ao GitHub**, porque podem conter caminhos e tokens.

---

## Estrutura do projeto

```text
.
├── run_marvin.py          # ponto de entrada
├── marvin/
│   ├── main.py            # MarvinCompanion (janela principal e orquestração)
│   ├── database.py        # tarefas em SQLite
│   ├── config.py          # configurações do usuário
│   ├── reminders.py       # fila e serviço de lembretes
│   ├── notifications.py   # central de notificações
│   ├── extension_api.py   # API pública para extensões
│   ├── extension_loader.py
│   ├── ui/                # janelas (tarefas, configurações, central...)
│   └── assets/            # sprites do personagem
├── extensions/            # extensões opcionais
├── tests/                 # testes com pytest
├── installer/             # script do Inno Setup
└── MARVIN.spec            # configuração do PyInstaller
```

---

## Autor

Desenvolvido por [Felipe Mio](https://github.com/FelipeMio).
