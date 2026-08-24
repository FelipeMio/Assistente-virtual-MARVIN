import datetime
import sqlite3
from pathlib import Path
from threading import Lock


# Diretório de dados do MARVIN
HOME = Path.home() / ".marvin"
HOME.mkdir(exist_ok=True)

DB_F = HOME / "marvin.db"

# Conexão com o banco
con = sqlite3.connect(str(DB_F), check_same_thread=False)
cursor = con.cursor()
_db_lock = Lock()


def _migrate():
    """Cria/atualiza o schema sem perder dados."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tarefas (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            texto        TEXT    NOT NULL,
            descricao    TEXT    DEFAULT '',
            data         TEXT    NOT NULL,
            hora         TEXT    NOT NULL,
            recorrencia  TEXT    DEFAULT 'Nunca',
            concluida    INTEGER DEFAULT 0,
            lembrado     INTEGER DEFAULT 0,
            ativo        INTEGER DEFAULT 1,
            criado_em    TEXT    DEFAULT NULL,
            concluido_em TEXT    DEFAULT NULL,
            prioridade   TEXT    DEFAULT 'Normal',
            data_base    TEXT    DEFAULT NULL,
            hora_base    TEXT    DEFAULT NULL
        )
    """)

    # Migração segura para bancos antigos.
    cols = {r[1] for r in cursor.execute("PRAGMA table_info(tarefas)")}

    for col in ("criado_em", "concluido_em"):
        if col not in cols:
            cursor.execute(
                f"ALTER TABLE tarefas ADD COLUMN {col} TEXT DEFAULT NULL"
            )

    if "prioridade" not in cols:
        cursor.execute(
            "ALTER TABLE tarefas "
            "ADD COLUMN prioridade TEXT DEFAULT 'Normal'"
        )

    if "data_base" not in cols:
        cursor.execute(
            "ALTER TABLE tarefas "
            "ADD COLUMN data_base TEXT DEFAULT NULL"
        )

    if "hora_base" not in cols:
        cursor.execute(
            "ALTER TABLE tarefas "
            "ADD COLUMN hora_base TEXT DEFAULT NULL"
        )

    # Tarefas antigas passam a usar sua data/hora atual
    # como programacao original.
    cursor.execute(
        "UPDATE tarefas "
        "SET data_base=data "
        "WHERE data_base IS NULL OR data_base=''"
    )

    cursor.execute(
        "UPDATE tarefas "
        "SET hora_base=hora "
        "WHERE hora_base IS NULL OR hora_base=''"
    )

    con.commit()


_migrate()


def db_criar(
    texto,
    descricao,
    data,
    hora,
    recorrencia,
    prioridade="Normal"
):
    with _db_lock:
        agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(
            "INSERT INTO tarefas "
            "(texto,descricao,data,hora,recorrencia,criado_em,prioridade,"
            "data_base,hora_base) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (
                texto,
                descricao,
                data,
                hora,
                recorrencia,
                agora,
                prioridade,
                data,
                hora,
            ),
        )

        con.commit()


def db_listar(apenas_pendentes=False):
    with _db_lock:
        q = (
            "SELECT id,texto,descricao,data,hora,recorrencia,"
            "concluida,lembrado "
            "FROM tarefas WHERE ativo=1"
        )

        if apenas_pendentes:
            q += " AND concluida=0"

        q += (
            " ORDER BY "
            "CASE prioridade "
            "WHEN 'Alta' THEN 0 "
            "WHEN 'Normal' THEN 1 "
            "WHEN 'Baixa' THEN 2 "
            "ELSE 1 END, "
            "data,hora"
        )

        cursor.execute(q)
        return cursor.fetchall()


def db_prioridade(tid):
    with _db_lock:
        cursor.execute(
            "SELECT prioridade FROM tarefas WHERE id=?",
            (tid,),
        )

        row = cursor.fetchone()

        if not row or not row[0]:
            return "Normal"

        prioridade = str(row[0]).strip()

        if prioridade not in (
            "Baixa",
            "Normal",
            "Alta",
        ):
            return "Normal"

        return prioridade


def _proxima_data_recorrente(
    data_atual,
    recorrencia,
    data_base=None
):
    """
    Calcula a proxima ocorrencia de uma tarefa recorrente.

    A data salva na tarefa representa sempre a proxima
    ocorrencia que ainda precisa ser feita.
    """
    hoje = datetime.date.today()

    try:
        original = datetime.date.fromisoformat(data_atual)
    except (TypeError, ValueError):
        original = hoje

    # Se a tarefa estiver atrasada, partimos de hoje.
    base = max(original, hoje)

    if recorrencia == "Todo dia":
        return base + datetime.timedelta(days=1)

    if recorrencia == "Toda semana":
        # Mantem o dia da semana original mesmo que
        # esta ocorrencia tenha sido adiada.
        try:
            ancora = datetime.date.fromisoformat(
                data_base
            )
        except (TypeError, ValueError):
            ancora = original

        alvo = ancora.weekday()

        candidato = base + datetime.timedelta(days=1)

        while candidato.weekday() != alvo:
            candidato += datetime.timedelta(days=1)

        return candidato

    if recorrencia == "Seg/Qua/Sex":
        permitidos = {0, 2, 4}

    elif recorrencia == "Seg a Sex":
        permitidos = {0, 1, 2, 3, 4}

    elif recorrencia == "Fins de semana":
        permitidos = {5, 6}

    else:
        return None

    candidato = base + datetime.timedelta(days=1)

    while candidato.weekday() not in permitidos:
        candidato += datetime.timedelta(days=1)

    return candidato


