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
            prioridade   TEXT    DEFAULT 'Normal'
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
            "(texto,descricao,data,hora,recorrencia,criado_em,prioridade) "
            "VALUES (?,?,?,?,?,?,?)",
            (
                texto,
                descricao,
                data,
                hora,
                recorrencia,
                agora,
                prioridade,
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


def db_concluir(tid):
    agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with _db_lock:
        cursor.execute(
            "UPDATE tarefas "
            "SET concluida=1, lembrado=1, concluido_em=? "
            "WHERE id=?",
            (agora, tid),
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
    with _db_lock:
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
            "WHERE ativo=1 AND concluida=1 "
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