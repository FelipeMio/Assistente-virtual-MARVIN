"""
Interpreta frases em portugues para criar tarefas rapidamente.

Exemplos:
    "reuniao com o time amanha 15h"
    "pagar boleto dia 20 prioridade alta"
    "beber agua todo dia 10h"
    "ligar pro Joao na sexta as 9h30"
    "revisar relatorio em 2 horas"

Tudo roda localmente, sem internet. A funcao principal e
`interpretar(texto, agora)`, que devolve um `TarefaRapida`.
"""

import calendar
import datetime
import re
import unicodedata
from dataclasses import dataclass, field


# ============================================================
# RESULTADO
# ============================================================

@dataclass
class TarefaRapida:
    titulo: str = ""
    data: datetime.date = None
    hora: str = ""
    recorrencia: str = "Nunca"
    prioridade: str = "Nenhuma"
    erro: str = ""

    # Campos que vieram do texto (e nao de um valor padrao).
    detectado: set = field(default_factory=set)

    @property
    def valida(self):
        return not self.erro

    @property
    def data_iso(self):
        return self.data.isoformat() if self.data else ""


# ============================================================
# VOCABULARIO
# ============================================================

DIAS_SEMANA = {
    "segunda": 0,
    "terca": 1,
    "quarta": 2,
    "quinta": 3,
    "sexta": 4,
    "sabado": 5,
    "domingo": 6,
}

_DIA = r"(segunda|terca|quarta|quinta|sexta|sabado|domingo)(?:[- ]feira)?s?"

NUMEROS = {
    "um": 1,
    "uma": 1,
    "dois": 2,
    "duas": 2,
    "tres": 3,
    "quatro": 4,
    "cinco": 5,
    "seis": 6,
    "dez": 10,
    "quinze": 15,
    "vinte": 20,
    "trinta": 30,
}

_NUM = r"(\d+|um|uma|dois|duas|tres|quatro|cinco|seis|dez|quinze|vinte|trinta|meia)"

PERIODOS = {
    "manha": 9,
    "tarde": 14,
    "noite": 19,
}

# Palavras que sobram soltas no titulo depois de tirar datas e horas.
_CONECTORES = {
    "a", "as", "ao", "de", "do", "da", "dos", "das", "para", "pra",
    "pro", "no", "na", "nos", "nas", "em", "e", "dia", "pelas",
    "pelo", "ate", "proximo", "proxima", "que", "vem", "com",
}


def _normalizar(texto):
    """Minusculas e sem acento, mantendo o mesmo tamanho do texto."""
    saida = []

    for ch in texto:
        base = unicodedata.normalize("NFD", ch.lower())[:1] or " "
        saida.append(base)

    return "".join(saida)


def _numero(valor):
    if valor.isdigit():
        return int(valor)

    if valor == "meia":
        return 0.5

    return NUMEROS.get(valor)


def _proxima_hora_cheia(agora):
    base = agora.replace(minute=0, second=0, microsecond=0)
    return base + datetime.timedelta(hours=1)


# ============================================================
# INTERPRETADOR
# ============================================================

class _Leitor:
    """Procura padroes e vai 'apagando' o que ja foi entendido."""

    def __init__(self, texto):
        self.original = texto
        self.norm = _normalizar(texto)
        self.usado = [False] * len(texto)

    def procurar(self, padrao):
        """Primeiro trecho ainda nao usado que casa com o padrao."""
        for m in re.finditer(padrao, self.norm):
            if not any(self.usado[m.start():m.end()]):
                self._marcar(m.start(), m.end())
                return m

        return None

    def _marcar(self, inicio, fim):
        for i in range(inicio, fim):
            self.usado[i] = True

    def resto(self):
        return "".join(
            " " if usado else ch
            for ch, usado in zip(self.original, self.usado)
        )


def _limpar_titulo(texto):
    texto = re.sub(r"\s+", " ", texto).strip(" ,;.-–")

    palavras = texto.split(" ")

    def conector(palavra):
        return _normalizar(palavra).strip(",;.") in _CONECTORES

    while palavras and conector(palavras[-1]):
        palavras.pop()

    while palavras and conector(palavras[0]):
        palavras.pop(0)

    texto = " ".join(palavras).strip(" ,;.-–")

    # Remove conectores duplicados que sobraram no meio
    # (ex.: "ligar pro Joao na  as" -> ja tratado nas pontas).
    texto = re.sub(r"\s+", " ", texto)

    if texto:
        texto = texto[0].upper() + texto[1:]

    return texto


