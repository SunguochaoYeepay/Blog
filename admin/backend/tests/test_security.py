import pytest
from app.utils.security import generate_random_string, get_password_hash

def test_generate_random_string():
    # 测试默认长度
    random_str = generate_random_string()
    assert len(random_str) == 32
    assert isinstance(random_str, str)
    
    # 测试指定长度
    length = 16
    random_str = generate_random_string(length)
    assert len(random_str) == length
    assert isinstance(random_str, str)
    
    # 测试生成的字符串是否唯一
    str1 = generate_random_string()
    str2 = generate_random_string()
    assert str1 != str2

def test_hash_password():
    password = "test_password"
    hashed = get_password_hash(password)
    
    # 验证哈希结果是字符串
    assert isinstance(hashed, str)
    
    # 验证哈希结果不等于原密码
    assert hashed != password
    
    # 验证哈希结果长度不为0
    assert len(hashed) > 0