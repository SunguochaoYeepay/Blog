import re
from typing import Optional
from unidecode import unidecode

def slugify(text: str) -> str:
    """
    将文本转换为 URL 友好的 slug。
    
    Args:
        text: 要转换的文本
        
    Returns:
        转换后的 slug
    """
    # 转换为小写并移除重音符号
    text = str(text).lower().strip()
    text = unidecode(text)
    
    # 将空格和其他特殊字符替换为连字符
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    
    return text.strip('-') 