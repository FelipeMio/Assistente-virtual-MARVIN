from pathlib import Path

from PIL import Image, ImageTk


class SpriteLoader:

    def __init__(
        self,
        *,
        config,
        asset_root=None,
    ):
        self.config = config

        self.asset_root = (
            Path(asset_root)
            if asset_root is not None
            else (
                Path(__file__)
                .resolve()
                .parent
                / "assets"
                / "marvin"
            )
        )


    # ========================================================
    # SIZE
    # ========================================================

    def normal_sprite_size(self):
        percentual = int(
            self.config.get(
                "tamanho_normal",
                100,
            )
        )

        percentual = max(
            60,
            min(
                120,
                percentual,
            ),
        )

        return max(
            1,
            int(
                150
                * percentual
                / 100
            ),
        )


    def compact_sprite_scale(self):
        percentual = int(
            self.config.get(
                "tamanho_compacto",
                85,
            )
        )

        percentual = max(
            60,
            min(
                120,
                percentual,
            ),
        )

        return (
            percentual / 100.0
        )


    # ========================================================
    # GENERIC LOADER
    # ========================================================

    def load_frames(
        self,
        subfolder,
        filenames,
        *,
        label,
        missing_label=None,
    ):
        pasta = (
            self.asset_root
            / subfolder
        )

        frames = []


        for filename in filenames:
            arquivo = (
                pasta / filename
            )

            if not arquivo.exists():
                descricao = (
                    missing_label
                    or f"Sprite {label}"
                )

                print(
                    "[MARVIN] "
                    f"{descricao} nao encontrado: "
                    f"{arquivo}"
                )

                continue


            imagem = (
                Image.open(
                    arquivo
                )
                .convert("RGBA")
            )


            tamanho = (
                self.normal_sprite_size()
            )


            imagem = imagem.resize(
                (
                    tamanho,
                    tamanho,
                ),
                Image.Resampling.NEAREST,
            )


            frames.append(
                ImageTk.PhotoImage(
                    imagem
                )
            )


        print(
            "[MARVIN] "
            f"{len(frames)} frame(s) "
            f"{label} carregado(s)."
        )


        return frames


    # ========================================================
    # NORMAL SPRITES
    # ========================================================

    def load_idle_frames(self):
        return self.load_frames(
            "idle",
            (
                "01.png",
                "02.png",
            ),
            label="idle",
            missing_label="Sprite",
        )


    def load_alert_frames(self):
        return self.load_frames(
            "alert",
            (
                "01.png",
                "02.png",
            ),
            label="alert",
            missing_label=(
                "Sprite de alerta"
            ),
        )


    def load_waiting_frames(self):
        return self.load_frames(
            "waiting",
            (
                "01.png",
                "02.png",
                "03.png",
            ),
            label="waiting",
            missing_label=(
                "Sprite waiting"
            ),
        )


    def load_yawn_frames(self):
        return self.load_frames(
            "yawn",
            (
                "01.png",
                "02.png",
            ),
            label="yawn",
            missing_label=(
                "Sprite yawn"
            ),
        )


    # ========================================================
    # HAPPY
    # ========================================================

    def load_happy_frame(self):
        arquivo = (
            self.asset_root
            / "happy"
            / "01.png"
        )


        if not arquivo.exists():
            print(
                "[MARVIN] Sprite happy "
                f"nao encontrado: {arquivo}"
            )

            return None


        imagem = (
            Image.open(
                arquivo
            )
            .convert("RGBA")
        )


        tamanho = (
            self.normal_sprite_size()
        )


        imagem = imagem.resize(
            (
                tamanho,
                tamanho,
            ),
            Image.Resampling.NEAREST,
        )


        frame = ImageTk.PhotoImage(
            imagem
        )


        print(
            "[MARVIN] frame happy carregado."
        )


        return frame


    # ========================================================
    # COMPACT
    # ========================================================

    def load_compact_frames(self):
        pasta = (
            self.asset_root
            / "compact"
        )


        arquivos = [
            pasta / "01.png",
            pasta / "02.png",
            pasta / "03.png",
        ]


        imagens = []


        for arquivo in arquivos:

            if not arquivo.exists():
                print(
                    "[MARVIN] Sprite compact "
                    f"nao encontrado: {arquivo}"
                )

                continue


            imagens.append(
                Image.open(
                    arquivo
                ).convert(
                    "RGBA"
                )
            )


        if not imagens:
            return []


        caixas = []


        for imagem in imagens:
            bbox = (
                imagem
                .getchannel("A")
                .getbbox()
            )

            if bbox:
                caixas.append(
                    bbox
                )


        if not caixas:
            return []


        left = min(
            b[0]
            for b in caixas
        )

        top = min(
            b[1]
            for b in caixas
        )

        right = max(
            b[2]
            for b in caixas
        )

        bottom = max(
            b[3]
            for b in caixas
        )


        crop_box = (
            left,
            top,
            right,
            bottom,
        )


        largura = right - left
        altura = bottom - top


        compact_scale = (
            self.compact_sprite_scale()
        )


        max_w = max(
            1,
            int(
                92
                * compact_scale
            ),
        )

        max_h = max(
            1,
            int(
                64
                * compact_scale
            ),
        )


        escala = min(
            max_w / largura,
            max_h / altura,
        )


        novo_w = max(
            1,
            int(
                largura
                * escala
            ),
        )

        novo_h = max(
            1,
            int(
                altura
                * escala
            ),
        )


        frames = []


        for imagem in imagens:
            imagem = imagem.crop(
                crop_box
            )

            imagem = imagem.resize(
                (
                    novo_w,
                    novo_h,
                ),
                Image.Resampling.NEAREST,
            )


            frames.append(
                ImageTk.PhotoImage(
                    imagem
                )
            )


        print(
            "[MARVIN] "
            f"{len(frames)} frame(s) "
            "compact carregado(s)."
        )


        return frames


    # ========================================================
    # ALL
    # ========================================================

    def load_all(self):
        return {
            "idle":
                self.load_idle_frames(),

            "alert":
                self.load_alert_frames(),

            "waiting":
                self.load_waiting_frames(),

            "happy":
                self.load_happy_frame(),

            "compact":
                self.load_compact_frames(),

            "yawn":
                self.load_yawn_frames(),
        }
