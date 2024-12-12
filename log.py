import logging


class AlignedFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, level_width=8, name_width=16):
        super().__init__(fmt, datefmt)
        self.level_width = level_width
        self.name_width = name_width

    def format(self, record):
        record.levelname = f"{record.levelname:<{self.level_width}}"  # Aligns left (e.g. INFO  , WARNING)
        record.name = f"[{record.name:<{self.name_width}}]"           # Aligns left (e.g. [root           ])
        return super().format(record)


def configure_logger():
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    
    log_format = "%(asctime)s | %(name)s %(levelname)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    formatter = AlignedFormatter(fmt=log_format, datefmt=date_format)
    handler.setFormatter(formatter)
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    
    return logger