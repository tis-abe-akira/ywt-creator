import pytest
from fastapi import status
from datetime import datetime, timedelta

def test_create_release(client):
    response = client.post(
        "/releases/",
        json={
            "version": "1.0.0",
            "description": "これはテスト用のリリースです",
            "status": "PLANNED",
            "planned_date": (datetime.utcnow() + timedelta(days=7)).isoformat()
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["version"] == "1.0.0"
    assert data["status"] == "PLANNED"

def test_get_release(client):
    # リリースを作成
    create_response = client.post(
        "/releases/",
        json={
            "version": "1.0.0",
            "description": "これはテスト用のリリースです",
            "status": "PLANNED",
            "planned_date": (datetime.utcnow() + timedelta(days=7)).isoformat()
        }
    )
    release_id = create_response.json()["id"]

    # 作成したリリースを取得
    response = client.get(f"/releases/{release_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == release_id
    assert data["version"] == "1.0.0"

def test_list_releases(client):
    # 複数のリリースを作成
    versions = ["1.0.0", "1.1.0", "1.2.0"]
    for version in versions:
        client.post(
            "/releases/",
            json={
                "version": version,
                "description": f"これはバージョン{version}のリリースです",
                "status": "PLANNED",
                "planned_date": (datetime.utcnow() + timedelta(days=7)).isoformat()
            }
        )

    # リリース一覧を取得
    response = client.get("/releases/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3

def test_update_release_status(client):
    # リリースを作成
    create_response = client.post(
        "/releases/",
        json={
            "version": "1.0.0",
            "description": "これはテスト用のリリースです",
            "status": "PLANNED",
            "planned_date": (datetime.utcnow() + timedelta(days=7)).isoformat()
        }
    )
    release_id = create_response.json()["id"]

    # ステータスを更新
    response = client.put(
        f"/releases/{release_id}/status",
        json={"status": "COMPLETED"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert data["actual_date"] is not None

def test_create_rollback(client):
    # リリースを作成して完了状態にする
    create_response = client.post(
        "/releases/",
        json={
            "version": "1.0.0",
            "description": "これはテスト用のリリースです",
            "status": "PLANNED",
            "planned_date": (datetime.utcnow() + timedelta(days=7)).isoformat()
        }
    )
    release_id = create_response.json()["id"]
    
    # リリースを完了状態に更新
    client.put(
        f"/releases/{release_id}/status",
        json={"status": "COMPLETED"}
    )

    # ロールバックを作成
    response = client.post(
        f"/releases/{release_id}/rollback",
        json={
            "release_id": release_id,
            "reason": "テスト用のロールバック"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["release_id"] == release_id
    assert data["reason"] == "テスト用のロールバック"

def test_get_release_rollbacks(client):
    # リリースを作成して完了状態にする
    create_response = client.post(
        "/releases/",
        json={
            "version": "1.0.0",
            "description": "これはテスト用のリリースです",
            "status": "PLANNED",
            "planned_date": (datetime.utcnow() + timedelta(days=7)).isoformat()
        }
    )
    release_id = create_response.json()["id"]
    
    # リリースを完了状態に更新
    client.put(
        f"/releases/{release_id}/status",
        json={"status": "COMPLETED"}
    )

    # ロールバックを作成
    client.post(
        f"/releases/{release_id}/rollback",
        json={
            "release_id": release_id,
            "reason": "テスト用のロールバック"
        }
    )

    # ロールバック履歴を取得
    response = client.get(f"/releases/{release_id}/rollbacks")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["release_id"] == release_id

def test_get_pending_releases(client):
    # 異なるステータスのリリースを作成
    statuses = ["PLANNED", "PENDING_APPROVAL", "PENDING_APPROVAL", "COMPLETED"]
    for i, status_value in enumerate(statuses):
        client.post(
            "/releases/",
            json={
                "version": f"1.{i}.0",
                "description": f"これはバージョン1.{i}.0のリリースです",
                "status": status_value,
                "planned_date": (datetime.utcnow() + timedelta(days=7)).isoformat()
            }
        )

    # 承認待ちのリリース一覧を取得
    response = client.get("/releases/pending/approval")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2  # pending_approvalのリリースが2つあるはず

def test_approve_release(client):
    # リリースを作成
    create_response = client.post(
        "/releases/",
        json={
            "version": "1.0.0",
            "description": "これはテスト用のリリースです",
            "status": "PENDING_APPROVAL",
            "planned_date": (datetime.utcnow() + timedelta(days=7)).isoformat()
        }
    )
    release_id = create_response.json()["id"]

    # リリースを承認
    response = client.put(f"/releases/{release_id}/approve")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "APPROVED"

def test_get_nonexistent_release(client):
    response = client.get("/releases/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_rollback_non_completed_release(client):
    # リリースを作成（完了状態ではない）
    create_response = client.post(
        "/releases/",
        json={
            "version": "1.0.0",
            "description": "これはテスト用のリリースです",
            "status": "PLANNED",
            "planned_date": (datetime.utcnow() + timedelta(days=7)).isoformat()
        }
    )
    release_id = create_response.json()["id"]

    # ロールバックを試みる
    response = client.post(
        f"/releases/{release_id}/rollback",
        json={
            "release_id": release_id,
            "reason": "テスト用のロールバック"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
