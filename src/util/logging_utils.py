import logging


LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
}

def setup_logging(level: str = "info"):
    """로깅 설정을 초기화합니다.

    Args:
        level (str): 로그 레벨 (debug, info, warning, error, critical)
    """
    log_level = LOG_LEVELS.get(level.lower(), logging.INFO)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )