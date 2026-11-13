import datetime

from marvin.away import (
    AwayTracker,
    descrever_duracao,
    montar_resumo,
)


SEX = datetime.date(2026, 11, 13)


def em(hora, minuto=0, dia=SEX):
    return datetime.datetime.combine(dia, datetime.time(hora, minuto))


# ============================================================
# DETECCAO
# ============================================================

def test_uso_normal_nao_gera_resumo():
    t = AwayTracker(limite_segundos=600)

    for minuto in range(0, 30, 1):
        assert t.atualizar(5, em(9, minuto)) is None

    assert not t.ausente


def test_ausencia_longa_gera_resumo_na_volta():
    t = AwayTracker(limite_segundos=600)

    # Ultima tecla as 8:00; leituras enquanto o PC esta parado.
    assert t.atualizar(11 * 60, em(8, 11)) is None
    assert t.ausente
    assert t.atualizar(60 * 60, em(9, 0)) is None

    # Voltou as 9:40 (leitura as 9:40:20, 20 s depois da volta).
    volta = t.atualizar(20, em(9, 40) + datetime.timedelta(seconds=20))

    assert volta == (em(8, 0), em(9, 40))
    assert not t.ausente


def test_ausencia_curta_nao_conta():
    t = AwayTracker(limite_segundos=600)

    assert t.atualizar(5 * 60, em(10, 5)) is None
    assert t.atualizar(3, em(10, 6)) is None
    assert not t.ausente


def test_resumo_so_dispara_uma_vez():
    t = AwayTracker(limite_segundos=600)

    t.atualizar(900, em(12, 15))
    assert t.atualizar(1, em(13, 0)) is not None
    assert t.atualizar(1, em(13, 1)) is None


# ============================================================
# RESUMO
# ============================================================

def tarefa(tid, titulo, data, hora, rep="Nunca"):
    return (tid, titulo, "", data.isoformat(), hora, rep, 0, 0)


def aviso(origem, momento):
    return {
        "origem": origem,
        "criada_em": momento.astimezone().isoformat(timespec="seconds"),
    }


def test_conta_avisos_por_origem_dentro_do_periodo():
    notificacoes = [
        aviso("B2B", em(8, 30)),
        aviso("B2B", em(9, 10)),
        aviso("GOE", em(9, 5)),
        aviso("B2B", em(7, 50)),   # antes de sair
        aviso("B2B", em(10, 30)),  # depois de voltar
    ]

    r = montar_resumo(em(8, 0), em(9, 40), notificacoes=notificacoes)

    assert r.avisos == {"B2B": 2, "GOE": 1}
    assert r.total_avisos == 3


def test_lembretes_que_venceram_durante_a_ausencia():
    tarefas = [
        tarefa(1, "Daily", SEX, "09:00", "Seg a Sex"),
        tarefa(2, "Enviar relatório", SEX, "08:30"),
        tarefa(3, "Almoço", SEX, "12:00"),
        tarefa(4, "Conferir e-mails", SEX, "07:00"),
    ]

    r = montar_resumo(
        em(8, 0),
        em(9, 40),
        tarefas_pendentes=tarefas,
    )

    assert r.lembretes == ["Daily", "Enviar relatório"]

    # Tarefas comuns vencidas e abertas (inclui a das 7h).
    assert r.atrasadas == 2

    assert r.proxima == ("Almoço", em(12, 0))


def test_recorrente_fora_do_dia_permitido_nao_aparece():
    sabado = SEX + datetime.timedelta(days=1)
    tarefas = [tarefa(1, "Daily", SEX, "09:00", "Seg a Sex")]

    r = montar_resumo(
        em(8, 0, sabado),
        em(10, 0, sabado),
        tarefas_pendentes=tarefas,
    )

    assert r.lembretes == []


def test_resumo_vazio():
    r = montar_resumo(em(8, 0), em(8, 30))

    assert r.vazio
    assert r.proxima is None


def test_checklist_pendente_conta_como_novidade():
    r = montar_resumo(em(8, 0), em(8, 30), checklist_pendentes=3)

    assert not r.vazio
    assert r.checklist_pendentes == 3


def test_descrever_duracao():
    assert descrever_duracao(datetime.timedelta(minutes=45)) == "45 min"
    assert descrever_duracao(datetime.timedelta(hours=2)) == "2 h"
    assert descrever_duracao(datetime.timedelta(hours=1, minutes=35)) == "1 h 35 min"
