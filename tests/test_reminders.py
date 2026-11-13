import datetime

import pytest

from marvin.reminders import ReminderQueue, ReminderService


# Datas de referencia (novembro de 2026)
SEX = datetime.date(2026, 11, 13)
SAB = datetime.date(2026, 11, 14)
DOM = datetime.date(2026, 11, 15)
SEG = datetime.date(2026, 11, 16)


def em(data, hora, minuto=0, segundo=0):
    return datetime.datetime.combine(
        data,
        datetime.time(hora, minuto, segundo),
    )


def tarefa(data, hora="10:00", rep="Nunca", lembrado=0):
    # (id, texto, descricao, data, hora, recorrencia, concluida, lembrado)
    return (1, "Tarefa", "", data.isoformat(), hora, rep, 0, lembrado)


due = ReminderService.is_due


# ============================================================
# TAREFAS COMUNS
# ============================================================

class TestTarefaComum:

    def test_antes_do_horario_nao_lembra(self):
        assert not due(tarefa(SEX), em(SEX, 9, 59))

    def test_no_horario_lembra(self):
        assert due(tarefa(SEX), em(SEX, 10, 0))

    def test_continua_lembrando_ate_concluir_ou_adiar(self):
        # Ex.: o computador ficou bloqueado a manha toda.
        assert due(tarefa(SEX), em(SEX, 15, 0))

    def test_vencida_ontem_continua_pendente(self):
        assert due(tarefa(SEX), em(SAB, 8, 0))

    def test_data_futura_nao_lembra(self):
        assert not due(tarefa(SAB), em(SEX, 23, 0))

    def test_flag_lembrado_nao_esconde_tarefa_comum(self):
        # Se o MARVIN foi fechado com o alerta aberto,
        # o lembrete precisa voltar na proxima execucao.
        assert due(tarefa(SEX, lembrado=1), em(SEX, 11, 0))


# ============================================================
# TAREFAS RECORRENTES
# ============================================================

class TestRecorrente:

    def test_todo_dia_lembra_na_janela_de_90_segundos(self):
        assert due(tarefa(SEX, rep="Todo dia"), em(SEX, 10, 0, 30))

    def test_todo_dia_nao_lembra_depois_da_janela(self):
        assert not due(tarefa(SEX, rep="Todo dia"), em(SEX, 10, 2))

    def test_flag_lembrado_evita_repetir_a_mesma_ocorrencia(self):
        assert not due(
            tarefa(SEX, rep="Todo dia", lembrado=1),
            em(SEX, 10, 0, 10),
        )

    def test_toda_semana_lembra_no_mesmo_dia_da_semana(self):
        assert due(tarefa(SEX, rep="Toda semana"), em(SEX, 10, 0))

    def test_toda_semana_espera_a_proxima_data(self):
        proxima = SEX + datetime.timedelta(days=7)
        assert not due(tarefa(proxima, rep="Toda semana"), em(SEX, 10, 0))

    @pytest.mark.parametrize(
        "rep, dia, esperado",
        [
            ("Seg a Sex", SEG, True),
            ("Seg a Sex", SAB, False),
            ("Seg/Qua/Sex", SEX, True),
            ("Seg/Qua/Sex", SEG + datetime.timedelta(days=1), False),
            ("Fins de semana", DOM, True),
            ("Fins de semana", SEG, False),
        ],
    )
    def test_dias_permitidos(self, rep, dia, esperado):
        assert due(tarefa(SEX, rep=rep), em(dia, 10, 0)) is esperado

    def test_recorrencia_desconhecida_nao_lembra(self):
        assert not due(tarefa(SEX, rep="A cada lua cheia"), em(SEX, 10, 0))


# ============================================================
# DADOS INVALIDOS
# ============================================================

@pytest.mark.parametrize(
    "row",
    [
        (1, "curta demais"),
        (1, "T", "", "2026-13-40", "10:00", "Nunca", 0, 0),
        (1, "T", "", "2026-11-13", "25:99", "Nunca", 0, 0),
        (1, "T", "", None, "10:00", "Nunca", 0, 0),
        (1, "T", "", "2026-11-13", None, "Nunca", 0, 0),
    ],
)
def test_linha_invalida_nao_quebra_o_servico(row):
    assert due(row, em(SEX, 12, 0)) is False


# ============================================================
# FILA
# ============================================================

def test_fila_de_lembretes():
    fila = ReminderQueue()

    assert not fila
    assert fila.peek() is None
    assert fila.pop_current() is None

    a = tarefa(SEX)
    b = (2,) + tarefa(SEX)[1:]

    fila.append(a)
    fila.append(b)

    assert len(fila) == 2
    assert fila.contains_task_id(2)
    assert not fila.contains_task_id(3)
    assert fila.peek() is a
    assert fila.pop_current() is a
    assert list(fila) == [b]

    fila.clear()
    assert not fila
