from collections import deque
from datetime import date, datetime
from pathlib import Path

from execution.controller.log_view import LogView


class LogFile:

    @staticmethod
    def listar(quantidade: int, data: date, nivel: str | None, fone: str | None) -> str:
        """
        Lê o arquivo de log da data informada, filtra e retorna HTML com grid navegável.
        """
        caminho = Path(f"logs/app_{data}.log")
        if not caminho.exists():
            registros: list[dict] = []
        else:
            with caminho.open("r", encoding="utf-8") as arquivo:
                linhas = arquivo.readlines()

            # Filtra por nível (ex: INFO, ERROR)
            if nivel:
                linhas = [l for l in linhas if f"| {nivel.upper()}" in l]

            # Filtra por fone — aceita com ou sem formatação
            if fone:
                fone_digitos = ''.join(filter(str.isdigit, fone))
                linhas = [l for l in linhas if fone_digitos in l or fone in l]

            # Pega as últimas N linhas e parseia em dicts estruturados
            linhas_recentes = list(deque(linhas, maxlen=quantidade))
            registros = LogFile._parsear_linhas(linhas_recentes)

        return LogView.get(
            registros=registros,
            quantidade=quantidade,
            data=data,
            nivel=nivel,
            fone=fone,
        )

    @staticmethod
    def _parsear_linhas(linhas: list[str]) -> list[dict]:
        """
        Converte linhas de texto do log no formato:
        'DD/MM/YYYY HH:mm:ss | LEVEL    | name:function:line | message'
        em lista de dicts com chaves: data_hora, nivel, local, mensagem.
        Linhas que não seguem o formato são agrupadas na mensagem anterior.
        """
        registros: list[dict] = []
        for linha in linhas:
            partes = linha.split("|", 3)
            if len(partes) == 4:
                registros.append({
                    "data_hora": partes[0].strip(),
                    "nivel":     partes[1].strip(),
                    "local":     partes[2].strip(),
                    "mensagem":  partes[3].strip(),
                })
            elif registros:
                # Linha de continuação (ex: traceback) — anexa à mensagem anterior
                registros[-1]["mensagem"] += "\n" + linha.rstrip()
        return registros

    @staticmethod
    def listar_arquivos() -> dict[str, list[dict]]:
        """
        Lista arquivos de log (.log) com nome, tamanho e data de modificação.
        """
        def _info_arquivo(caminho: Path) -> dict:
            """Retorna metadados de um arquivo."""
            tamanho = caminho.stat().st_size
            modificado = datetime.fromtimestamp(caminho.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            return {"nome": caminho.name, "tamanho": tamanho, "data": modificado}

        pasta_logs = Path("logs")
        arquivos_log = sorted(
            [_info_arquivo(f) for f in pasta_logs.glob("*.log") if f.is_file()],
            key=lambda x: x["data"],
            reverse=True,
        ) if pasta_logs.exists() else []

        return {"logs": arquivos_log}
