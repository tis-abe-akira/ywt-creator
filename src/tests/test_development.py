import pytest
from fastapi import status

def create_test_initiative(client):
    response = client.post(
        "/initiatives/",
        json={
            "title": "テスト施策",
            "description": "これはテスト用の改善施策です",
            "irr": 7.5,
            "cost": 500000
        }
    )
    return response.json()["id"]

def test_create_requirement(client):
    initiative_id = create_test_initiative(client)
    
    response = client.post(
        "/development/requirements/",
        json={
            "initiative_id": initiative_id,
            "title": "テスト要件",
            "description": "これはテスト用の要件定義です",
            "status": "DRAFT"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "テスト要件"
    assert data["status"] == "DRAFT"

def test_get_requirement(client):
    initiative_id = create_test_initiative(client)
    
    # 要件を作成
    create_response = client.post(
        "/development/requirements/",
        json={
            "initiative_id": initiative_id,
            "title": "テスト要件",
            "description": "これはテスト用の要件定義です",
            "status": "DRAFT"
        }
    )
    requirement_id = create_response.json()["id"]

    # 作成した要件を取得
    response = client.get(f"/development/requirements/{requirement_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == requirement_id
    assert data["title"] == "テスト要件"

def test_update_requirement_status(client):
    initiative_id = create_test_initiative(client)
    
    # 要件を作成
    create_response = client.post(
        "/development/requirements/",
        json={
            "initiative_id": initiative_id,
            "title": "テスト要件",
            "description": "これはテスト用の要件定義です",
            "status": "DRAFT"
        }
    )
    requirement_id = create_response.json()["id"]

    # ステータスを更新
    response = client.put(
        f"/development/requirements/{requirement_id}/status",
        json={"status": "APPROVED"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "APPROVED"

def test_create_development_task(client):
    initiative_id = create_test_initiative(client)
    
    # 要件を作成
    requirement_response = client.post(
        "/development/requirements/",
        json={
            "initiative_id": initiative_id,
            "title": "テスト要件",
            "description": "これはテスト用の要件定義です",
            "status": "DRAFT"
        }
    )
    requirement_id = requirement_response.json()["id"]

    # タスクを作成
    response = client.post(
        "/development/tasks/",
        json={
            "requirement_id": requirement_id,
            "title": "テストタスク",
            "description": "これはテスト用の開発タスクです",
            "status": "TODO"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "テストタスク"
    assert data["status"] == "TODO"

def test_update_development_task(client):
    initiative_id = create_test_initiative(client)
    
    # 要件を作成
    requirement_response = client.post(
        "/development/requirements/",
        json={
            "initiative_id": initiative_id,
            "title": "テスト要件",
            "description": "これはテスト用の要件定義です",
            "status": "DRAFT"
        }
    )
    requirement_id = requirement_response.json()["id"]

    # タスクを作成
    task_response = client.post(
        "/development/tasks/",
        json={
            "requirement_id": requirement_id,
            "title": "テストタスク",
            "description": "これはテスト用の開発タスクです",
            "status": "TODO"
        }
    )
    task_id = task_response.json()["id"]

    # タスクを更新
    response = client.put(
        f"/development/tasks/{task_id}",
        json={
            "requirement_id": requirement_id,
            "title": "更新されたテストタスク",
            "description": "これは更新された開発タスクです",
            "status": "IN_PROGRESS"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "更新されたテストタスク"
    assert data["status"] == "IN_PROGRESS"

def test_get_tasks_by_requirement(client):
    initiative_id = create_test_initiative(client)
    
    # 要件を作成
    requirement_response = client.post(
        "/development/requirements/",
        json={
            "initiative_id": initiative_id,
            "title": "テスト要件",
            "description": "これはテスト用の要件定義です",
            "status": "DRAFT"
        }
    )
    requirement_id = requirement_response.json()["id"]

    # 複数のタスクを作成
    for i in range(3):
        client.post(
            "/development/tasks/",
            json={
                "requirement_id": requirement_id,
                "title": f"テストタスク{i+1}",
                "description": f"これはテスト用の開発タスク{i+1}です",
                "status": "TODO"
            }
        )

    # 要件に紐づくタスク一覧を取得
    response = client.get(f"/development/requirements/{requirement_id}/tasks")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3

def test_get_nonexistent_requirement(client):
    response = client.get("/development/requirements/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_get_nonexistent_task(client):
    response = client.get("/development/tasks/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_create_task_for_nonexistent_requirement(client):
    response = client.post(
        "/development/tasks/",
        json={
            "requirement_id": 999,
            "title": "テストタスク",
            "description": "これはテスト用の開発タスクです",
            "status": "TODO"
        }
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
