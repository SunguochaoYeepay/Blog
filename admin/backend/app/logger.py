import logging
import sys
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler

# 配置日志格式
log_format = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

def setup_logger(name: str) -> logging.Logger:
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
    """
    # 如果已经存在同名的 logger，直接返回
    existing_logger = logging.getLogger(name)
    if existing_logger.handlers:
        return existing_logger
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # 确定日志目录
    log_dir = os.environ.get("LOG_DIR", "logs")
    log_dir = Path(log_dir)
    log_dir.mkdir(exist_ok=True)

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