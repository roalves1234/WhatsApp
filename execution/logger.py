import sys
from loguru import logger

# Remove o handler padrão para configurar do zero
logger.remove()

# Saída no terminal com cores
logger.add(
    sys.stdout,
    level="DEBUG",
    format="<green>{time:DD/MM/YYYY HH:mm:ss}</green> | <level>{level:<8}</level> | <cyan>{name}:{function}:{line}</cyan> | {message}",
    colorize=True,
)

# Saída em arquivo com rotação diária e retenção de 30 dias
logger.add(
    "logs/app_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="30 days",
    level="DEBUG",
    format="{time:DD/MM/YYYY HH:mm:ss} | {level:<8} | {name}:{function}:{line} | {message}",
    backtrace=True,   # call stack completo no traceback
    diagnose=True,    # exibe valores das variáveis locais em cada frame
    encoding="utf-8",
)
