import datetime
import sqlite3
from pathlib import Path


DB_FILE = (
    Path.home()
    / ".marvin"
    / "goe_history.db"
)


def _conectar():
    DB_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    con = sqlite3.connect(
        str(DB_FILE),
        timeout=10,
    )

    con.row_factory = sqlite3.Row

    return con


def _migrar():
    with _conectar() as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS goe_historico (
                data TEXT NOT NULL,
                hora INTEGER NOT NULL,
                qtde INTEGER NOT NULL,
                registrado_em TEXT NOT NULL,

                PRIMARY KEY (
                    data,
                    hora
                )
            )
            """
        )

        con.commit()


_migrar()


def registrar_leitura(
    status,
    exigir_atual=True,
):
    """
    Salva uma hora valida do GOE.

    Se a mesma data/hora ja existir,
    apenas atualiza a quantidade.
    """

    if not status.get("ok"):
        return False

    if (
        exigir_atual
        and not status.get("atual")
    ):
        return False

    data = status.get("data")
    hora = status.get("hora")
    qtde = status.get("qtde")

    if isinstance(
        data,
        datetime.datetime,
    ):
        data = data.date()

    if isinstance(
        data,
        datetime.date,
    ):
        data = data.isoformat()

    if not data:
        return False

    try:
        hora = int(hora)
        qtde = int(qtde)

    except (
        TypeError,
        ValueError,
    ):
        return False

    if not 0 <= hora <= 23:
        return False

    if qtde < 0:
        return False

    registrado_em = (
        datetime.datetime.now()
        .isoformat(
            timespec="seconds"
        )
    )

    with _conectar() as con:
        con.execute(
            """
            INSERT INTO goe_historico (
                data,
                hora,
                qtde,
                registrado_em
            )
            VALUES (?, ?, ?, ?)

            ON CONFLICT(data, hora)
            DO UPDATE SET
                qtde=excluded.qtde,
                registrado_em=excluded.registrado_em
            """,
            (
                data,
                hora,
                qtde,
                registrado_em,
            ),
        )

        con.commit()

    return True


def listar_dia(data=None):
    if data is None:
        data = (
            datetime.date.today()
            .isoformat()
        )

    elif isinstance(
        data,
        datetime.date,
    ):
        data = data.isoformat()

    with _conectar() as con:
        rows = con.execute(
            """
            SELECT
                data,
                hora,
                qtde,
                registrado_em

            FROM goe_historico

            WHERE data=?

            ORDER BY hora
            """,
            (data,),
        ).fetchall()

    return [
        {
            "data": row["data"],
            "hora": row["hora"],
            "qtde": row["qtde"],
            "registrado_em":
                row["registrado_em"],
        }
        for row in rows
    ]


def resumo_dia(data=None):
    linhas = listar_dia(data)

    if not linhas:
        return {
            "total": 0,
            "ultima": None,
            "menor": None,
            "maior": None,
            "horas_registradas": 0,
        }

    ultima = linhas[-1]

    menor = min(
        linhas,
        key=lambda x: x["qtde"],
    )

    maior = max(
        linhas,
        key=lambda x: x["qtde"],
    )

    return {
        "total": sum(
            item["qtde"]
            for item in linhas
        ),
        "ultima": ultima,
        "menor": menor,
        "maior": maior,
        "horas_registradas":
            len(linhas),
    }
