from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class InfoArquivo:
    """Metadados de um arquivo de log listado para o visualizador."""
    nome: str
    tamanho: int
    data_modificacao: datetime


class ArquivoTool:
    """Camada DAO para leitura dos arquivos da pasta logs/."""

    _DIR_LOGS: Path = Path(__file__).parent.parent.parent / "logs"
    _EXTENSOES_PERMITIDAS: set[str] = {".log", ".agno"}
    _TAMANHO_MAXIMO_BYTES: int = 5_000_000

    @staticmethod
    def listar() -> list[InfoArquivo]:
        """Lista arquivos .log e .agno da pasta logs/, ordenados por data desc."""
        if not ArquivoTool._DIR_LOGS.exists():
            return []

        arquivos: list[InfoArquivo] = []
        for caminho in ArquivoTool._DIR_LOGS.iterdir():
            if not caminho.is_file():
                continue
            if caminho.suffix not in ArquivoTool._EXTENSOES_PERMITIDAS:
                continue
            estatisticas = caminho.stat()
            arquivos.append(
                InfoArquivo(
                    nome=caminho.name,
                    tamanho=estatisticas.st_size,
                    data_modificacao=datetime.fromtimestamp(estatisticas.st_mtime),
                )
            )

        arquivos.sort(key=lambda info: info.data_modificacao, reverse=True)
        return arquivos

    @staticmethod
    def ler_conteudo(nome: str) -> str:
        """
        Lê o conteúdo bruto de um arquivo da pasta logs/.
        Retorna texto não escapado — a camada View é responsável pelo escape HTML.
        """
        # Descarta qualquer componente de diretório no nome recebido
        nome_seguro = Path(nome).name

        # Valida extensão antes de tocar no sistema de arquivos
        if Path(nome_seguro).suffix not in ArquivoTool._EXTENSOES_PERMITIDAS:
            return "[Arquivo inválido: extensão não permitida]"

        caminho = (ArquivoTool._DIR_LOGS / nome_seguro).resolve()

        # Garante que o caminho resolvido permanece dentro da pasta logs/ (anti path traversal)
        if caminho.parent != ArquivoTool._DIR_LOGS.resolve():
            return "[Arquivo inválido: caminho fora da pasta de logs]"

        if not caminho.exists() or not caminho.is_file():
            return "[Arquivo não encontrado]"

        tamanho = caminho.stat().st_size

        # Para arquivos muito grandes, lê apenas os últimos N bytes para evitar travar o navegador
        if tamanho > ArquivoTool._TAMANHO_MAXIMO_BYTES:
            with caminho.open("rb") as arquivo_binario:
                arquivo_binario.seek(-ArquivoTool._TAMANHO_MAXIMO_BYTES, 2)
                bytes_finais = arquivo_binario.read()
            conteudo = bytes_finais.decode("utf-8", errors="replace")
            banner = (
                f"[ARQUIVO TRUNCADO - exibindo últimos "
                f"{ArquivoTool._TAMANHO_MAXIMO_BYTES // 1_000_000} MB de "
                f"{tamanho // 1_000_000} MB]\n\n"
            )
            return banner + conteudo

        return caminho.read_text(encoding="utf-8", errors="replace")
