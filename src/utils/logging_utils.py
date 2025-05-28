import logging
import sys

LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
}

def setup_logger(level: str = "info", name: str = __name__) -> logging.Logger:
    logger = logging.getLogger(name)
    """
    logger.propagate = True (기본값) 이면 로그 메시지가 부모 로거에게 전달된다.
    Celery 나 Django 같은 프레임워크는 기본적으로 로깅세팅이 되어있으므로,
    결과적으로 내가 설정한 로거에서 출력 (1) 부모로거(프레임워크 기본로거)에서 출력 (2) 된다.
    그래서 False 로 해두면 부모로거에 전달되지 않으므로 1번만 로그를 출력할 수 있게 된다. 
    """
    logger.propagate = False
    log_level = LOG_LEVELS.get(level.lower(), logging.INFO)
    logger.setLevel(log_level)

    # 중복 핸들러 방지
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        handler.setLevel(log_level)
        logger.addHandler(handler)

    return logger