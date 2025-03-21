import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.errors import ErrorCode, ErrorMessages
from app.models.category import Category
from app.models.article import Article

class TestCategoryAPI:
    def test_create_category(self, client: TestClient, db_session: Session):
        """测试创建分类"""
        category_data = {
            "name": "Test Category",
            "slug": "test-category",
            "description": "Test Description",
            "parent_id": None
        }
        response = client.post("/api/categories", json=category_data)
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.SUCCESS
        assert response.json()["message"] == ErrorMessages.CATEGORY_CREATE_SUCCESS
        data = response.json()["data"]
        assert data["name"] == category_data["name"]
        assert data["slug"] == category_data["slug"]
        assert data["description"] == category_data["description"]

    def test_create_category_name_exists(self, client: TestClient, db_session: Session):
        """测试创建分类 - 名称已存在"""
        # 先创建一个分类
        category = Category(
            name="Test Category",
            slug="test-category",
            description="Test Description"
        )
        db_session.add(category)
        db_session.commit()

        # 尝试创建同名分类
        category_data = {
            "name": "Test Category",
            "slug": "test-category-2",
            "description": "Test Description"
        }
        response = client.post("/api/categories", json=category_data)
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.CATEGORY_NAME_EXISTS
        assert response.json()["message"] == ErrorMessages.CATEGORY_NAME_EXISTS

    def test_create_category_slug_exists(self, client: TestClient, db_session: Session):
        """测试创建分类 - 别名已存在"""
        # 先创建一个分类
        category = Category(
            name="Test Category 1",
            slug="test-category",
            description="Test Description"
        )
        db_session.add(category)
        db_session.commit()

        # 尝试创建相同别名的分类
        category_data = {
            "name": "Test Category 2",
            "slug": "test-category",
            "description": "Test Description"
        }
        response = client.post("/api/categories", json=category_data)
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.CATEGORY_SLUG_EXISTS
        assert response.json()["message"] == ErrorMessages.CATEGORY_SLUG_EXISTS

    def test_create_category_parent_not_found(self, client: TestClient, db_session: Session):
        """测试创建分类 - 父分类不存在"""
        category_data = {
            "name": "Test Category",
            "slug": "test-category",
            "description": "Test Description",
            "parent_id": 999  # 不存在的父分类ID
        }
        response = client.post("/api/categories", json=category_data)
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.CATEGORY_NOT_FOUND
        assert response.json()["message"] == ErrorMessages.CATEGORY_NOT_FOUND

    def test_get_categories(self, client: TestClient, db_session: Session):
        """测试获取分类列表"""
        # 创建多个分类
        categories = []
        for i in range(3):
            category = Category(
                name=f"Test Category {i}",
                slug=f"test-category-{i}",
                description=f"Test Description {i}"
            )
            db_session.add(category)
            categories.append(category)
        db_session.commit()

        response = client.get("/api/categories")
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.SUCCESS
        assert response.json()["message"] == ErrorMessages.SUCCESS
        data = response.json()["data"]
        assert len(data["items"]) >= 3
        assert data["total"] >= 3

    def test_update_category(self, client: TestClient, db_session: Session):
        """测试更新分类"""
        # 创建一个分类
        category = Category(
            name="Test Category",
            slug="test-category",
            description="Test Description"
        )
        db_session.add(category)
        db_session.commit()

        # 更新分类
        update_data = {
            "name": "Updated Category",
            "description": "Updated Description"
        }
        response = client.put(f"/api/categories/{category.id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.SUCCESS
        assert response.json()["message"] == ErrorMessages.CATEGORY_UPDATE_SUCCESS
        data = response.json()["data"]
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]

    def test_update_category_not_found(self, client: TestClient, db_session: Session):
        """测试更新分类 - 分类不存在"""
        update_data = {
            "name": "Updated Category",
            "description": "Updated Description"
        }
        response = client.put("/api/categories/999", json=update_data)
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.CATEGORY_NOT_FOUND
        assert response.json()["message"] == ErrorMessages.CATEGORY_NOT_FOUND

    def test_update_category_name_exists(self, client: TestClient, db_session: Session):
        """测试更新分类 - 名称已存在"""
        # 创建两个分类
        category1 = Category(
            name="Test Category 1",
            slug="test-category-1",
            description="Test Description 1"
        )
        category2 = Category(
            name="Test Category 2",
            slug="test-category-2",
            description="Test Description 2"
        )
        db_session.add_all([category1, category2])
        db_session.commit()

        # 尝试将第二个分类的名称更新为第一个分类的名称
        update_data = {
            "name": "Test Category 1"
        }
        response = client.put(f"/api/categories/{category2.id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.CATEGORY_NAME_EXISTS
        assert response.json()["message"] == ErrorMessages.CATEGORY_NAME_EXISTS

    def test_delete_category(self, client: TestClient, db_session: Session):
        """测试删除分类"""
        # 创建一个分类
        category = Category(
            name="Test Category",
            slug="test-category",
            description="Test Description"
        )
        db_session.add(category)
        db_session.commit()

        response = client.delete(f"/api/categories/{category.id}")
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.SUCCESS
        assert response.json()["message"] == ErrorMessages.CATEGORY_DELETE_SUCCESS

    def test_delete_category_not_found(self, client: TestClient, db_session: Session):
        """测试删除分类 - 分类不存在"""
        response = client.delete("/api/categories/999")
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.CATEGORY_NOT_FOUND
        assert response.json()["message"] == ErrorMessages.CATEGORY_NOT_FOUND

    def test_delete_category_has_articles(self, client: TestClient, db_session: Session):
        """测试删除分类 - 分类下有文章"""
        # 创建一个分类
        category = Category(
            name="Test Category",
            slug="test-category",
            description="Test Description"
        )
        db_session.add(category)
        db_session.commit()

        # 创建一篇关联该分类的文章
        article = Article(
            title="Test Article",
            content="Test Content",
            slug="test-article",
            author_id=1  # 需要一个有效的作者ID
        )
        article.categories = [category]
        db_session.add(article)
        db_session.commit()

        response = client.delete(f"/api/categories/{category.id}")
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.CATEGORY_HAS_ARTICLES
        assert response.json()["message"] == ErrorMessages.CATEGORY_HAS_ARTICLES

    def test_delete_category_has_children(self, client: TestClient, db_session: Session):
        """测试删除分类 - 分类下有子分类"""
        # 创建父分类
        parent = Category(
            name="Parent Category",
            slug="parent-category",
            description="Parent Description"
        )
        db_session.add(parent)
        db_session.commit()

        # 创建子分类
        child = Category(
            name="Child Category",
            slug="child-category",
            description="Child Description",
            parent_id=parent.id
        )
        db_session.add(child)
        db_session.commit()

        response = client.delete(f"/api/categories/{parent.id}")
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.CATEGORY_HAS_ARTICLES  # 使用相同的错误码
        assert response.json()["message"] == "该分类下有子分类，无法删除"  # 这里需要添加新的错误消息

    def test_category_hierarchy(self, client: TestClient, db_session: Session):
        """测试分类层级关系"""
        # 创建一个三层的分类结构
        root = Category(
            name="Root Category",
            slug="root-category",
            description="Root Description"
        )
        db_session.add(root)
        db_session.commit()

        child1 = Category(
            name="Child Category 1",
            slug="child-category-1",
            description="Child Description 1",
            parent_id=root.id
        )
        db_session.add(child1)
        db_session.commit()

        child2 = Category(
            name="Child Category 2",
            slug="child-category-2",
            description="Child Description 2",
            parent_id=root.id
        )
        db_session.add(child2)
        db_session.commit()

        grandchild = Category(
            name="Grandchild Category",
            slug="grandchild-category",
            description="Grandchild Description",
            parent_id=child1.id
        )
        db_session.add(grandchild)
        db_session.commit()

        # 测试获取分类树结构
        response = client.get("/api/categories/tree")
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.SUCCESS
        data = response.json()["data"]

        # 验证根分类
        root_category = next(c for c in data if c["id"] == root.id)
        assert root_category["name"] == "Root Category"
        assert len(root_category["children"]) == 2

        # 验证子分类
        child1_category = next(c for c in root_category["children"] if c["id"] == child1.id)
        assert child1_category["name"] == "Child Category 1"
        assert len(child1_category["children"]) == 1

        child2_category = next(c for c in root_category["children"] if c["id"] == child2.id)
        assert child2_category["name"] == "Child Category 2"
        assert len(child2_category["children"]) == 0

        # 验证孙分类
        grandchild_category = child1_category["children"][0]
        assert grandchild_category["name"] == "Grandchild Category"
        assert len(grandchild_category["children"]) == 0

        # 测试移动分类
        move_data = {"new_parent_id": child2.id}
        response = client.put(f"/api/categories/{grandchild.id}/move", json=move_data)
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.SUCCESS
        assert response.json()["message"] == ErrorMessages.CATEGORY_MOVE_SUCCESS

        # 验证移动后的结构
        response = client.get("/api/categories/tree")
        data = response.json()["data"]
        root_category = next(c for c in data if c["id"] == root.id)
        child2_category = next(c for c in root_category["children"] if c["id"] == child2.id)
        assert len(child2_category["children"]) == 1
        assert child2_category["children"][0]["id"] == grandchild.id

    def test_category_sorting(self, client: TestClient, db_session: Session):
        """测试分类排序"""
        # 创建测试分类
        categories = [
            Category(
                name=f"Sort Test Category {i}",
                slug=f"sort-test-category-{i}",
                description=f"Sort Test Description {i}",
                sort_order=i
            ) for i in range(3)
        ]
        db_session.add_all(categories)
        db_session.commit()

        # 测试按排序顺序降序
        response = client.get("/api/categories?sort=-sort_order")
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.SUCCESS
        data = response.json()["data"]
        assert len(data["items"]) >= 3
        assert data["items"][0]["name"] == "Sort Test Category 2"
        assert data["items"][1]["name"] == "Sort Test Category 1"
        assert data["items"][2]["name"] == "Sort Test Category 0"

        # 测试按排序顺序升序
        response = client.get("/api/categories?sort=sort_order")
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.SUCCESS
        data = response.json()["data"]
        assert len(data["items"]) >= 3
        assert data["items"][0]["name"] == "Sort Test Category 0"
        assert data["items"][1]["name"] == "Sort Test Category 1"
        assert data["items"][2]["name"] == "Sort Test Category 2"

        # 测试按名称排序
        response = client.get("/api/categories?sort=name")
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.SUCCESS
        data = response.json()["data"]
        assert len(data["items"]) >= 3
        assert data["items"][0]["name"] == "Sort Test Category 0"
        assert data["items"][1]["name"] == "Sort Test Category 1"
        assert data["items"][2]["name"] == "Sort Test Category 2"

        # 测试更新排序顺序
        update_data = {"sort_order": 10}
        response = client.put(f"/api/categories/{categories[0].id}/sort", json=update_data)
        assert response.status_code == 200
        assert response.json()["code"] == ErrorCode.SUCCESS
        assert response.json()["message"] == ErrorMessages.CATEGORY_SORT_SUCCESS

        # 验证更新后的排序
        response = client.get("/api/categories?sort=-sort_order")
        data = response.json()["data"]
        assert data["items"][0]["id"] == categories[0].id
        assert data["items"][0]["sort_order"] == 10

        # 清理测试数据
        for category in categories:
            db_session.delete(category)
        db_session.commit()