def interpretar(texto, agora=None):
    agora = agora or datetime.datetime.now()
    agora = agora.replace(second=0, microsecond=0)
    hoje = agora.date()

    r = TarefaRapida()
    leitor = _Leitor(texto or "")

    data = None
    hora = None          # (h, m)
    periodo = None
    momento = None       # datetime vindo de "em 2 horas"
    dia_semana = None
    hoje_explicito = False

    # --------------------------------------------------------
    # Prioridade
    # --------------------------------------------------------
    m = leitor.procurar(
        r"\b(?:prioridade|prio)\s+(alta|media|normal|baixa|nenhuma)\b"
    )

    if m:
        r.prioridade = {
            "alta": "Alta",
            "media": "Normal",
            "normal": "Normal",
            "baixa": "Baixa",
            "nenhuma": "Nenhuma",
        }[m.group(1)]
        r.detectado.add("prioridade")

    elif leitor.procurar(r"\b(urgente|importante)\b"):
        r.prioridade = "Alta"
        r.detectado.add("prioridade")

    # --------------------------------------------------------
    # Repeticao
    # --------------------------------------------------------
    regras = [
        (r"\b(?:de\s+)?seg(?:unda)?(?:[- ]feira)?\s+(?:a|ate)\s+sex(?:ta)?(?:[- ]feira)?\b", "Seg a Sex"),
        (r"\b(?:todos\s+os\s+|nos\s+|em\s+)?dias?\s+uteis\b", "Seg a Sex"),
        (r"\bseg(?:unda)?\s*[,/]\s*qua(?:rta)?\s*(?:[,/]|\s+e)\s*sex(?:ta)?\b", "Seg/Qua/Sex"),
        (r"\b(?:todo\s+|todos\s+os\s+|nos\s+|aos\s+)?fins?\s+de\s+semana\b", "Fins de semana"),
        (r"\b(?:todos\s+os\s+dias|todo\s+dia|diariamente)\b", "Todo dia"),
        (r"\b(?:toda\s+semana|todas\s+as\s+semanas|semanalmente)\b", "Toda semana"),
    ]

    for padrao, valor in regras:
        if leitor.procurar(padrao):
            r.recorrencia = valor
            r.detectado.add("recorrencia")
            break

    if "recorrencia" not in r.detectado:
        m = leitor.procurar(r"\b(?:toda|todo|todas\s+as|todos\s+os)\s+" + _DIA + r"\b")

        if m:
            r.recorrencia = "Toda semana"
            r.detectado.add("recorrencia")
            dia_semana = DIAS_SEMANA[m.group(1)]

    # --------------------------------------------------------
    # Tempo relativo: "em 2 horas", "daqui a 30 min", "em 3 dias"
    # --------------------------------------------------------
    m = leitor.procurar(
        r"\b(?:em|daqui\s+a|daqui|dentro\s+de)\s+" + _NUM
        + r"\s*(minutos?|mins?|m|horas?|hrs?|h|dias?|semanas?)\b"
    )

    if m:
        qtd = _numero(m.group(1))
        unidade = m.group(2)

        if unidade.startswith("m"):
            momento = agora + datetime.timedelta(minutes=qtd)
        elif unidade.startswith("h"):
            momento = agora + datetime.timedelta(hours=qtd)
        elif unidade.startswith("d"):
            data = hoje + datetime.timedelta(days=int(qtd))
        else:
            data = hoje + datetime.timedelta(weeks=int(qtd))

    # --------------------------------------------------------
    # Datas
    # --------------------------------------------------------
    if data is None and momento is None:
        if leitor.procurar(r"\bdepois\s+de\s+amanha\b"):
            data = hoje + datetime.timedelta(days=2)

        elif leitor.procurar(r"\bamanha\b"):
            data = hoje + datetime.timedelta(days=1)

        elif leitor.procurar(r"\bhoje\b"):
            data = hoje
            hoje_explicito = True

    if data is None and momento is None:
        m = leitor.procurar(r"\b(?:dia\s+)?(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?\b")

        if m:
            dia, mes = int(m.group(1)), int(m.group(2))
            ano = m.group(3)

            if ano:
                ano = int(ano)
                ano = ano + 2000 if ano < 100 else ano
            else:
                ano = hoje.year

            try:
                data = datetime.date(ano, mes, dia)

                if not m.group(3) and data < hoje:
                    data = data.replace(year=ano + 1)

            except ValueError:
                r.erro = "Data inválida."

    if data is None and momento is None and not r.erro:
        m = leitor.procurar(r"\bdia\s+(\d{1,2})\b")

        if m:
            dia = int(m.group(1))
            ano, mes = hoje.year, hoje.month

            if dia < hoje.day:
                mes += 1
                if mes > 12:
                    mes, ano = 1, ano + 1

            if 1 <= dia <= calendar.monthrange(ano, mes)[1]:
                data = datetime.date(ano, mes, dia)
            else:
                r.erro = f"Esse mês não tem dia {dia}."

    if data is None and momento is None and dia_semana is None:
        m = leitor.procurar(
            r"\b(?:(?:na|no|nesta|neste|nessa|nesse|esta|este)\s+)?"
            r"(proxima\s+|proximo\s+)?" + _DIA + r"(\s+que\s+vem)?\b"
        )

        if m:
            dia_semana = DIAS_SEMANA[m.group(2)]

            if m.group(1) or m.group(3):
                # "proxima segunda": nunca hoje
                delta = (dia_semana - hoje.weekday()) % 7 or 7
                data = hoje + datetime.timedelta(days=delta)
                dia_semana = None

    # --------------------------------------------------------
    # Horario
    # --------------------------------------------------------
    if momento is None:
        m = leitor.procurar(r"\b(?:as\s+|a\s+|pelas\s+)?(\d{1,2})\s*(?::|h)\s*(\d{2})\b")

        if m:
            hora = (int(m.group(1)), int(m.group(2)))

        if hora is None:
            m = leitor.procurar(r"\b(?:as\s+|a\s+|pelas\s+)?(\d{1,2})\s*(?:h|hs|hrs|horas?)\b")

            if m:
                hora = (int(m.group(1)), 0)

        if hora is None:
            m = leitor.procurar(r"\b(?:as|pelas)\s+(\d{1,2})\b")

            if m:
                hora = (int(m.group(1)), 0)

        if hora is None:
            # "8 da noite", "as 7 da manha"
            m = leitor.procurar(
                r"\b(?:as\s+|pelas\s+)?(\d{1,2})\s+(?:da|de|a)\s+(manha|tarde|noite)\b"
            )

            if m:
                hora = (int(m.group(1)), 0)
                periodo = m.group(2)

        if hora is None:
            if leitor.procurar(r"\b(?:ao\s+|as\s+|a\s+)?meio[- ]dia\b"):
                hora = (12, 0)
            elif leitor.procurar(r"\b(?:a\s+)?meia[- ]noite\b"):
                hora = (0, 0)

        m = leitor.procurar(r"\b(?:da|de|pela|a|as|na)\s+(manha|tarde|noite)\b")

        if m:
            periodo = m.group(1)

    if hora is not None:
        h, mi = hora

        if periodo in ("tarde", "noite") and h < 12:
            h += 12

        if not (0 <= h <= 23 and 0 <= mi <= 59):
            r.erro = r.erro or "Horário inválido."
        else:
            hora = (h, mi)

    elif periodo:
        hora = (PERIODOS[periodo], 0)

    # --------------------------------------------------------
    # Monta data e hora finais
    # --------------------------------------------------------
    if momento is not None:
        alvo = momento
        r.detectado.update({"data", "hora"})

    else:
        if dia_semana is not None:
            delta = (dia_semana - hoje.weekday()) % 7
            data = hoje + datetime.timedelta(days=delta)

        if data is not None:
            r.detectado.add("data")

        if hora is not None and not r.erro:
            r.detectado.add("hora")

        if r.erro:
            alvo = None

        elif data is None and hora is None:
            alvo = _proxima_hora_cheia(agora)

        elif data is None:
            alvo = datetime.datetime.combine(hoje, datetime.time(*hora))

            # Horario que ja passou hoje vai para amanha.
            if alvo <= agora:
                alvo += datetime.timedelta(days=1)

        elif hora is None:
            if data == hoje:
                alvo = _proxima_hora_cheia(agora)
            else:
                alvo = datetime.datetime.combine(data, datetime.time(9, 0))

        else:
            alvo = datetime.datetime.combine(data, datetime.time(*hora))

            # "sexta 9h" numa sexta depois das 9h: proxima semana.
            if (
                alvo <= agora
                and dia_semana is not None
                and not hoje_explicito
            ):
                alvo += datetime.timedelta(days=7)

    if alvo is not None:
        r.data = alvo.date()
        r.hora = alvo.strftime("%H:%M")

        if alvo <= agora and not r.erro:
            r.erro = "Esse horário já passou."

    # --------------------------------------------------------
    # Titulo
    # --------------------------------------------------------
    r.titulo = _limpar_titulo(leitor.resto())

    if not r.titulo and not r.erro:
        r.erro = "Escreva o que precisa ser feito."

    return r


# ============================================================
# TEXTO PARA A PREVIA
# ============================================================

_NOMES_DIA = (
    "segunda",
    "terça",
    "quarta",
    "quinta",
    "sexta",
    "sábado",
    "domingo",
)


def descrever_data(data, hoje=None):
    """'Hoje', 'Amanhã', 'Sexta, 20/11' ..."""
    if data is None:
        return ""

    hoje = hoje or datetime.date.today()
    delta = (data - hoje).days

    if delta == 0:
        return "Hoje"

    if delta == 1:
        return "Amanhã"

    nome = _NOMES_DIA[data.weekday()].capitalize()

    if 1 < delta < 7:
        return f"{nome}, {data.strftime('%d/%m')}"

    return f"{nome}, {data.strftime('%d/%m/%Y')}"
