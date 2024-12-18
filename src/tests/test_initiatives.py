import pytest
from fastapi import status
from datetime import datetime

def test_create_initiative(client):
    response = client.post(
        "/initiatives/",
        json={
            "title": "テスト施策",
            "description": "これはテスト用の改善施策です",
            "irr": 7.5,
            "cost": 500000
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "テスト施策"
    assert data["status"] == "PROPOSED"

def test_get_initiative(client):
    # 施策を作成
    create_response = client.post(
        "/initiatives/",
        json={
            "title": "テスト施策",
            "description": "これはテスト用の改善施策です",
            "irr": 7.5,
            "cost": 500000
        }
    )
    initiative_id = create_response.json()["id"]

    # 作成した施策を取得
    response = client.get(f"/initiatives/{initiative_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == initiative_id
    assert data["title"] == "テスト施策"

def test_list_initiatives(client):
    # 複数の施策を作成
    initiatives = [
        {
            "title": f"テスト施策{i}",
            "description": f"これはテスト用の改善施策{i}です",
            "irr": 7.5 + i,
            "cost": 500000 + (i * 100000)
        }
        for i in range(3)
    ]
    
    for initiative in initiatives:
        client.post("/initiatives/", json=initiative)
    
    # 施策一覧を取得
    response = client.get("/initiatives/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3

def test_create_initiative_assessment(client):
    # 施策を作成
    initiative_response = client.post(
        "/initiatives/",
        json={
            "title": "テスト施策",
            "description": "これはテスト用の改善施策です",
            "irr": 7.5,
            "cost": 500000
        }
    )
    initiative_id = initiative_response.json()["id"]

    # 施策の評価を作成
    assessment_response = client.post(
        f"/initiatives/{initiative_id}/assessments",
        json={
            "initiative_id": initiative_id,
            "feasibility_score": 85.5,
            "compliance_check": True,
            "terms_impact": False
        }
    )
    assert assessment_response.status_code == status.HTTP_200_OK
    data = assessment_response.json()
    assert data["initiative_id"] == initiative_id
    assert data["feasibility_score"] == 85.5

def test_record_initiative_effect(client):
    # 施策を作成
    initiative_response = client.post(
        "/initiatives/",
        json={
            "title": "テスト施策",
            "description": "これはテスト用の改善施策です",
            "irr": 7.5,
            "cost": 500000
        }
    )
    initiative_id = initiative_response.json()["id"]

    # 効果を記録
    effect_response = client.post(
        f"/initiatives/{initiative_id}/effects",
        json={
            "initiative_id": initiative_id,
            "metric_name": "コスト削減率",
            "metric_value": 15.5
        }
    )
    assert effect_response.status_code == status.HTTP_200_OK
    data = effect_response.json()
    assert data["initiative_id"] == initiative_id
    assert data["metric_name"] == "コスト削減率"
    assert data["metric_value"] == 15.5

def test_update_initiative_status(client):
    # 施策を作成
    initiative_response = client.post(
        "/initiatives/",
        json={
            "title": "テスト施策",
            "description": "これはテスト用の改善施策です",
            "irr": 7.5,
            "cost": 500000
        }
    )
    initiative_id = initiative_response.json()["id"]

    # ステータスを更新
    status_response = client.put(
        f"/initiatives/{initiative_id}/status",
        json={"status": "APPROVED"}
    )
    assert status_response.status_code == status.HTTP_200_OK
    data = status_response.json()
    assert data["status"] == "APPROVED"

def test_get_nonexistent_initiative(client):
    response = client.get("/initiatives/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_create_initiative_invalid_irr(client):
    response = client.post(
        "/initiatives/",
        json={
            "title": "テスト施策",
            "description": "これはテスト用の改善施策です",
            "irr": -1.0,  # 負のIRRは無効
            "cost": 500000
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_create_initiative_invalid_cost(client):
    response = client.post(
        "/initiatives/",
        json={
            "title": "テスト施策",
            "description": "これはテスト用の改善施策です",
            "irr": 7.5,
            "cost": -100000  # 負のコストは無効
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
