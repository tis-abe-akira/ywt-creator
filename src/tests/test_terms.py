import pytest
from fastapi import status
from datetime import datetime, timedelta

def test_create_terms(client):
    response = client.post(
        "/terms/",
        json={
            "version": "1.0.0",
            "content": "これはテスト用の利用規約です。",
            "effective_date": (datetime.utcnow() + timedelta(days=30)).isoformat()
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["version"] == "1.0.0"
    assert data["content"] == "これはテスト用の利用規約です。"

def test_get_terms(client):
    # 利用規約を作成
    create_response = client.post(
        "/terms/",
        json={
            "version": "1.0.0",
            "content": "これはテスト用の利用規約です。",
            "effective_date": (datetime.utcnow() + timedelta(days=30)).isoformat()
        }
    )
    terms_id = create_response.json()["id"]

    # 作成した利用規約を取得
    response = client.get(f"/terms/{terms_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == terms_id
    assert data["version"] == "1.0.0"

def test_get_latest_terms(client):
    # 複数バージョンの利用規約を作成
    versions = ["1.0.0", "1.1.0", "1.2.0"]
    for version in versions:
        client.post(
            "/terms/",
            json={
                "version": version,
                "content": f"これはバージョン{version}の利用規約です。",
                "effective_date": (datetime.utcnow() + timedelta(days=30)).isoformat()
            }
        )

    # 最新の利用規約を取得
    response = client.get("/terms/latest")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["version"] == "1.2.0"

def test_record_agreement(client):
    # 利用規約を作成
    terms_response = client.post(
        "/terms/",
        json={
            "version": "1.0.0",
            "content": "これはテスト用の利用規約です。",
            "effective_date": (datetime.utcnow() + timedelta(days=30)).isoformat()
        }
    )
    terms_id = terms_response.json()["id"]

    # 会員の同意を記録
    member_id = "test_member_001"
    response = client.post(f"/terms/{terms_id}/agreements?member_id={member_id}")
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["status"] == "success"

def test_get_member_agreements(client):
    # 利用規約を作成
    terms_response = client.post(
        "/terms/",
        json={
            "version": "1.0.0",
            "content": "これはテスト用の利用規約です。",
            "effective_date": (datetime.utcnow() + timedelta(days=30)).isoformat()
        }
    )
    terms_id = terms_response.json()["id"]

    # 会員の同意を記録
    member_id = "test_member_001"
    client.post(f"/terms/{terms_id}/agreements?member_id={member_id}")

    # 会員の同意履歴を取得
    response = client.get(f"/terms/agreements/{member_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["terms_id"] == terms_id
    assert data[0]["member_id"] == member_id

def test_check_latest_agreement(client):
    # 利用規約を作成
    terms_response = client.post(
        "/terms/",
        json={
            "version": "1.0.0",
            "content": "これはテスト用の利用規約です。",
            "effective_date": (datetime.utcnow() + timedelta(days=30)).isoformat()
        }
    )
    terms_id = terms_response.json()["id"]

    # 会員の同意状態を確認（同意前）
    member_id = "test_member_001"
    response = client.get(f"/terms/check-agreement/{member_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["has_agreed"] is False

    # 同意を記録
    client.post(f"/terms/{terms_id}/agreements?member_id={member_id}")

    # 会員の同意状態を再確認（同意後）
    response = client.get(f"/terms/check-agreement/{member_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["has_agreed"] is True

def test_duplicate_agreement(client):
    # 利用規約を作成
    terms_response = client.post(
        "/terms/",
        json={
            "version": "1.0.0",
            "content": "これはテスト用の利用規約です。",
            "effective_date": (datetime.utcnow() + timedelta(days=30)).isoformat()
        }
    )
    terms_id = terms_response.json()["id"]

    # 会員の同意を記録
    member_id = "test_member_001"
    client.post(f"/terms/{terms_id}/agreements?member_id={member_id}")

    # 同じ会員が同じ利用規約に再度同意を試みる
    response = client.post(f"/terms/{terms_id}/agreements?member_id={member_id}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_get_nonexistent_terms(client):
    response = client.get("/terms/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
