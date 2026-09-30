def register(
    client,
    email="test@example.com",
):
    return client.post(
        "/api/auth/register",
        json={
            "email": email,
            "full_name": "Test User",
            "password": "password123",
        },
    )


def test_health(client):

    response = client.get(
        "/api/health"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"


def test_register_login_session(client):

    response = register(client)

    assert response.status_code == 200

    response = client.get(
        "/api/auth/session-info"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == (
        "test@example.com"
    )


def test_home_requires_auth(client):

    response = client.post(
        "/api/planners/home",
        json={
            "budget": 50000,
            "rooms": [
                "Living Room"
            ],
        },
    )

    assert response.status_code == 401


def test_home_fallback_and_history(client):

    response = register(client)

    assert response.status_code == 200

    response = client.post(
        "/api/planners/home",
        json={
            "budget": 50000,
            "rooms": [
                "Living Room",
                "Bedroom",
            ],
            "style": "modern",
            "priorities": [
                "lighting"
            ],
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["planner_type"] == "home"

    assert (
        body["estimated_total"]
        <= 50000
    )

    assert body["source"] == (
        "demo-fallback"
    )

    history = client.get(
        "/api/history"
    )

    assert history.status_code == 200

    assert len(
        history.json()
    ) == 1


def test_jewelry_without_image(client):

    response = register(client)

    assert response.status_code == 200

    response = client.post(
        "/api/planners/jewelry",
        data={
            "budget": "20000",
            "occasion": "Wedding",
            "style": "elegant",
            "metal": "Gold",
            "outfit_color": "Red",
            "notes": "",
        },
        files={
            "outfit_image": (
                "",
                b"",
                "application/octet-stream",
            )
        },
    )

    assert response.status_code == 200

    assert response.json()[
        "planner_type"
    ] == "jewelry"


def test_duplicate_register(client):

    first = register(client)

    assert first.status_code == 200

    second = register(client)

    assert second.status_code == 409