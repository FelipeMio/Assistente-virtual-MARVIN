"""
"Enquanto voce estava fora": percebe a ausencia do usuario e
monta um resumo do que aconteceu nesse periodo.

A deteccao usa o tempo desde a ultima tecla/movimento do mouse
(GetLastInputInfo), que tambem cobre a tela bloqueada.
"""

import datetime
import logging
import sys
import tkinter as tk
from collections import Counter
from dataclasses import dataclass, field

from .reminders import ReminderService


logger = logging.getLogger(
    "marvin.away"
)


# ============================================================
# TEMPO OCIOSO DO WINDOWS
# ============================================================

def idle_seconds():
    """Segundos desde a ultima entrada de teclado/mouse."""
    if sys.platform != "win32":
        return 0.0

    try:
        import ctypes
        from ctypes import wintypes

        class LASTINPUTINFO(ctypes.Structure):
            _fields_ = [
                ("cbSize", wintypes.UINT),
                ("dwTime", wintypes.DWORD),
            ]

        info = LASTINPUTINFO()
        info.cbSize = ctypes.sizeof(LASTINPUTINFO)

        if not ctypes.windll.user32.GetLastInputInfo(ctypes.byref(info)):
            return 0.0

        agora = ctypes.windll.kernel32.GetTickCount()

        # GetTickCount volta a zero a cada ~49 dias.
        return ((agora - info.dwTime) & 0xFFFFFFFF) / 1000.0

    except Exception:
        return 0.0


# ============================================================
# ESTADO DA AUSENCIA (logica pura, testavel)
# ============================================================

class AwayTracker:
    """
    Recebe leituras periodicas do tempo ocioso e avisa
    quando o usuario volta depois de uma ausencia longa.
    """

    def __init__(self, limite_segundos=600):
        self.limite = float(limite_segundos)
        self.ausente_desde = None

    @property
    def ausente(self):
        return self.ausente_desde is not None

    def atualizar(self, ocioso, agora):
        """
        Devolve (inicio, fim) no momento em que o usuario
        volta; None em qualquer outra leitura.
        """
        if ocioso >= self.limite:
            if self.ausente_desde is None:
                self.ausente_desde = agora - datetime.timedelta(seconds=ocioso)
            return None

        if self.ausente_desde is None:
            return None

        inicio = self.ausente_desde
        self.ausente_desde = None

        # A volta aconteceu ha `ocioso` segundos.
        fim = agora - datetime.timedelta(seconds=ocioso)

        return inicio, fim


class AwayMonitor:
    """Consulta o tempo ocioso periodicamente na thread do Tk."""

    def __init__(
        self,
        root,
        *,
        on_return,
        enabled=lambda: True,
        limite_segundos=600,
        poll_ms=10_000,
        idle_fn=idle_seconds,
        clock=datetime.datetime.now,
    ):
        self.root = root
        self._on_return = on_return
        self._enabled = enabled
        self._idle_fn = idle_fn
        self._clock = clock

        self.tracker = AwayTracker(limite_segundos)
        self.poll_ms = int(poll_ms)

        self._job = None
        self._parado = True

    def start(self):
        self._parado = False
        self._agendar()

    def stop(self):
        self._parado = True

        if self._job is not None:
            try:
                self.root.after_cancel(self._job)
            except Exception:
                pass

            self._job = None

    def _agendar(self):
        if self._parado:
            return

        try:
            self._job = self.root.after(self.poll_ms, self._verificar)
        except tk.TclError:
            self._job = None

    def _verificar(self):
        self._job = None

        try:
            volta = self.tracker.atualizar(
                self._idle_fn(),
                self._clock(),
            )

            if volta and self._enabled():
                inicio, fim = volta

                logger.info(
                    "Usuario voltou (ausente de %s a %s).",
                    inicio.strftime("%H:%M"),
                    fim.strftime("%H:%M"),
                )

                self._on_return(inicio, fim)

        except Exception:
            logger.exception("Erro ao verificar ausencia.")

        self._agendar()


