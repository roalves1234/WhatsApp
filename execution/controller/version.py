from pathlib import Path


class Version:
    # Caminho para o arquivo de versão, relativo ao diretório pai deste módulo
    _caminho_arquivo: Path = Path(__file__).parent.parent / "version.txt"

    def get(self) -> str:
        """Lê e retorna a versão registrada no arquivo version.txt."""
        return self._caminho_arquivo.read_text(encoding="utf-8").strip()
