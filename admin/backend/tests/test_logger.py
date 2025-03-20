import os
from app.logger import setup_logger
import logging
import tempfile
import shutil

def test_setup_logger():
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    try:
        # 设置临时日志目录
        os.environ["LOG_DIR"] = temp_dir
        
        # 测试日志配置
        logger = setup_logger("test")
        
        # 验证日志级别
        assert logger.level == logging.DEBUG
        
        # 验证处理器数量
        assert len(logger.handlers) == 2
        
        # 验证处理器类型
        assert isinstance(logger.handlers[0], logging.StreamHandler)
        assert isinstance(logger.handlers[1], logging.handlers.RotatingFileHandler)
        
        # 测试日志写入
        test_message = "Test log message"
        logger.info(test_message)
        
        # 验证日志文件是否存在
        log_file = os.path.join(temp_dir, "test.log")
        assert os.path.exists(log_file)
        
        # 验证日志内容
        with open(log_file, "r") as f:
            log_content = f.read()
            assert test_message in log_content
            
    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)

def test_get_logger():
    # 测试获取相同名称的logger
    logger1 = setup_logger("test_module")
    logger2 = setup_logger("test_module")
    
    # 验证是否返回相同的logger实例
    assert logger1 is logger2
    
    # 验证logger名称
    assert logger1.name == "test_module"