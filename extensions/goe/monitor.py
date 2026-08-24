import csv
import datetime
import os
from pathlib import Path


def caminho_csv_goe():
    personalizado = os.getenv(
        "MARVIN_GOE_CSV"
    )

    if personalizado:
        return Path(personalizado)

    return (
        Path.home()
        / "Desktop"
        / "MARVIN_GOE_MONITOR.csv"
    )


def _converter_data(valor):
    valor = str(valor).strip()

    for formato in (
        "%d/%m/%Y",
        "%Y-%m-%d",
    ):
        try:
            return datetime.datetime.strptime(
                valor,
                formato
            ).date()

        except ValueError:
            continue

    raise ValueError(
        f"Data invalida no CSV: {valor}"
    )


def ler_status_goe(arquivo=None):
    arquivo = Path(
        arquivo or caminho_csv_goe()
    )

    if not arquivo.exists():
        return {
            "ok": False,
            "motivo": "arquivo_nao_encontrado",
            "arquivo": str(arquivo),
        }

    with arquivo.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:
        leitor = csv.DictReader(f)
        linhas = list(leitor)

    if not linhas:
        return {
            "ok": False,
            "motivo": "csv_vazio",
            "arquivo": str(arquivo),
        }

    linha = linhas[-1]

    try:
        data = _converter_data(
            linha["DTREFERENCIA"]
        )

        hora = int(
            str(linha["HH"]).strip()
        )

        qtde_txt = str(
            linha["QTDE"]
        ).strip()

        qtde_txt = (
            qtde_txt
            .replace(".", "")
            .replace(",", "")
        )

        qtde = int(qtde_txt)

    except (
        KeyError,
        TypeError,
        ValueError
    ) as exc:
        return {
            "ok": False,
            "motivo": "csv_invalido",
            "erro": str(exc),
            "arquivo": str(arquivo),
        }

    agora = datetime.datetime.now()

    hora_esperada = (
        agora.replace(
            minute=0,
            second=0,
            microsecond=0
        )
        - datetime.timedelta(hours=1)
    )

    hora_csv = datetime.datetime.combine(
        data,
        datetime.time(hour=hora)
    )

    return {
        "ok": True,
        "data": data,
        "hora": hora,
        "qtde": qtde,
        "atual": hora_csv == hora_esperada,
        "arquivo": str(arquivo),
    }


class GOEMonitor:

    def __init__(
        self,
        root,
        on_parou,
        on_voltou,
        on_ok=None,
        arquivo=None,
        intervalo_ms=30000,
    ):
        self.root = root

        self.on_parou = on_parou
        self.on_voltou = on_voltou
        self.on_ok = on_ok

        self.arquivo = Path(
            arquivo or caminho_csv_goe()
        )

        self.intervalo_ms = intervalo_ms

        self._ultimo_mtime = None
        self._em_alerta = False
        self._ativo = True


    @property
    def em_alerta(self):
        return self._em_alerta


    def start(self):
        self.root.after(
            1500,
            self._tick
        )


    def stop(self):
        self._ativo = False


    def _agendar(self):
        if not self._ativo:
            return

        try:
            self.root.after(
                self.intervalo_ms,
                self._tick
            )

        except Exception:
            pass


    def _tick(self):
        if not self._ativo:
            return

        try:
            if not self.arquivo.exists():
                self._agendar()
                return

            mtime = (
                self.arquivo
                .stat()
                .st_mtime_ns
            )

            # O Navicat ainda nao gerou
            # um novo resultado.
            if mtime == self._ultimo_mtime:
                self._agendar()
                return

            self._ultimo_mtime = mtime

            status = ler_status_goe(
                self.arquivo
            )

            if not status.get("ok"):
                print(
                    "[GOE] CSV invalido:",
                    status
                )

                self._agendar()
                return

            # Nao usa resultado antigo para gerar alerta.
            if not status.get("atual"):
                print(
                    "[GOE] CSV ainda nao corresponde "
                    "a ultima hora completa:",
                    status.get("hora")
                )

                self._agendar()
                return

            qtde = status["qtde"]

            print(
                f"[GOE] {status['hora']:02d}h "
                f"-> {qtde} registros"
            )

            # -----------------------------------------
            # GOE PARADO
            # -----------------------------------------
            if qtde == 0:

                if not self._em_alerta:
                    self._em_alerta = True

                    self.on_parou(
                        status
                    )

            # -----------------------------------------
            # GOE FUNCIONANDO
            # -----------------------------------------
            else:

                if self._em_alerta:
                    self._em_alerta = False

                    self.on_voltou(
                        status
                    )

                elif self.on_ok is not None:
                    # Um novo CSV valido foi gerado e
                    # o GOE continua normal.
                    self.on_ok(
                        status
                    )

        except Exception as exc:
            print(
                f"[GOE] Erro no monitor: {exc}"
            )

        self._agendar()
