import re
from unidecode import unidecode

def generate_slug(text: str) -> str:
    """
    生成 URL 友好的 slug
    
    Args:
        text: 要转换的文本
        
    Returns:
        转换后的 slug
    """
    # 转换为小写并移除重音符号
    text = unidecode(text.lower())
    
    # 将空格和特殊字符替换为连字符
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text).strip('-')
    
    return text 