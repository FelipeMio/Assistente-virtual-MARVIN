import datetime
import importlib
import sys

import pytest


@pytest.fixture
def database(
    tmp_path,
    monkeypatch,
):
    """
    Importa marvin.database usando uma HOME
    temporaria.

    Assim nenhum teste acessa ~/.marvin
    real do usuario.
    """

    fake_home = (
        tmp_path
        / "fake_user"
    )

    fake_home.mkdir()

    # Windows.
    monkeypatch.setenv(
        "USERPROFILE",
        str(fake_home),
    )

    # Linux/macOS e fallback.
    monkeypatch.setenv(
        "HOME",
        str(fake_home),
    )

    # Garante import limpo.
    sys.modules.pop(
        "marvin.database",
        None,
    )

    db = importlib.import_module(
        "marvin.database"
    )

    expected_parent = (
        fake_home
        / ".marvin"
    )

    assert (
        db.DB_F.parent
        == expected_parent
    )

    yield db

    db.con.close()

    sys.modules.pop(
        "marvin.database",
        None,
    )


def _create_task(
    db,
    recurrence="Nunca",
    priority="Normal",
):
    date = (
        datetime.date.today()
        + datetime.timedelta(
            days=30
        )
    )

    db.db_criar(
        texto="Tarefa teste",
        descricao="",
        data=date.isoformat(),
        hora="09:30",
        recorrencia=recurrence,
        prioridade=priority,
    )

    rows = db.db_listar()

    assert len(rows) == 1

    return (
        rows[0][0],
        date,
    )


def test_complete_and_reopen_task(
    database
):
    db = database

    tid, _ = _create_task(
        db,
        recurrence="Nunca",
        priority="Alta",
    )

    db.db_concluir(tid)

    task = db.db_listar()[0]

    assert task[6] == 1
    assert task[7] == 1

    history = (
        db.db_historico_conclusoes()
    )

    assert len(history) == 1

    item = history[0]

    assert item[1] == tid
    assert item[2] == "Tarefa teste"
    assert item[3] == "Nunca"
    assert item[4] == "Alta"

    assert db.db_streak_hoje() == 1

    db.db_desconcluir(tid)

    task = db.db_listar()[0]

    assert task[6] == 0

    assert (
        db.db_historico_conclusoes()
        == []
    )

    assert db.db_streak_hoje() == 0


def test_daily_task_advances_date(
    database
):
    db = database

    tid, original = _create_task(
        db,
        recurrence="Todo dia",
    )

    db.db_concluir(tid)

    task = db.db_listar()[0]

    expected = (
        original
        + datetime.timedelta(days=1)
    )

    # Tarefa recorrente continua pendente.
    assert task[6] == 0

    # Deve poder lembrar novamente.
    assert task[7] == 0

    assert task[3] == expected.isoformat()
    assert task[4] == "09:30"

    history = (
        db.db_historico_conclusoes()
    )

    assert len(history) == 1
    assert history[0][1] == tid
    assert history[0][3] == "Todo dia"

    assert db.db_streak_hoje() == 1


@pytest.mark.parametrize(
    "recurrence,allowed",
    [
        (
            "Seg/Qua/Sex",
            {0, 2, 4},
        ),
        (
            "Seg a Sex",
            {0, 1, 2, 3, 4},
        ),
        (
            "Fins de semana",
            {5, 6},
        ),
    ],
)
def test_recurring_weekdays(
    database,
    recurrence,
    allowed,
):
    db = database

    original = (
        datetime.date.today()
        + datetime.timedelta(
            days=30
        )
    )

    result = (
        db._proxima_data_recorrente(
            original.isoformat(),
            recurrence,
            original.isoformat(),
        )
    )

    assert result is not None
    assert result > original
    assert result.weekday() in allowed
