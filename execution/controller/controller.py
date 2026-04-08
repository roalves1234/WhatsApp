import textwrap
from collections import deque
from datetime import date, datetime
from pathlib import Path

from loguru import logger

from execution.controller.agente import Agente
from execution.controller.base_vetorial import construir_base_vetorial
from execution.controller.classes import InteracaoUser, InteracaoAssistant
from execution.controller.conhecimento_view import ConhecimentoView
from execution.controller.home import Home
from execution.controller.log_view import LogView
from execution.controller.uzapi import Uzapi
from execution.controller.version import Version
from execution.dao.dao_interacao import DaoInteracao
from execution.dao.dao_conhecimento import DaoConhecimento


class Controller:
    _agente: Agente = Agente()

    @staticmethod
    def get_home() -> str:
        return Home.get()

    @staticmethod
    def get_lista_log(quantidade: int, data: date, nivel: str | None, fone: str | None) -> str:
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
            registros = Controller._parsear_linhas_log(linhas_recentes)

        return LogView.get(
            registros=registros,
            quantidade=quantidade,
            data=data,
            nivel=nivel,
            fone=fone,
        )

    @staticmethod
    def _parsear_linhas_log(linhas: list[str]) -> list[dict]:
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
    async def eliminar_historico(fone: str) -> None:
        """
        Apaga o histórico do fone.
        """
        await DaoInteracao.delete_by_fone(fone)
        logger.info("HISTÓRICO | Eliminado | fone={fone}", fone=fone)

    @staticmethod
    async def get_lista_interacao_by_fone(fone: str) -> list[dict]:
        return await DaoInteracao.get_by_fone(fone)

    @staticmethod
    async def salvarInteracaoUser(fone: str, nome: str, mensagem: str) -> InteracaoUser:
        """
        Cria e persiste uma interação do usuário no banco de dados.
        Retorna o objeto InteracaoUser persistido.
        """
        interacao_user = InteracaoUser(fone=fone, nome=nome, mensagem=mensagem)
        await DaoInteracao.persistir(interacao_user)
        logger.debug("INTERAÇÃO USER | Persistida | fone={fone} | nome={nome}", fone=fone, nome=nome)
        return interacao_user

    @staticmethod
    async def doInteracaoAssistant(fone: str, nome: str) -> InteracaoAssistant:
        """
        Orquestra o fluxo completo de interação do assistente:
        1. Busca o histórico de interações do fone
        2. Obtém resposta da LLM via enviar_resposta_assistant
        3. Persiste a interação do assistente no banco de dados
        Retorna o objeto InteracaoAssistant persistido.
        """
        contexto_entrada = await DaoInteracao.get_by_fone(fone)
        interacao_assistant = await Controller.enviar_resposta_assistant(fone, nome, contexto_entrada)
        await DaoInteracao.persistir(interacao_assistant)
        logger.debug("INTERAÇÃO ASSISTANT | Persistida | fone={fone}", fone=fone)
        return interacao_assistant

    @staticmethod
    async def get_conhecimento() -> str:
        """Carrega o texto da base de conhecimento e retorna a página HTML do editor."""
        texto = await DaoConhecimento.buscar_texto()
        return ConhecimentoView.get(texto)

    @staticmethod
    def get_lista_arquivos() -> dict[str, list[dict]]:
        """
        Lista arquivos de log (.log) e índices FAISS (.faiss) com metadados.
        Arquivos FAISS salvos como diretório têm o tamanho calculado como soma dos conteúdos internos.
        """
        def _info_arquivo(caminho: Path) -> dict:
            """Retorna metadados de um arquivo ou diretório."""
            if caminho.is_dir():
                tamanho = sum(f.stat().st_size for f in caminho.rglob("*") if f.is_file())
            else:
                tamanho = caminho.stat().st_size
            modificado = datetime.fromtimestamp(caminho.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            return {"nome": caminho.name, "tamanho_bytes": tamanho, "modificado_em": modificado}

        # Logs na pasta /logs
        pasta_logs = Path("logs")
        arquivos_log = sorted(
            [_info_arquivo(f) for f in pasta_logs.glob("*.log") if f.is_file()],
            key=lambda x: x["modificado_em"],
            reverse=True,
        ) if pasta_logs.exists() else []

        # Índices FAISS (diretórios ou arquivos com extensão .faiss na raiz)
        raiz = Path(".")
        arquivos_faiss = sorted(
            [_info_arquivo(p) for p in raiz.glob("*.faiss")],
            key=lambda x: x["modificado_em"],
            reverse=True,
        )

        return {"logs": arquivos_log, "faiss": arquivos_faiss}

    @staticmethod
    async def salvar_conhecimento(texto: str) -> dict[str, bool]:
        """Persiste o texto da base de conhecimento no Supabase e reconstrói a base vetorial FAISS."""
        await DaoConhecimento.salvar_texto(texto)
        construir_base_vetorial(texto)
        return {"sucesso": True}

    @staticmethod
    async def enviar_resposta_assistant(fone: str, nome: str, contexto_entrada: list[dict]) -> InteracaoAssistant:
        """
        Orquestra o fluxo completo de resposta inteligente:
        1. Obtém a resposta da LLM via classe Agente (já instanciada no Controller)
        2. Envia a resposta ao remetente via Uzapi.enviar_texto
        """

        # Consulta a LLM com o contexto recebido pelo usuário usando a instância única
        interacao_assistant = await Controller._agente.obter_resposta(fone, nome, contexto_entrada)

        # Resposta da IA, incluindo o tempo de resposta e versão:
        texto_resposta = textwrap.dedent(f"""
                                        {interacao_assistant.mensagem}
                                        🧠 {interacao_assistant.conteudo.raciocinio}
                                        ⏱ {interacao_assistant.duracao}
                                        🏷️ v{Version().get()}
                                        """).strip()

        # Envia para WhatsApp
        await Uzapi.enviar_digitando(fone, texto_resposta)
        await Uzapi.enviar_texto(fone, texto_resposta)

        logger.info(
            "RESPOSTA | fone={fone} | duração={duracao} | tokens_entrada={tin} | tokens_saida={tout}",
            fone=fone,
            duracao=interacao_assistant.duracao,
            tin=interacao_assistant.tokens_entrada,
            tout=interacao_assistant.tokens_saida,
        )

        return interacao_assistant
