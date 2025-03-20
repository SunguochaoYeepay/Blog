import pytest
from app.schemas.common import OrderEnum, StatusEnum, PaginationParams

def test_order_enum():
    """测试排序枚举"""
    assert OrderEnum.asc.value == "asc"
    assert OrderEnum.desc.value == "desc"

def test_status_enum():
    """测试状态枚举"""
    assert StatusEnum.active.value == "active"
    assert StatusEnum.inactive.value == "inactive"
    assert StatusEnum.deleted.value == "deleted"

def test_pagination_params():
    """测试分页参数"""
    params = PaginationParams(page=1, size=10)
    assert params.page == 1
    assert params.size == 10
    
    # 测试默认值
    default_params = PaginationParams()
    assert default_params.page == 1
    assert default_params.size == 10