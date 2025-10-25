import logging
import time
import watchtower
from config import config


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(console)

    try:
        cw_handler = watchtower.CloudWatchLogHandler(
            log_group=config.LOG_GROUP,
            stream_name=f"{name}-{int(time.time())}",
            use_queues=True,
        )
        cw_handler.setLevel(logging.INFO)
        logger.addHandler(cw_handler)
    except Exception as e:
        logger.warning(f"CloudWatch logging not available: {e}")

    return logger
