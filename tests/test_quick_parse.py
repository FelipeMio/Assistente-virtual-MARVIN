import datetime

import pytest

from marvin.quick_parse import descrever_data, interpretar


# Sexta-feira, 13/11/2026, 13:22
AGORA = datetime.datetime(2026, 11, 13, 13, 22)
HOJE = AGORA.date()


def d(dia, mes=11, ano=2026):
    return datetime.date(ano, mes, dia)


@pytest.mark.parametrize(
    "texto, titulo, data, hora",
    [
        ("reunião com o time amanhã 15h", "Reunião com o time", d(14), "15:00"),
        ("ligar pro João na sexta às 9h30", "Ligar pro João", d(20), "09:30"),
        ("pagar boleto dia 20", "Pagar boleto", d(20), "09:00"),
        ("enviar relatório 20/12 às 10", "Enviar relatório", d(20, 12), "10:00"),
        ("consulta 05/01/2027 8h", "Consulta", d(5, 1, 2027), "08:00"),
        ("revisar PR em 2 horas", "Revisar PR", d(13), "15:22"),
        ("tomar remédio daqui a 30 minutos", "Tomar remédio", d(13), "13:52"),
        ("renovar contrato em 3 dias", "Renovar contrato", d(16), "09:00"),
        ("almoço com a Ana meio-dia", "Almoço com a Ana", d(14), "12:00"),
        ("academia amanhã de manhã", "Academia", d(14), "09:00"),
        ("ligar para a mãe 8 da noite", "Ligar para a mãe", d(13), "20:00"),
        ("estudar hoje à tarde 3h", "Estudar", d(13), "15:00"),
        ("happy hour depois de amanhã 18h", "Happy hour", d(15), "18:00"),
        ("planejamento próxima segunda 10h", "Planejamento", d(16), "10:00"),
        ("deploy terça-feira 14:00", "Deploy", d(17), "14:00"),
    ],
)
def test_datas_e_horarios(texto, titulo, data, hora):
    r = interpretar(texto, AGORA)

    assert r.valida, r.erro
    assert r.titulo == titulo
    assert r.data == data
    assert r.hora == hora


def test_sem_data_nem_hora_vai_para_proxima_hora_cheia():
    r = interpretar("comprar pão", AGORA)

    assert r.titulo == "Comprar pão"
    assert (r.data, r.hora) == (HOJE, "14:00")
    assert "data" not in r.detectado
    assert "hora" not in r.detectado


def test_hora_que_ja_passou_vai_para_amanha():
    r = interpretar("conferir e-mails 8h", AGORA)

    assert (r.data, r.hora) == (d(14), "08:00")


def test_hoje_com_hora_passada_e_erro():
    r = interpretar("reunião hoje 8h", AGORA)

    assert not r.valida
    assert "passou" in r.erro


def test_sexta_numa_sexta_depois_do_horario_vai_para_semana_seguinte():
    r = interpretar("call sexta 9h", AGORA)

    assert r.data == d(20)


def test_sexta_numa_sexta_antes_do_horario_e_hoje():
    r = interpretar("call sexta 16h", AGORA)

    assert r.data == HOJE


@pytest.mark.parametrize(
    "texto, recorrencia, titulo",
    [
        ("beber água todo dia 10h", "Todo dia", "Beber água"),
        ("tomar vitamina todos os dias", "Todo dia", "Tomar vitamina"),
        ("daily de segunda a sexta 9h", "Seg a Sex", "Daily"),
        ("ponto dias úteis 8h", "Seg a Sex", "Ponto"),
        ("treino seg, qua e sex 7h", "Seg/Qua/Sex", "Treino"),
        ("faxina fins de semana", "Fins de semana", "Faxina"),
        ("relatório semanal toda semana", "Toda semana", "Relatório semanal"),
    ],
)
def test_recorrencia(texto, recorrencia, titulo):
    r = interpretar(texto, AGORA)

    assert r.valida, r.erro
    assert r.recorrencia == recorrencia
    assert r.titulo == titulo


def test_toda_segunda_vira_semanal_comecando_na_proxima_segunda():
    r = interpretar("reunião 1:1 toda segunda 11h", AGORA)

    assert r.recorrencia == "Toda semana"
    assert r.data == d(16)
    assert r.hora == "11:00"
    assert r.titulo == "Reunião 1:1"


def test_todo_dia_10h_nao_confunde_com_dia_10():
    r = interpretar("beber água todo dia 10h", AGORA)

    assert r.data == d(14)
    assert r.hora == "10:00"


@pytest.mark.parametrize(
    "texto, prioridade",
    [
        ("pagar boleto prioridade alta", "Alta"),
        ("pagar boleto prioridade média", "Normal"),
        ("pagar boleto prioridade baixa", "Baixa"),
        ("pagar boleto urgente", "Alta"),
        ("pagar boleto", "Nenhuma"),
    ],
)
def test_prioridade(texto, prioridade):
    r = interpretar(texto, AGORA)

    assert r.prioridade == prioridade
    assert r.titulo == "Pagar boleto"


def test_titulo_vazio_e_erro():
    r = interpretar("amanhã 15h", AGORA)

    assert not r.valida
    assert r.erro == "Escreva o que precisa ser feito."


def test_dia_inexistente_e_erro():
    r = interpretar("pagar conta dia 31", AGORA)

    # Novembro passou do dia 13, entao "dia 31" seria em... novembro? nao:
    # 31 >= 13, mesmo mes, e novembro nao tem 31.
    assert not r.valida
    assert "31" in r.erro


def test_dia_ja_passado_vai_para_o_mes_seguinte():
    r = interpretar("pagar aluguel dia 5", AGORA)

    assert r.data == d(5, 12)


def test_data_sem_ano_ja_passada_vai_para_o_ano_seguinte():
    r = interpretar("aniversário 10/01", AGORA)

    assert r.data == d(10, 1, 2027)


def test_numeros_no_titulo_sao_preservados():
    r = interpretar("comprar 2 pães e 3 litros de leite amanhã", AGORA)

    assert r.titulo == "Comprar 2 pães e 3 litros de leite"


def test_descrever_data():
    assert descrever_data(HOJE, HOJE) == "Hoje"
    assert descrever_data(d(14), HOJE) == "Amanhã"
    assert descrever_data(d(17), HOJE) == "Terça, 17/11"
    assert descrever_data(d(5, 1, 2027), HOJE) == "Terça, 05/01/2027"
