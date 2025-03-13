import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

# 创建日志目录
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# 配置日志格式
log_format = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    # 文件处理器 - 按大小轮转
    file_handler = RotatingFileHandler(
        log_dir / f"{name}.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(log_format)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    return logger

# 创建应用主日志记录器
app_logger = setup_logger("app") 