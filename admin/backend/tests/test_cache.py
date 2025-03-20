import pytest
from app.utils.cache import RedisCache
import json

def test_set_cache():
    cache = RedisCache()
    
    # 测试设置字符串
    assert cache.set("test_str", "value")
    
    # 测试设置字典
    assert cache.set("test_dict", {"key": "value"})
    
    # 测试设置带过期时间
    assert cache.set("test_expire", "value", 60)

def test_get_cache():
    cache = RedisCache()
    
    # 测试获取字符串
    cache.set("test_str", "value")
    assert cache.get("test_str") == "value"
    
    # 测试获取字典
    test_dict = {"key": "value"}
    cache.set("test_dict", test_dict)
    assert cache.get("test_dict") == test_dict
    
    # 测试获取不存在的键
    assert cache.get("not_exist") is None

def test_delete_cache():
    cache = RedisCache()
    
    # 设置测试数据
    cache.set("test_delete", "value")
    
    # 测试删除
    assert cache.delete("test_delete")
    assert cache.get("test_delete") is None
    
    # 测试删除不存在的键
    assert not cache.delete("not_exist")

def test_clear_cache():
    cache = RedisCache()
    
    # 设置测试数据
    cache.set("test1", "value1")
    cache.set("test2", "value2")
    
    # 测试清空
    assert cache.clear()
    assert cache.get("test1") is None
    assert cache.get("test2") is None