import csv
import datetime
import os
from pathlib import Path

from .history import registrar_leitura


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
            # -------------------------------------------------
            # MODO DE TESTE
            # Permite simular o GOE sem alterar o CSV real.
            # -------------------------------------------------
            arquivo_teste = (
                Path(__file__).resolve().parent
                / ".goe_test_command"
            )

            if arquivo_teste.exists():
                comando = (
                    arquivo_teste
                    .read_text(encoding="utf-8-sig")
                    .strip()
                    .lower()
                )

                try:
                    arquivo_teste.unlink()
                except Exception:
                    pass

                agora = datetime.datetime.now()

                referencia = (
                    agora.replace(
                        minute=0,
                        second=0,
                        microsecond=0
                    )
                    - datetime.timedelta(hours=1)
                )

                status_teste = {
                    "ok": True,
                    "data": referencia.date(),
                    "hora": referencia.hour,
                    "atual": True,
                    "arquivo": "MODO_TESTE",
                }

                if comando == "parado":
                    status_teste["qtde"] = 0

                    print(
                        f"[GOE TESTE] "
                        f"{referencia.hour:02d}h -> PARADO"
                    )

                    self._em_alerta = True
                    self.on_parou(status_teste)

                elif comando == "normal":
                    status_teste["qtde"] = 123456

                    print(
                        f"[GOE TESTE] "
                        f"{referencia.hour:02d}h -> VOLTOU"
                    )

                    self._em_alerta = False
                    self.on_voltou(status_teste)

                elif comando == "ok":
                    status_teste["qtde"] = 123456

                    print(
                        f"[GOE TESTE] "
                        f"{referencia.hour:02d}h -> OK"
                    )

                    if self.on_ok is not None:
                        self.on_ok(status_teste)

                else:
                    print(
                        f"[GOE TESTE] "
                        f"comando desconhecido: {comando}"
                    )

                self._agendar()
                return

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

            # -------------------------------------------------
            # HISTORICO
            # Uma leitura valida deve ser preservada mesmo
            # quando ja nao e mais a ultima hora completa.
            # -------------------------------------------------
            try:
                registrar_leitura(
                    status,
                    exigir_atual=False,
                )

            except Exception as exc:
                print(
                    "[GOE] Erro ao salvar "
                    f"historico: {exc}"
                )

            # Resultado antigo pode entrar no historico,
            # mas nunca deve gerar alerta.
            if not status.get("atual"):
                print(
                    "[GOE] Leitura historica registrada: "
                    f"{status.get('hora', 0):02d}h"
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