# ============================================================
# RESUMO
# ============================================================

@dataclass
class ResumoAusencia:
    inicio: datetime.datetime
    fim: datetime.datetime

    # origem -> quantidade (ex.: {"B2B": 12})
    avisos: dict = field(default_factory=dict)

    # titulos das tarefas cujo horario passou durante a ausencia
    lembretes: list = field(default_factory=list)

    # tarefas comuns vencidas e ainda abertas (total)
    atrasadas: int = 0

    checklist_pendentes: int = 0

    # (titulo, datetime) da proxima tarefa, se houver
    proxima: tuple = None

    @property
    def duracao(self):
        return self.fim - self.inicio

    @property
    def total_avisos(self):
        return sum(self.avisos.values())

    @property
    def vazio(self):
        return not (
            self.avisos
            or self.lembretes
            or self.atrasadas
            or self.checklist_pendentes
        )


def _quando_tarefa(row, dia):
    """datetime da ocorrencia da tarefa em `dia` (ou None)."""
    try:
        _, _, _, data, hora, rep, _, _ = row
        hora_obj = datetime.datetime.strptime(hora[:5], "%H:%M").time()
        data_obj = datetime.date.fromisoformat(data)

    except Exception:
        return None

    if rep == "Nunca":
        return datetime.datetime.combine(data_obj, hora_obj)

    if dia < data_obj:
        return None

    if not ReminderService.should_remind(
        rep,
        data,
        datetime.datetime.combine(dia, hora_obj),
        dia.isoformat(),
    ):
        return None

    return datetime.datetime.combine(dia, hora_obj)


def _datahora_notificacao(item):
    try:
        momento = datetime.datetime.fromisoformat(item.get("criada_em", ""))
    except (TypeError, ValueError):
        return None

    # Notificacoes sao salvas com fuso; comparamos em hora local.
    if momento.tzinfo is not None:
        momento = momento.astimezone().replace(tzinfo=None)

    return momento


def montar_resumo(
    inicio,
    fim,
    *,
    agora=None,
    notificacoes=(),
    tarefas_pendentes=(),
    checklist_pendentes=0,
):
    """Junta tudo o que aconteceu entre `inicio` e `fim`."""
    agora = agora or fim

    resumo = ResumoAusencia(inicio=inicio, fim=fim)

    # Avisos recebidos (B2B, GOE...) no periodo
    origens = Counter()

    for item in notificacoes:
        momento = _datahora_notificacao(item)

        if momento is not None and inicio <= momento <= fim:
            origens[item.get("origem") or "Avisos"] += 1

    resumo.avisos = dict(origens)

    # Lembretes que venceram durante a ausencia
    dias = {inicio.date(), fim.date()}
    proximas = []

    for row in tarefas_pendentes:
        titulo = row[1]
        rep = row[5]

        for dia in sorted(dias):
            quando = _quando_tarefa(row, dia)

            if quando is not None and inicio <= quando <= fim:
                resumo.lembretes.append(titulo)
                break

        quando_hoje = _quando_tarefa(row, agora.date())

        # So tarefas comuns ficam "atrasadas": as recorrentes
        # apenas avancam para a proxima ocorrencia.
        if (
            rep == "Nunca"
            and quando_hoje is not None
            and quando_hoje <= agora
        ):
            resumo.atrasadas += 1

        if quando_hoje is not None and quando_hoje > agora:
            proximas.append((quando_hoje, titulo))

    if proximas:
        quando, titulo = min(proximas)
        resumo.proxima = (titulo, quando)

    resumo.checklist_pendentes = int(checklist_pendentes or 0)

    return resumo


def descrever_duracao(delta):
    minutos = int(delta.total_seconds() // 60)
    horas, minutos = divmod(minutos, 60)

    if horas and minutos:
        return f"{horas} h {minutos} min"

    if horas:
        return f"{horas} h"

    return f"{minutos} min"