def db_concluir(tid):
    agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with _db_lock:
        cursor.execute(
            "SELECT data,hora,recorrencia,data_base,hora_base "
            "FROM tarefas WHERE id=?",
            (tid,),
        )

        row = cursor.fetchone()

        if not row:
            return

        (
            data_atual,
            hora_atual,
            recorrencia,
            data_base,
            hora_base,
        ) = row

        # Tarefa comum: comportamento antigo.
        if recorrencia == "Nunca":
            cursor.execute(
                "UPDATE tarefas "
                "SET concluida=1, lembrado=1, concluido_em=? "
                "WHERE id=?",
                (agora, tid),
            )

        else:
            proxima = _proxima_data_recorrente(
                data_atual,
                recorrencia,
                data_base,
            )

            if proxima is None:
                # Protecao caso exista uma recorrencia desconhecida.
                cursor.execute(
                    "UPDATE tarefas "
                    "SET concluida=1, lembrado=1, concluido_em=? "
                    "WHERE id=?",
                    (agora, tid),
                )

            else:
                # A tarefa recorrente continua ativa.
                # Apenas avancamos para a proxima ocorrencia.
                cursor.execute(
                    "UPDATE tarefas "
                    "SET data=?, "
                    "hora=?, "
                    "concluida=0, "
                    "lembrado=0, "
                    "concluido_em=? "
                    "WHERE id=?",
                    (
                        proxima.isoformat(),
                        hora_base or hora_atual,
                        agora,
                        tid,
                    ),
                )

        con.commit()

def db_desconcluir(tid):
    with _db_lock:
        cursor.execute(
            "UPDATE tarefas "
            "SET concluida=0, concluido_em=NULL "
            "WHERE id=?",
            (tid,),
        )

        con.commit()

def db_excluir(tid):
    with _db_lock:
        cursor.execute(
            "UPDATE tarefas SET ativo=0 WHERE id=?",
            (tid,),
        )

        con.commit()


def db_alterar(tid, campo, valor):
    campos_validos = {
        "texto",
        "descricao",
        "data",
        "hora",
        "recorrencia",
        "prioridade",
    }

    if campo not in campos_validos:
        raise ValueError(
            f"Campo invalido: {campo}"
        )

    with _db_lock:
        if campo == "data":
            cursor.execute(
                "UPDATE tarefas "
                "SET data=?,data_base=? "
                "WHERE id=?",
                (valor, valor, tid),
            )

        elif campo == "hora":
            cursor.execute(
                "UPDATE tarefas "
                "SET hora=?,hora_base=? "
                "WHERE id=?",
                (valor, valor, tid),
            )

        else:
            cursor.execute(
                f"UPDATE tarefas SET {campo}=? WHERE id=?",
                (valor, tid),
            )

        con.commit()


def db_marcar_lembrado(tid):
    with _db_lock:
        cursor.execute(
            "UPDATE tarefas SET lembrado=1 WHERE id=?",
            (tid,),
        )

        con.commit()


def db_reset_lembrado(tid):
    with _db_lock:
        cursor.execute(
            "UPDATE tarefas SET lembrado=0 WHERE id=?",
            (tid,),
        )

        con.commit()


def db_adiar(tid, nova_data, nova_hora):
    with _db_lock:
        cursor.execute(
            "UPDATE tarefas "
            "SET data=?,hora=?,lembrado=0 "
            "WHERE id=?",
            (nova_data, nova_hora, tid),
        )

        con.commit()


def db_streak_hoje():
    hoje = datetime.date.today().strftime("%Y-%m-%d")

    with _db_lock:
        cursor.execute(
            "SELECT COUNT(*) FROM tarefas "
            "WHERE ativo=1 "
            "AND concluido_em IS NOT NULL "
            "AND substr(concluido_em,1,10)=?",
            (hoje,),
        )

        return cursor.fetchone()[0]


def db_limpar_antigas(dias=30):
    corte = (
        datetime.date.today() -
        datetime.timedelta(days=dias)
    ).isoformat()

    with _db_lock:
        cursor.execute(
            "DELETE FROM tarefas "
            "WHERE concluida=1 "
            "AND concluido_em IS NOT NULL "
            "AND substr(concluido_em,1,10)<?",
            (corte,),
        )

        con.commit()

def db_obter(tid):
    with _db_lock:
        cursor.execute(
            "SELECT texto,descricao,data,hora,recorrencia,prioridade "
            "FROM tarefas WHERE id=?",
            (tid,),
        )

        return cursor.fetchone()