import json
from pathlib import Path


HOME = Path.home() / ".marvin"
HOME.mkdir(exist_ok=True)

CFG_F = HOME / "config.json"


CFG_DEFAULTS = {
    "pos_x": None,
    "pos_y": None,
    "pos_compact_x": None,
    "pos_compact_y": None,
    "nao_perturbe": False,
    "som": True,
    "opacidade": 1.0,
    "tamanho_normal": 90,
    "tamanho_compacto": 85,
    "ultimo_resumo_dia": None,
    "frases_idle": [
        "Clique com botao esquerdo para o menu.",
        "Clique com botao direito para o menu.",
    ],
    "frases_waiting": [
        "Ei... {tarefa}",
        "Vai fazer ou adiar? {tarefa}",
        "Ainda estou esperando: {tarefa}",
    ],
}


def load_cfg():
    if CFG_F.exists():
        try:
            data = json.loads(CFG_F.read_text("utf-8"))
            return {**CFG_DEFAULTS, **data}
        except Exception:
            pass

    return dict(CFG_DEFAULTS)


def save_cfg(cfg):
    CFG_F.write_text(
        json.dumps(cfg, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

