import logging
from logging.handlers import RotatingFileHandler


class Logger:
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        logger = logging.getLogger(name)
        if not logger.hasHandlers():
            logger.setLevel(logging.DEBUG)

            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)

            console_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            console_handler.setFormatter(console_formatter)

            rotating_file_handler = RotatingFileHandler(
                "app.log", maxBytes=1024 * 1024 * 5, backupCount=3
            )
            rotating_file_handler.setLevel(logging.DEBUG)

            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            rotating_file_handler.setFormatter(file_formatter)

            logger.addHandler(console_handler)
            logger.addHandler(rotating_file_handler)

        return logger
