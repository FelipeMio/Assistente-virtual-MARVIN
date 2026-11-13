import datetime
import importlib
import sys

import pytest


SEX = datetime.date(2026, 11, 13)
SAB = datetime.date(2026, 11, 14)
DOM = datetime.date(2026, 11, 15)
SEG = datetime.date(2026, 11, 16)
QUA = datetime.date(2026, 11, 18)


@pytest.fixture
def proxima(tmp_path, monkeypatch):
    """_proxima_data_recorrente com uma HOME temporaria."""
    fake_home = tmp_path / "fake_user"
    fake_home.mkdir()

    monkeypatch.setenv("USERPROFILE", str(fake_home))
    monkeypatch.setenv("HOME", str(fake_home))

    sys.modules.pop("marvin.database", None)
    db = importlib.import_module("marvin.database")

    yield db._proxima_data_recorrente

    db.con.close()
    sys.modules.pop("marvin.database", None)


def iso(data):
    return data.isoformat()


def test_todo_dia_vai_para_amanha(proxima):
    assert proxima(iso(SEX), "Todo dia", hoje=SEX) == SAB


def test_todo_dia_atrasada_parte_de_hoje(proxima):
    # Concluida com 3 dias de atraso: nao gera ocorrencias no passado.
    tres_dias_atras = SEX - datetime.timedelta(days=3)
    assert proxima(iso(tres_dias_atras), "Todo dia", hoje=SEX) == SAB


def test_toda_semana_mesmo_dia_da_semana(proxima):
    assert proxima(iso(SEX), "Toda semana", iso(SEX), hoje=SEX) == SEX + datetime.timedelta(days=7)


def test_toda_semana_adiada_volta_para_o_dia_original(proxima):
    # A ocorrencia de sexta foi adiada para sabado;
    # a proxima continua sendo na sexta seguinte.
    assert proxima(iso(SAB), "Toda semana", iso(SEX), hoje=SAB) == SEX + datetime.timedelta(days=7)


def test_seg_a_sex_pula_o_fim_de_semana(proxima):
    assert proxima(iso(SEX), "Seg a Sex", hoje=SEX) == SEG


def test_seg_qua_sex(proxima):
    assert proxima(iso(SEG), "Seg/Qua/Sex", hoje=SEG) == QUA
    assert proxima(iso(SEX), "Seg/Qua/Sex", hoje=SEX) == SEG


def test_fins_de_semana(proxima):
    assert proxima(iso(SAB), "Fins de semana", hoje=SAB) == DOM
    assert proxima(iso(DOM), "Fins de semana", hoje=DOM) == SAB + datetime.timedelta(days=7)


def test_data_invalida_parte_de_hoje(proxima):
    assert proxima("nao-e-data", "Todo dia", hoje=SEX) == SAB


def test_recorrencia_desconhecida(proxima):
    assert proxima(iso(SEX), "A cada lua cheia", hoje=SEX) is None
